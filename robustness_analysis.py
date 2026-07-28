"""Airfoil robustness across the Reynolds envelope.

Robustness metrics (CV, min CL/CD) are computed ONLY on airfoils with full
4-Re coverage - a CV over 3 points is not comparable to one over 4.

Partial-coverage airfoils are sorted into three buckets by WHY they are
partial, distinguishing convergence (pre-cleaning) from filtering:
  - edge      : genuine low-Re convergence failure (monotonic) -> tentative fragility
  - interior  : mid-envelope convergence hole (flanked by successes) -> likely numerical
  - filtered  : converged at all 4 Re but a run was dropped by the point filter
                -> data-completeness exclusion, NOT fragility

Convergence is measured the same way for all four Re: 150k/300k/400k by counting
raw polar rows, 200k from simulation_results.csv (which has no raw .txt files).
"""

import pandas as pd
import numpy as np
import os

TRAINING_CSV = 'results/training_data_multiRe.csv'
POLARS_200K = 'results/simulation_results.csv'
RAW_DIR = 'results/raw'
RE_VALUES = [150000, 200000, 300000, 400000]
RE_200K = 200000
METRIC = 'max_CL_CD'   # robustness computed on peak CL/CD per run

os.makedirs('results/figures', exist_ok=True)

# 200k has no raw .txt files - its polars live here (raw, pre-cleaning).
# Load once so 200k convergence is measured the same way as the other Re.
_polars_200k = pd.read_csv(POLARS_200K)
_airfoils_200k = set(_polars_200k['airfoil'].unique())


def count_data_rows(airfoil, reynolds):
    """Valid 7-column rows in a raw polar. -1 if file absent, 0 if
    header-only (convergence failure)."""
    path = f'{RAW_DIR}/results_{airfoil}_Re{reynolds}.txt'
    if not os.path.exists(path):
        return -1
    n = 0
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 7:
                try:
                    [float(p) for p in parts]
                    n += 1
                except ValueError:
                    continue
    return n


def converged(airfoil, reynolds):
    """True if XFOIL produced data at this Re, pre-cleaning - measured the
    same way for all four Re. 200k comes from simulation_results.csv (no raw
    .txt files exist); the other three from raw polar row counts."""
    if reynolds == RE_200K:
        return airfoil in _airfoils_200k
    return count_data_rows(airfoil, reynolds) > 0


def failure_pattern(conv_flags):
    """conv_flags: list of bools in ascending Re order.
    'interior' if a non-converged Re is flanked by convergence on both sides,
    else 'edge' (boundary failure), else 'full'."""
    interior = any(
        (not conv_flags[i]) and any(conv_flags[:i]) and any(conv_flags[i+1:])
        for i in range(len(conv_flags))
    )
    if interior:
        return 'interior'
    if not all(conv_flags):
        return 'edge'
    return 'full'


def analyze():
    df = pd.read_csv(TRAINING_CSV)
    in_table = {(r.airfoil, int(r.reynolds)) for r in df.itertuples()}
    airfoils = sorted(df['airfoil'].unique())

    full_rows = []       # robustness metrics for genuine 4-Re airfoils
    edge_list = []       # genuine low-Re convergence failure
    interior_list = []   # mid-envelope convergence hole (likely numerical)
    filtered_list = []   # converged at all 4 Re but a run was point-filtered

    for name in airfoils:
        sub = df[df['airfoil'] == name]
        present_Re = set(sub['reynolds'].astype(int))
        n_in_table = len(present_Re)

        if n_in_table == 4:
            vals = np.array([sub[sub['reynolds'] == Re][METRIC].iloc[0]
                             for Re in RE_VALUES])
            mean = vals.mean()
            cv = vals.std() / mean if mean != 0 else np.nan
            full_rows.append({
                'airfoil': name,
                'mean_CL_CD': mean,
                'min_CL_CD': vals.min(),
                'max_CL_CD': vals.max(),
                'cv': cv,
            })
        else:
            # Partial: fewer than 4 Re survived into the table. Split by WHY
            # each missing Re is missing - convergence failure vs filter drop.
            conv_flags = [converged(name, Re) for Re in RE_VALUES]

            if all(conv_flags):
                # Converged at every Re but lost >=1 run to the point filter.
                # Not fragile - a data-completeness exclusion, not a physics signal.
                filtered_Re = [Re for Re in RE_VALUES
                               if (name, Re) not in in_table]
                filtered_list.append({
                    'airfoil': name,
                    'filtered_Re': filtered_Re,
                    'note': 'converged at all 4 Re; run(s) dropped by point filter'
                })
            else:
                # At least one genuine convergence failure - classify its shape.
                pat = failure_pattern(conv_flags)
                entry = {
                    'airfoil': name,
                    'converged_Re': [Re for Re, c in zip(RE_VALUES, conv_flags) if c],
                    'failed_Re': [Re for Re, c in zip(RE_VALUES, conv_flags) if not c],
                }
                if pat == 'interior':
                    interior_list.append(entry)
                else:
                    edge_list.append(entry)

    full = pd.DataFrame(full_rows)

    # Integrity: every full-coverage airfoil must genuinely have converged at all 4 Re
    for r in full_rows:
        name = r['airfoil']
        assert all(converged(name, Re) for Re in RE_VALUES), \
            f"{name} in full set but did not converge at all 4 Re"
    print(f"Integrity check passed: all {len(full_rows)} full-coverage airfoils "
          f"converged at 4 Re.\n")

    return full, edge_list, interior_list, filtered_list


