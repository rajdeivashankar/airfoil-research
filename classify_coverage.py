"""Classify each airfoil's Re coverage by reading raw XFOIL output files.
Distinguishes genuine convergence failures from filter drops from successes,
because 'missing from the training table' conflates all three (E216 proved it:
converged fine at 400k but absent from the table)."""

import pandas as pd
import os

RAW_DIR = 'results/raw'
TRAINING_CSV = 'results/training_data_multiRe.csv'
RE_VALUES = [150000, 200000, 300000, 400000]
RE_200K_FROM_TABLE = 200000   # 200k has no raw file in RAW_DIR (separate source)

def count_data_rows(airfoil, reynolds):
    """Count valid 7-column numeric rows in a raw polar file.
    Returns -1 if the file is absent, 0 if present but headers-only
    (= convergence failure), else the row count."""
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

def classify():
    table = pd.read_csv(TRAINING_CSV)
    in_table = {(r.airfoil, int(r.reynolds)) for r in table.itertuples()}
    airfoils = sorted(table['airfoil'].unique())

    rows = []
    for name in airfoils:
        status = {}
        for Re in RE_VALUES:
            if Re == RE_200K_FROM_TABLE:
                # no raw file here; trust the table
                status[Re] = 'success' if (name, Re) in in_table else 'absent'
                continue
            n = count_data_rows(name, Re)
            if n == -1:
                status[Re] = 'no_file'
            elif n == 0:
                status[Re] = 'conv_fail'      # header only, zero data = failed to converge
            elif (name, Re) in in_table:
                status[Re] = 'success'
            else:
                status[Re] = 'filter_drop'    # had data, but pipeline dropped it
        rows.append({'airfoil': name, **{f'Re{Re}': status[Re] for Re in RE_VALUES}})

    cov = pd.DataFrame(rows)

    # coverage count = number of Re that made it into the table
    cov['n_success'] = cov.apply(
        lambda r: sum((r[f'Re{Re}'] == 'success') for Re in RE_VALUES), axis=1)

    # flag non-monotonic convergence (success-fail-success = likely numerical)
    def nonmono(r):
        seq = [r[f'Re{Re}'] in ('success',) for Re in RE_VALUES]  # ascending Re
        # a False flanked by True on both sides, anywhere in the sequence
        return any(seq[i-1] and not seq[i] and any(seq[i+1:])
                   for i in range(1, len(seq)))
    cov['nonmonotonic'] = cov.apply(nonmono, axis=1)

    return cov

if __name__ == '__main__':
    cov = classify()
    print("Coverage classification (per airfoil, per Re):\n")
    print(cov.to_string(index=False))
    print("\nCoverage summary:")
    print(cov['n_success'].value_counts().sort_index().to_string())
    print(f"\nGenuine convergence failures (any Re): "
          f"{(cov[[f'Re{Re}' for Re in RE_VALUES]] == 'conv_fail').any(axis=1).sum()}")
    print(f"Filter drops (any Re): "
          f"{(cov[[f'Re{Re}' for Re in RE_VALUES]] == 'filter_drop').any(axis=1).sum()}")
    print(f"Non-monotonic patterns (likely numerical): {cov['nonmonotonic'].sum()}")
    print("\nE216 (sanity check against the hand trace):")
    print(cov[cov['airfoil'] == 'e216'].to_string(index=False))