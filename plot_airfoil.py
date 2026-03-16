import numpy as np
import matplotlib.pyplot as plt
import os

def load_airfoil(filepath):
    """Load airfoil coordinates from a UIUC .dat file (handles both formats)"""
    coords = []
    
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
                # Skip point-count lines like "61.0  61.0"
                if x > 1.5 or y > 1.5:
                    continue
                coords.append([x, y])
            except ValueError:
                continue
    
    return np.array(coords)

# List of airfoils to plot
airfoils = {
    'NACA 2412': 'data/naca2412.dat',
    'NACA 4412': 'data/naca4412.dat',
    'Clark Y':   'data/clarky.dat',
    'E387':      'data/e387.dat',
    'S1223':     'data/s1223.dat',
}

#  Plot all airfoils on one figure
fig, axes = plt.subplots(len(airfoils), 1, figsize=(12, 14))
colors = ['blue', 'red', 'green', 'orange', 'purple']

for ax, (name, filepath), color in zip(axes, airfoils.items(), colors):
    coords = load_airfoil(filepath)
    x = coords[:, 0]
    y = coords[:, 1]
    
    ax.plot(x, y, '-o', color=color, markersize=3)
    ax.fill(x, y, alpha=0.2, color=color)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_title(f'{name}')
    ax.set_xlabel('x/c')
    ax.set_ylabel('y/c')
    ax.axis('equal')
    ax.grid(True, alpha=0.3)

plt.suptitle('Airfoil Geometry Comparison', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('airfoil_shapes.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"Successfully loaded and plotted {len(airfoils)} airfoils")