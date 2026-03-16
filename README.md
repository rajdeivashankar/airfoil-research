# Airfoil Performance Analysis for Small UAV Applications

**Independent Research Project** | High School Junior | 2025–2026

## Research Question
Can computational screening using XFOIL identify high-performance airfoil 
geometries for small UAV applications at low Reynolds numbers, and what 
geometric features predict optimal performance?

## Overview
This project performs large-scale aerodynamic analysis of 80+ airfoils 
using XFOIL, validates predictions against experimental wind tunnel data, 
and applies machine learning to identify geometric predictors of airfoil 
efficiency at low Reynolds numbers (Re = 100k–400k).

## Repository Structure
```
airfoil-research/
    data/          # Airfoil coordinate files from UIUC database
    results/       # Simulation output CSVs and plots
    scripts/       # Python automation pipeline
    paper/         # Research paper (in progress)
```

## Methods
- **Simulation**: XFOIL panel method solver
- **Dataset**: UIUC Airfoil Coordinate Database (80+ airfoils)
- **Validation**: NASA/UIUC experimental wind tunnel data
- **Analysis**: Statistical analysis + machine learning (scikit-learn)

## Key Results
*(Updated as research progresses)*

## Dependencies
```
pip install numpy pandas matplotlib scipy scikit-learn
```

## Status
🔄 In Progress — Target submission: Regeneron STS November 2026
```