def report(full, edge_list, interior_list, filtered_list):
    print(f"Full-coverage airfoils (robustness computed): {len(full)}\n")

    cv_med = full['cv'].median()
    min_med = full['min_CL_CD'].median()
    print(f"Median CV = {cv_med:.3f}   Median min CL/CD = {min_med:.1f}\n")

    print("Robustness is a continuous tradeoff, not four boxes - the median\n"
          "lines on the map are visual reference only. Naming the extremes:\n")

    # Robust extreme: genuinely flat AND high worst-case (bottom-quartile CV,
    # top-quartile min) - a real corner, not a median artifact
    cv_q25 = full['cv'].quantile(0.25)
    min_q75 = full['min_CL_CD'].quantile(0.75)
    robust_corner = full[(full['cv'] <= cv_q25) & (full['min_CL_CD'] >= min_q75)]
    print("ROBUST extreme (lowest-quartile CV AND highest-quartile worst-case):")
    if len(robust_corner):
        print(robust_corner.sort_values('cv')
              [['airfoil', 'min_CL_CD', 'cv', 'mean_CL_CD']].round(3).to_string(index=False))
    else:
        print("  (none satisfy both - the corner is empty; report the trend instead)")

    # Specialist extreme: highest CV (swings hardest across Re)
    print("\nSPECIALIST extreme (highest CV - largest swing across Re):")
    print(full.sort_values('cv', ascending=False).head(5)
          [['airfoil', 'min_CL_CD', 'cv', 'max_CL_CD']].round(3).to_string(index=False))

    # The continuous relationship: does a higher peak cost you consistency?
    corr = full['max_CL_CD'].corr(full['cv'])
    print(f"\nPeak CL/CD vs CV correlation: r = {corr:.3f}")
    print("(positive = higher-peak airfoils tend to swing more across Re -\n"
          " the peak-vs-consistency tradeoff, stated as a trend not a box)")

    print(f"\n--- Partial coverage ---")

    print(f"\nEDGE failures (genuine low-Re convergence failure, monotonic) -\n"
          f"tentative low-Re fragility, flag for higher-fidelity check:")
    for e in edge_list:
        print(f"  {e['airfoil']}: converged at {e['converged_Re']}, failed at {e['failed_Re']}")

    print(f"\nINTERIOR failures (mid-envelope convergence hole, flanked by\n"
          f"successes) - likely NUMERICAL artifact, NOT a fragility claim:")
    for e in interior_list:
        print(f"  {e['airfoil']}: converged at {e['converged_Re']}, failed at {e['failed_Re']}")

    print(f"\nCONVERGED-BUT-FILTERED (converged at all 4 Re; a run was dropped by\n"
          f"the point filter - a data-completeness exclusion, NOT fragility):")
    for e in filtered_list:
        print(f"  {e['airfoil']}: filtered at {e['filtered_Re']}")

    return cv_med, min_med


def plot_map(full, cv_med, min_med):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.scatter(full['cv'], full['min_CL_CD'], s=70, alpha=0.75,
               color='steelblue', edgecolors='white', linewidth=0.7, zorder=3)

    ax.axvline(cv_med, color='gray', ls='--', lw=1, alpha=0.6)
    ax.axhline(min_med, color='gray', ls='--', lw=1, alpha=0.6)

    # label standouts: the robust corner and the highest-swing / highest-peak airfoils
    cv_q25 = full['cv'].quantile(0.25)
    min_q75 = full['min_CL_CD'].quantile(0.75)
    for _, r in full.iterrows():
        if (r['cv'] <= cv_q25 and r['min_CL_CD'] >= min_q75) or \
           r['max_CL_CD'] == full['max_CL_CD'].max() or \
           r['cv'] == full['cv'].max():
            ax.annotate(r['airfoil'], (r['cv'], r['min_CL_CD']),
                        fontsize=7, alpha=0.8,
                        xytext=(4, 3), textcoords='offset points')

    ax.set_xlabel('Coefficient of variation of CL/CD across Re  (lower = more robust)')
    ax.set_ylabel('Worst-case (min) CL/CD across Re')
    ax.set_title('Airfoil Robustness Map: consistency vs worst-case performance\n'
                 f'(full 4-Re coverage, n={len(full)}, Re = 150k-400k)',
                 fontweight='bold', fontsize=12)
    ax.text(0.02, 0.98, 'ROBUST\nhigh-performers', transform=ax.transAxes,
            va='top', ha='left', fontsize=9, color='green', alpha=0.7)
    ax.text(0.98, 0.98, 'SPECIALISTS\n(high peak, high swing)', transform=ax.transAxes,
            va='top', ha='right', fontsize=9, color='darkorange', alpha=0.7)
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig('results/figures/robustness_map.png', dpi=150)
    plt.close()
    print("\nSaved: results/figures/robustness_map.png")


if __name__ == '__main__':
    full, edge_list, interior_list, filtered_list = analyze()
    cv_med, min_med = report(full, edge_list, interior_list, filtered_list)
    full.sort_values('min_CL_CD', ascending=False).to_csv(
        'results/robustness_metrics.csv', index=False)
    print("Saved: results/robustness_metrics.csv")
    plot_map(full, cv_med, min_med)