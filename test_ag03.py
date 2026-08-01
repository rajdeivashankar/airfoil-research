import numpy as np
from extract_geometry import load_airfoil, extract_geometry

coords = load_airfoil('data/ag03.dat')
print("Loaded coords shape:", coords.shape)
print("x range:", coords[:,0].min(), "to", coords[:,0].max())
print("First 3 points:", coords[:3].tolist())
print("Number of points:", len(coords))

result = extract_geometry(coords)
print("RESULT:", result)