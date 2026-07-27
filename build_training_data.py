"""Assemble the multi-Re training table.

1. Aggregate 200k metrics from raw polars (simulation_results.csv),
   using the same cleaning + metric logic as the sweep.
2. Concatenate with the 150k/300k/400k metrics.
3. Add n_points, filter sparse runs (fail loudly if the column is absent
   after this step).
4. Merge with GEOMETRY-ONLY columns (no stale performance columns).
5. Sanity-check that geometry is constant across each airfoil's Re rows.
"""

import pandas as pd

GEOMETRY_CSV = 'results/geometry_performance.csv'
METRICS_CSV  = 'results/airfoil_metrics_multiRe.csv'   # 150k/300k/400k
POLARS_200K  = 'results/simulation_results.csv'         # raw polars @ 200k
OUTPUT_CSV   = 'results/training_data_multiRe.csv'

MIN_POINTS = 10

GEOM_COLS = ['max_camber', 'max_camber_loc', 'max_thickness',
             'max_thickness_loc', 'le_thickness', 'te_thickness',
             'camber_at_25', 'camber_area']

METRIC_SCHEMA = ['airfoil', 'reynolds', 'max_CL', 'stall_angle',
                 'min_CD', 'max_CL_CD', 'best_alpha', 'CL_at_0', 'n_points']


def clean_polar(df):
    """Mirror of clean_results from the sweep - keep in sync."""
    df = df[df['CD'] > 0.008]
    df = df[df['CL_CD'].abs() < 150]
    median_cd = df['CD'].median()
    df = df[df['CD'] > median_cd * 0.3]
    df = df.drop_duplicates(subset='alpha', keep='last')
    if df['alpha'].min() > 1.0 or df['alpha'].max() < 5.0:
        return None
    if len(df) < 5:
        return None
    return df.reset_index(drop=True)


def metrics_from_polar(df, airfoil, reynolds):
    """Mirror of extract_metrics - one metrics row from one cleaned polar."""
    if df is None or len(df) < 3:
        return None
    max_cl_idx = df['CL'].idxmax()
    return {
        'airfoil': airfoil,
        'reynolds': reynolds,
        'max_CL': df['CL'].max(),
        'stall_angle': df.loc[max_cl_idx, 'alpha'],
        'min_CD': df['CD'].min(),
        'max_CL_CD': df['CL_CD'].max(),
        'best_alpha': df.loc[df['CL_CD'].idxmax(), 'alpha'],
        'CL_at_0': df.loc[df['alpha'].abs().idxmin(), 'CL'],
        'n_points': len(df),
    }


def build_200k_metrics():
    """Aggregate the raw 200k polars into one metrics row per airfoil."""
    polars = pd.read_csv(POLARS_200K)
    rows = []
    for name, grp in polars.groupby('airfoil'):
        cleaned = clean_polar(grp.copy())
        m = metrics_from_polar(cleaned, name, 200000)
        if m:
            rows.append(m)
    out = pd.DataFrame(rows)
    print(f"200k metrics aggregated from polars: {len(out)} airfoils")
    return out


def build():
    # --- 200k from polars ---
    m200 = build_200k_metrics()

    # --- 150k/300k/400k from the sweep's metrics CSV ---
    other = pd.read_csv(METRICS_CSV)
    print(f"150/300/400k metrics rows: {len(other)}")
    if 'n_points' not in other.columns:
        raise SystemExit(
            "ERROR: 'n_points' missing from " + METRICS_CSV + ".\n"
            "Add \"'n_points': len(df)\" to extract_metrics(), regenerate\n"
            "the multi-Re metrics CSV, then rerun. Refusing to build without\n"
            "the point-count filter."
        )

    # --- combine all four Re, aligned to one schema ---
    metrics = pd.concat([other[METRIC_SCHEMA], m200[METRIC_SCHEMA]],
                        ignore_index=True)
    print(f"Combined metrics rows (all 4 Re): {len(metrics)}")
    print("Rows per Re:")
    print(metrics.groupby('reynolds').size().to_string())

    # --- point-count filter, per run, before merge ---
    dropped = metrics[metrics['n_points'] < MIN_POINTS]
    if len(dropped):
        print(f"\nDropping {len(dropped)} runs below {MIN_POINTS} points, by Re:")
        print(dropped.groupby('reynolds').size().to_string())
    metrics = metrics[metrics['n_points'] >= MIN_POINTS].copy()
    print(f"Metrics after point filter: {len(metrics)}")

    # --- geometry, stripped to geometry only ---
    geom_full = pd.read_csv(GEOMETRY_CSV)
    geom = geom_full[['airfoil'] + GEOM_COLS].copy()
    print(f"\nGeometry rows (geometry cols only): {len(geom)}")

    # --- merge: geometry broadcast across each airfoil's Re rows ---
    merged = metrics.merge(geom, on='airfoil', how='inner')
    print(f"Merged rows: {len(merged)}")

    # --- name-mismatch report ---
    only_m = set(metrics['airfoil']) - set(geom['airfoil'])
    only_g = set(geom['airfoil']) - set(metrics['airfoil'])
    if only_m:
        print(f"In metrics but not geometry ({len(only_m)}): {sorted(only_m)}")
    if only_g:
        print(f"In geometry but not metrics ({len(only_g)}): {sorted(only_g)}")

    # --- completeness ---
    counts = merged.groupby('airfoil').size()
    print(f"\nRe-rows per airfoil: min={counts.min()}, max={counts.max()}")
    print(f"Airfoils with all 4 Re: {(counts == 4).sum()} of {len(counts)}")

    merged.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV}: {len(merged)} rows, {len(merged.columns)} cols")
    return merged


def sanity_check(merged, n=3):
    print("\nGeometry-constant check:")
    for name in merged['airfoil'].drop_duplicates().head(n):
        rows = merged[merged['airfoil'] == name]
        varies = [c for c in GEOM_COLS if rows[c].nunique() > 1]
        status = "OK - identical" if not varies else f"BAD - varies: {varies}"
        print(f"  {name} ({len(rows)} Re rows): {status}")


if __name__ == '__main__':
    m = build()
    sanity_check(m)