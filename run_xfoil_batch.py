import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import time

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
                # Point count line like "61.0  61.0"
                if x > 1.5:
                    current = 'upper'
                    continue
                if current == 'upper':
                    upper.append((x, y))
                    # Switch to lower after first surface ends at x=1
                    if x == 1.0 and len(upper) > 1:
                        current = 'lower'
                elif current == 'lower':
                    lower.append((x, y))
            except ValueError:
                continue
    
    # Selig format: upper surface leading edge to trailing edge reversed
    # then lower surface trailing edge to leading edge
    coords = list(reversed(upper)) + lower[1:]  # skip duplicate leading edge
    
    # Write converted file
    out_path = filepath.replace('.dat', '_converted.dat')
    with open(out_path, 'w') as f:
        f.write('CLARK Y AIRFOIL\n')
        for x, y in coords:
            f.write(f'  {x:.7f}  {y:.7f}\n')
    
    return out_path
# Then change the Clark Y entry in your airfoils dictionary to convert it on the fly:
pythonairfoils = {
    'naca2412': 'data/naca2412.dat',
    'naca4412': 'data/naca4412.dat',
    'clarky':   convert_lednicer_to_selig('data/clarky.dat'),
    'e387':     'data/e387.dat',
    's1223':    'data/s1223.dat',
}

def run_xfoil(airfoil_name, airfoil_file, reynolds, alpha_start, alpha_end, alpha_step):
    """Run XFOIL simulation and return results as a DataFrame"""
    
    output_file = f'results_{airfoil_name}.txt'
    
    # Delete old results file if it exists
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
    
    subprocess.run(
        ['xfoil.exe'],
        input=commands,
        capture_output=True,
        text=True,
        timeout=180
    )
    
    # Parse results file
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
    
    # Find stall angle (where CL starts dropping)
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

# Define airfoils to simulate
airfoils = {
    'naca2412': ('data/naca2412.dat', -5, 15),
    'naca4412': ('data/naca4412.dat', -5, 15),
    'clarky':   (convert_lednicer_to_selig('data/clarky.dat'), -5, 15),
    'e387':     ('data/e387.dat', 0, 12),
    's1223':    ('data/s1223.dat', 0, 12),
}

reynolds = 200000
all_results = []
all_metrics = []

print("Running batch XFOIL simulations...")
print(f"Airfoils: {len(airfoils)} | Reynolds: {reynolds:,}\n")

for name, (filepath, alpha_start, alpha_end) in airfoils.items():
    print(f"Simulating {name}...")
    
    df = run_xfoil(
        airfoil_name=name,
        airfoil_file=filepath,
        reynolds=reynolds,
        alpha_start=alpha_start,
        alpha_end=alpha_end,
        alpha_step=1
    )
    
    if df is not None:
        all_results.append(df)
        metrics = extract_metrics(df, name)
        if metrics:
            all_metrics.append(metrics)
        print(f"  Done — {len(df)} points, max CL/CD = {df['CL_CD'].max():.1f}")
    
    time.sleep(0.5)  # small pause between runs

# Combine all results
combined_df = pd.concat(all_results, ignore_index=True)
metrics_df = pd.DataFrame(all_metrics)

# Save to CSV
os.makedirs('results', exist_ok=True)
combined_df.to_csv('results/simulation_results.csv', index=False)
metrics_df.to_csv('results/airfoil_metrics.csv', index=False)

print(f"\nAll simulations complete!")
print(f"Total data points: {len(combined_df)}")
print(f"\nPerformance Summary:")
print(metrics_df.to_string(index=False))

# Plot lift curves for all airfoils
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
colors = ['blue', 'red', 'green', 'orange', 'purple']

for (name, group), color in zip(combined_df.groupby('airfoil'), colors):
    axes[0].plot(group['alpha'], group['CL'], '-o', color=color, markersize=3, label=name)
    axes[1].plot(group['CD'], group['CL'], '-o', color=color, markersize=3, label=name)
    axes[2].plot(group['alpha'], group['CL_CD'], '-o', color=color, markersize=3, label=name)

axes[0].set_title('Lift Curves')
axes[0].set_xlabel('Angle of Attack (deg)')
axes[0].set_ylabel('CL')
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)

axes[1].set_title('Drag Polars')
axes[1].set_xlabel('CD')
axes[1].set_ylabel('CL')
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

axes[2].set_title('Lift-to-Drag Ratios')
axes[2].set_xlabel('Angle of Attack (deg)')
axes[2].set_ylabel('CL/CD')
axes[2].legend(fontsize=8)
axes[2].grid(True, alpha=0.3)

plt.suptitle(f'Airfoil Performance Comparison (Re={reynolds:,})', fontweight='bold')
plt.tight_layout()
plt.savefig('results/comparison_plots.png', dpi=150)
plt.show()