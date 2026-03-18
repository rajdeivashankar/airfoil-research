import numpy as np
import pandas as pd
import os
import glob

def load_airfoil(filepath):
    """Load airfoil coordinates from a UIUC .dat file"""
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
                if x > 1.5 or abs(y) > 1.5:
                    continue
                coords.append([x, y])
            except ValueError:
                continue
    return np.array(coords)

def extract_geometry(coords):
    """
    Extract geometric parameters from airfoil coordinates.
    Returns camber, thickness, and other shape descriptors.
    """
    if len(coords) < 10:
        return None

    # Separate upper and lower surfaces
    # Find leading edge (minimum x)
    le_idx = np.argmin(coords[:, 0])
    
    upper = coords[:le_idx+1][::-1]  # leading to trailing
    lower = coords[le_idx:]           # leading to trailing

    if len(upper) < 5 or len(lower) < 5:
        return None

    # Interpolate onto common x grid
    x_grid = np.linspace(0.01, 0.99, 100)

    try:
        y_upper = np.interp(x_grid, upper[:, 0], upper[:, 1])
        y_lower = np.interp(x_grid, lower[:, 0], lower[:, 1])
    except:
        return None

    # Camber line and thickness distribution
    camber_line = (y_upper + y_lower) / 2
    thickness = y_upper - y_lower

    # Key geometric parameters
    max_camber = np.max(np.abs(camber_line))
    max_camber_loc = x_grid[np.argmax(np.abs(camber_line))]
    max_thickness = np.max(thickness)
    max_thickness_loc = x_grid[np.argmax(thickness)]

    # Leading edge thickness (at x=0.1)
    le_thickness = np.interp(0.1, x_grid, thickness)

    # Trailing edge thickness (at x=0.9)
    te_thickness = np.interp(0.9, x_grid, thickness)

    # Camber at quarter chord
    camber_at_25 = np.interp(0.25, x_grid, camber_line)

    # Area under camber line (measure of overall camber)
    camber_area = np.trapezoid(np.abs(camber_line), x_grid)

    return {
        'max_camber': round(max_camber, 5),
        'max_camber_loc': round(max_camber_loc, 3),
        'max_thickness': round(max_thickness, 5),
        'max_thickness_loc': round(max_thickness_loc, 3),
        'le_thickness': round(le_thickness, 5),
        'te_thickness': round(te_thickness, 5),
        'camber_at_25': round(camber_at_25, 5),
        'camber_area': round(camber_area, 5),
    }

# Load metrics to know which airfoils we have results for
metrics_df = pd.read_csv('results/airfoil_metrics.csv')
airfoil_names = metrics_df['airfoil'].tolist()

geometry_data = []
failed = []

print(f"Extracting geometry for {len(airfoil_names)} airfoils...\n")

for name in airfoil_names:
    # Find the coordinate file
    filepath = f'data/{name}.dat'
    converted = f'data/{name}_converted.dat'
    
    if os.path.exists(converted):
        filepath = converted
    elif not os.path.exists(filepath):
        print(f"  File not found: {name}")
        failed.append(name)
        continue
    
    coords = load_airfoil(filepath)
    geom = extract_geometry(coords)
    
    if geom:
        geom['airfoil'] = name
        geometry_data.append(geom)
        print(f"  {name}: camber={geom['max_camber']:.4f}, "
              f"thickness={geom['max_thickness']:.4f}, "
              f"camber_loc={geom['max_camber_loc']:.3f}")
    else:
        print(f"  Failed to extract geometry: {name}")
        failed.append(name)

# Merge with performance metrics
geom_df = pd.DataFrame(geometry_data)
merged_df = pd.merge(metrics_df, geom_df, on='airfoil')

# Save
merged_df.to_csv('results/geometry_performance.csv', index=False)

print(f"\nSuccessfully extracted: {len(geometry_data)}/{len(airfoil_names)}")
print(f"Failed: {len(failed)}")
print(f"\nSaved to results/geometry_performance.csv")
print(f"\nPreview:")
print(merged_df[['airfoil', 'max_camber', 'max_thickness', 
                  'max_camber_loc', 'max_CL_CD', 'max_CL']].head(10).to_string(index=False))