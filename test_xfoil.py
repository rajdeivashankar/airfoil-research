import subprocess
import os

def run_xfoil_test():
    """Run a single XFOIL simulation and print results"""
    
    # Commands to send to XFOIL
    commands = "LOAD data/naca2412.dat\nPANE\nOPER\nVISC\n200000\nITER\n100\nPACC\nresults_test.txt\n\nASEQ -5 10 1\nPACC\n\nQUIT\n"
    
    # Run XFOIL as a subprocess
    process = subprocess.run(
        ['xfoil.exe'],
        input=commands,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("XFOIL Output:")
    print(process.stdout[-2000:])  # Print last 2000 chars of output
    
    # Check if results file was created
    if os.path.exists('results_test.txt'):
        print("\nResults file created successfully!")
        print("\nContents:")
        with open('results_test.txt', 'r') as f:
            print(f.read())
    else:
        print("\nNo results file found - something went wrong")

run_xfoil_test()