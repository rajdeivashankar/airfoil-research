import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

df = pd.read_csv('results/geometry_performance.csv')
os.makedirs('results/figures', exist_ok=True)

print(f"Dataset: {len(df)} airfoils\n")

# ── 1. Correlation matrix ──────────────────────────────────────────────────
geom_params = ['max_camber', 'max_camber_loc', 'max_thickness',
               'max_thickness_loc', 'le_thickness', 'camber_at_25', 'camber_area']
perf_params = ['max_CL_CD', 'max_CL', 'min_CD', 'stall_angle']

corr_data = df[geom_params + perf_params].corr()
geom_perf_corr = corr_data.loc[geom_params, perf_params]

print("Correlation Matrix (Geometry vs Performance):")
print(geom_perf_corr.round(3).to_string())

# Plot correlation heatmap
fig, ax = plt.subplots(figsize=(10, 7))
im = ax.imshow(geom_perf_corr.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
plt.colorbar(im, label='Pearson Correlation')
ax.set_xticks(range(len(perf_params)))
ax.set_yticks(range(len(geom_params)))
ax.set_xticklabels(perf_params, fontsize=11)
ax.set_yticklabels(geom_params, fontsize=11)
for i in range(len(geom_params)):
    for j in range(len(perf_params)):
        ax.text(j, i, f'{geom_perf_corr.values[i,j]:.2f}',
                ha='center', va='center', fontsize=10,
                color='white' if abs(geom_perf_corr.values[i,j]) > 0.5 else 'black')
ax.set_title('Geometry-Performance Correlation Matrix', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('results/figures/correlation_heatmap.png', dpi=150)
plt.close()
print("\nSaved: correlation_heatmap.png")

# ── 2. Camber vs CL/CD scatter ─────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

def scatter_with_regression(ax, x, y, xlabel, ylabel, title):
    ax.scatter(x, y, alpha=0.7, edgecolors='gray', linewidth=0.5, s=50)
    # Regression line
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() > 3:
        slope, intercept, r, p, _ = stats.linregress(x[mask], y[mask])
        x_line = np.linspace(x[mask].min(), x[mask].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, 'r-', linewidth=2,
                label=f'R²={r**2:.3f}, p={p:.3f}')
        ax.legend(fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight='bold')
    ax.grid(True, alpha=0.3)

scatter_with_regression(
    axes[0,0], df['max_camber'], df['max_CL_CD'],
    'Max Camber (fraction of chord)', 'Max CL/CD',
    'Camber vs Aerodynamic Efficiency')

scatter_with_regression(
    axes[0,1], df['max_thickness'], df['max_CL_CD'],
    'Max Thickness (fraction of chord)', 'Max CL/CD',
    'Thickness vs Aerodynamic Efficiency')

scatter_with_regression(
    axes[1,0], df['max_camber_loc'], df['max_CL_CD'],
    'Camber Location (fraction of chord)', 'Max CL/CD',
    'Camber Location vs Aerodynamic Efficiency')

scatter_with_regression(
    axes[1,1], df['max_camber'], df['max_CL'],
    'Max Camber (fraction of chord)', 'Max CL',
    'Camber vs Maximum Lift')

plt.suptitle('Geometric Predictors of Airfoil Performance (Re=200,000)',
             fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('results/figures/geometry_correlations.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: geometry_correlations.png")

# ── 3. Camber range analysis ───────────────────────────────────────────────
# Bin airfoils by camber level
df['camber_bin'] = pd.cut(df['max_camber'],
                           bins=[0, 0.02, 0.04, 0.06, 0.08, 0.12],
                           labels=['0-2%', '2-4%', '4-6%', '6-8%', '8-12%'])

camber_groups = df.groupby('camber_bin', observed=True)['max_CL_CD'].agg(['mean', 'std', 'count'])
print("\nCL/CD by Camber Range:")
print(camber_groups.round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(camber_groups.index.astype(str), camber_groups['mean'],
       yerr=camber_groups['std'], capsize=5,
       color='steelblue', edgecolor='white', alpha=0.85)
ax.set_title('Mean CL/CD by Camber Range (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Max Camber (% chord)')
ax.set_ylabel('Mean Max CL/CD')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('results/figures/camber_vs_clcd.png', dpi=150)
plt.close()
print("Saved: camber_vs_clcd.png")

# ── 4. Thickness range analysis ────────────────────────────────────────────
df['thickness_bin'] = pd.cut(df['max_thickness'],
                              bins=[0, 0.08, 0.10, 0.12, 0.15, 0.20],
                              labels=['<8%', '8-10%', '10-12%', '12-15%', '>15%'])

thickness_groups = df.groupby('thickness_bin', observed=True)['max_CL_CD'].agg(['mean', 'std', 'count'])
print("\nCL/CD by Thickness Range:")
print(thickness_groups.round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(thickness_groups.index.astype(str), thickness_groups['mean'],
       yerr=thickness_groups['std'], capsize=5,
       color='tomato', edgecolor='white', alpha=0.85)
ax.set_title('Mean CL/CD by Thickness Range (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Max Thickness (% chord)')
ax.set_ylabel('Mean Max CL/CD')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('results/figures/thickness_vs_clcd.png', dpi=150)
plt.close()
print("Saved: thickness_vs_clcd.png")

print("\nGeometry analysis complete.")
print(f"All figures saved to results/figures/")