import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
import glob

def convert_lednicer_to_selig(filepath):
    """Convert Lednicer format .dat file to Selig format XFOIL can read"""
    upper = []
    lower = []
    current = None
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 2:
            try:
                x = float(parts[0])
                y = float(parts[1])
                if x > 1.5:
                    current = 'upper'
                    continue
                if current == 'upper':
                    upper.append((x, y))
                    if x == 1.0 and len(upper) > 1:
                        current = 'lower'
                elif current == 'lower':
                    lower.append((x, y))
            except ValueError:
                continue
    
    coords = list(reversed(upper)) + lower[1:]
    out_path = filepath.replace('.dat', '_converted.dat')
    with open(out_path, 'w') as f:
        f.write('AIRFOIL\n')
        for x, y in coords:
            f.write(f'  {x:.7f}  {y:.7f}\n')
    return out_path

def detect_format(filepath):
    """Detect if file is Lednicer format and convert if needed"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 2:
            try:
                x = float(parts[0])
                y = float(parts[1])
                if x > 1.5:
                    return convert_lednicer_to_selig(filepath)
            except ValueError:
                continue
    return filepath

def run_xfoil(airfoil_name, airfoil_file, reynolds, alpha_start, alpha_end, alpha_step):
    """Run XFOIL simulation and return results as a DataFrame"""
    
    output_file = f'results_{airfoil_name}.txt'
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    commands = (
        f"LOAD {airfoil_file}\n"
        f"PANE\n"
        f"OPER\n"
        f"VISC\n"
        f"{reynolds}\n"
        f"ITER\n"
        f"200\n"
        f"PACC\n"
        f"{output_file}\n"
        f"\n"
        f"ASEQ {alpha_start} {alpha_end} {alpha_step}\n"
        f"PACC\n"
        f"\n"
        f"QUIT\n"
    )
    
    try:
        subprocess.run(
            ['xfoil.exe'],
            input=commands,
            capture_output=True,
            text=True,
            timeout=60  # reduced from 180 — if it takes longer than 60s, skip it
        )
    except subprocess.TimeoutExpired:
        print(f"  Timeout — skipping {airfoil_name}")
        return None
    
    if not os.path.exists(output_file):
        print(f"  Warning: No results for {airfoil_name}")
        return None
    
    data = []
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        parts = line.split()
        if len(parts) == 7:
            try:
                row = [float(p) for p in parts]
                data.append(row)
            except ValueError:
                continue
    
    if not data:
        print(f"  Warning: Empty results for {airfoil_name}")
        return None
    
    df = pd.DataFrame(data, columns=['alpha', 'CL', 'CD', 'CDp', 'CM', 'Top_Xtr', 'Bot_Xtr'])
    df['CL_CD'] = df['CL'] / df['CD']
    df['airfoil'] = airfoil_name
    df['reynolds'] = reynolds
    return df

def extract_metrics(df, airfoil_name):
    """Extract key performance metrics from a polar"""
    if df is None or len(df) < 3:
        return None
    
    max_cl_idx = df['CL'].idxmax()
    
    metrics = {
        'airfoil': airfoil_name,
        'max_CL': df['CL'].max(),
        'stall_angle': df.loc[max_cl_idx, 'alpha'],
        'min_CD': df['CD'].min(),
        'max_CL_CD': df['CL_CD'].max(),
        'best_alpha': df.loc[df['CL_CD'].idxmax(), 'alpha'],
        'CL_at_0': df.loc[df['alpha'].abs().idxmin(), 'CL'] if 0 in df['alpha'].values else None,
    }
    return metrics

def clean_results(df):
    """Remove physically unrealistic data points"""
    if df is None:
        return None
    
    # Remove points where CD is unrealistically small
    df = df[df['CD'] > 0.008]
    
    # Remove points where CL/CD is unrealistically high
    df = df[df['CL_CD'].abs() < 150]

    # Remove statistical outliers in CD
    median_cd = df['CD'].median()
    df = df[df['CD'] > median_cd * 0.3]
    
    # Remove duplicate alpha values
    df = df.drop_duplicates(subset='alpha', keep='last')
    
    # Must have data covering alpha=0 to alpha=5 for UAV relevance
    has_low_alpha = df['alpha'].min() <= 1.0
    has_mid_alpha = df['alpha'].max() >= 5.0
    if not (has_low_alpha and has_mid_alpha):
        return None
    
    # Must have at least 5 valid points
    if len(df) < 5:
        return None
    
    return df.reset_index(drop=True)

# Auto-detect all airfoil files in data folder
dat_files = glob.glob('data/*.dat')
dat_files = [f for f in dat_files if 'converted' not in f]

reynolds = 200000
all_results = []
all_metrics = []

print(f"Found {len(dat_files)} airfoil files")
print(f"Reynolds number: {reynolds:,}\n")

for filepath in sorted(dat_files):
    name = os.path.basename(filepath).replace('.dat', '')
    print(f"Simulating {name}...")
    
    actual_filepath = detect_format(filepath)
    
    # Skip known problematic airfoils
    if name in ['mh114', 'ag14', 'ag13']:
        print(f"  Skipping {name} (known convergence issues)")
        continue

    df = run_xfoil(
        airfoil_name=name,
        airfoil_file=actual_filepath,
        reynolds=reynolds,
        alpha_start=-5,
        alpha_end=15,
        alpha_step=1
    )

    if df is not None:
        df = clean_results(df)

    if df is not None:
        all_results.append(df)
        metrics = extract_metrics(df, name)
        if metrics:
            all_metrics.append(metrics)
        print(f"  Done — {len(df)} points, max CL/CD = {df['CL_CD'].max():.1f}")
    
    time.sleep(0.3)

if all_results:
    combined_df = pd.concat(all_results, ignore_index=True)
    metrics_df = pd.DataFrame(all_metrics)
    
    os.makedirs('results', exist_ok=True)
    combined_df.to_csv('results/simulation_results.csv', index=False)
    metrics_df.to_csv('results/airfoil_metrics.csv', index=False)
    
    print(f"\nAll simulations complete!")
    print(f"Successful: {len(all_metrics)}/{len(dat_files)} airfoils")
    print(f"Total data points: {len(combined_df)}")
    print(f"\nTop 10 by CL/CD:")
    print(metrics_df.sort_values('max_CL_CD', ascending=False).head(10).to_string(index=False))
else:
    print("No results generated")