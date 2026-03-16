import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt

def run_xfoil(airfoil_file, reynolds, alpha_start, alpha_end, alpha_step, output_file):
    """Run XFOIL simulation and return results as a DataFrame"""
    
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
        f"100\n"
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
        timeout=60
    )
    
    # Parse results file
    if not os.path.exists(output_file):
        print(f"Warning: No results for {airfoil_file}")
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
        return None
    
    df = pd.DataFrame(data, columns=['alpha', 'CL', 'CD', 'CDp', 'CM', 'Top_Xtr', 'Bot_Xtr'])
    df['CL_CD'] = df['CL'] / df['CD']  # lift-to-drag ratio
    return df

# Run simulation for NACA 2412
df = run_xfoil(
    airfoil_file='data/naca2412.dat',
    reynolds=200000,
    alpha_start=-5,
    alpha_end=15,
    alpha_step=1,
    output_file='results_naca2412.txt'
)

if df is not None:
    print(df.to_string(index=False))
    
    # Plot lift curve and drag polar
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].plot(df['alpha'], df['CL'], 'b-o', markersize=4)
    axes[0].set_title('Lift Curve')
    axes[0].set_xlabel('Angle of Attack (deg)')
    axes[0].set_ylabel('CL')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(df['CD'], df['CL'], 'r-o', markersize=4)
    axes[1].set_title('Drag Polar')
    axes[1].set_xlabel('CD')
    axes[1].set_ylabel('CL')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(df['alpha'], df['CL_CD'], 'g-o', markersize=4)
    axes[2].set_title('Lift-to-Drag Ratio')
    axes[2].set_xlabel('Angle of Attack (deg)')
    axes[2].set_ylabel('CL/CD')
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle('NACA 2412 Aerodynamic Performance (Re=200,000)', fontweight='bold')
    plt.tight_layout()
    plt.savefig('naca2412_performance.png', dpi=150)
    plt.show()
    
    print(f"\nMax CL: {df['CL'].max():.3f} at alpha={df.loc[df['CL'].idxmax(), 'alpha']}°")
    print(f"Max CL/CD: {df['CL_CD'].max():.1f} at alpha={df.loc[df['CL_CD'].idxmax(), 'alpha']}°")
    print(f"Min CD: {df['CD'].min():.5f}")