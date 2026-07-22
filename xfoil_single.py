"""Single-point XFOIL analysis for the aeroelastic spring model."""

import subprocess
import os

def analyze_airfoil(naca, reynolds, alpha):
    """Run XFOIL at a single angle of attack for a NACA airfoil.
    Returns (CL, CM), or (None, None) if XFOIL fails to converge."""

    output_file = f'results/raw/single_naca{naca}_Re{reynolds}_a{alpha}.txt'

    if os.path.exists(output_file):
        os.remove(output_file)

    commands = (
        f"NACA {naca}\n"        #Generates the NACA airfoil internally (no coordinate file needed)
        f"PANE\n"               #Organizes data points into panels
        f"OPER\n"               #Opens operating menu
        f"VISC\n"               #Turns on viscous analysis
        f"{reynolds}\n"         #Sets up Reynolds regime
        f"ITER\n"               #Sets maximum number of iterations
        f"200\n"
        f"PACC\n"               #Begins saving results to output_file
        f"{output_file}\n"
        f"\n"                   #Blank line confirms PACC filename prompt
        f"ALFA {alpha}\n"       #Runs a single angle of attack (instead of ASEQ sweep)
        f"PACC\n"               #Ends saving results
        f"\n"
        f"QUIT\n"
    )

    try:
        subprocess.run(
            ['xfoil.exe'],
            input=commands,
            capture_output=True,
            text=True,
            timeout=30          #Single point should be fast; if it hangs, treat as failure
        )
    except subprocess.TimeoutExpired:
        return None, None

    if not os.path.exists(output_file):
        return None, None

    last_row = None
    with open(output_file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) == 7:
                try:
                    last_row = [float(p) for p in parts]    #Keep overwriting — ends holding the LAST valid row
                except ValueError:
                    continue

    if last_row is None:
        return None, None                                   #File exists but no data row = XFOIL didn't converge

    return last_row[1], last_row[4]  # CL=col1, CM=col4 — VERIFY CM sign convention before trusting spring model