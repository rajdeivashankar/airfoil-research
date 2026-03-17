import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os

# Load results
combined_df = pd.read_csv('results/simulation_results.csv')
metrics_df = pd.read_csv('results/airfoil_metrics.csv')

os.makedirs('results/figures', exist_ok=True)

# ── 1. Full performance summary table ──────────────────────────────────────
summary = metrics_df.sort_values('max_CL_CD', ascending=False).reset_index(drop=True)
summary.index += 1  # rank from 1
summary.to_csv('results/performance_summary.csv', index=True)
print("Performance Summary (ranked by CL/CD):")
print(summary.to_string())

# ── 2. Lift curves — all airfoils ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
colors = cm.tab20(np.linspace(0, 1, len(combined_df['airfoil'].unique())))

for (name, group), color in zip(combined_df.groupby('airfoil'), colors):
    ax.plot(group['alpha'], group['CL'], '-', color=color, linewidth=1, label=name)

ax.set_title('Lift Curves — All 67 Airfoils (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Angle of Attack (deg)')
ax.set_ylabel('CL')
ax.legend(fontsize=6, ncol=4, loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/all_lift_curves.png', dpi=150)
plt.close()
print("\nSaved: all_lift_curves.png")

# ── 3. Drag polars — all airfoils ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
for (name, group), color in zip(combined_df.groupby('airfoil'), colors):
    ax.plot(group['CD'], group['CL'], '-', color=color, linewidth=1, label=name)

ax.set_title('Drag Polars — All 67 Airfoils (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('CD')
ax.set_ylabel('CL')
ax.legend(fontsize=6, ncol=4, loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/all_drag_polars.png', dpi=150)
plt.close()
print("Saved: all_drag_polars.png")

# ── 4. CL/CD comparison bar chart — top 20 ────────────────────────────────
top20 = summary.head(20)
fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(top20['airfoil'], top20['max_CL_CD'], color='steelblue', edgecolor='white')
ax.set_title('Top 20 Airfoils by Maximum CL/CD (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Airfoil')
ax.set_ylabel('Maximum CL/CD')
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('results/figures/top20_clcd.png', dpi=150)
plt.close()
print("Saved: top20_clcd.png")

# ── 5. Max CL comparison bar chart — top 20 ───────────────────────────────
top20_cl = summary.sort_values('max_CL', ascending=False).head(20)
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(top20_cl['airfoil'], top20_cl['max_CL'], color='tomato', edgecolor='white')
ax.set_title('Top 20 Airfoils by Maximum CL (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Airfoil')
ax.set_ylabel('Maximum CL')
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('results/figures/top20_maxcl.png', dpi=150)
plt.close()
print("Saved: top20_maxcl.png")

# ── 6. Stall angle distribution ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(summary['stall_angle'], bins=15, color='mediumseagreen', edgecolor='white')
ax.set_title('Distribution of Stall Angles — All Airfoils', fontsize=13, fontweight='bold')
ax.set_xlabel('Stall Angle (deg)')
ax.set_ylabel('Count')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/stall_angle_distribution.png', dpi=150)
plt.close()
print("Saved: stall_angle_distribution.png")

# ── 7. CL/CD vs max CL scatter ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
sc = ax.scatter(summary['max_CL'], summary['max_CL_CD'],
                c=summary['stall_angle'], cmap='viridis',
                s=60, edgecolors='gray', linewidth=0.5)
plt.colorbar(sc, label='Stall Angle (deg)')

# Label top 10
for _, row in summary.head(10).iterrows():
    ax.annotate(row['airfoil'], (row['max_CL'], row['max_CL_CD']),
                fontsize=7, xytext=(5, 3), textcoords='offset points')

ax.set_title('Aerodynamic Efficiency vs Max Lift (Re=200,000)', fontsize=13, fontweight='bold')
ax.set_xlabel('Maximum CL')
ax.set_ylabel('Maximum CL/CD')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/efficiency_vs_lift.png', dpi=150)
plt.close()
print("Saved: efficiency_vs_lift.png")

print(f"\nAll figures saved to results/figures/")
print(f"Summary CSV saved to results/performance_summary.csv")
print(f"\nDataset: {len(metrics_df)} airfoils | {len(combined_df)} total data points")