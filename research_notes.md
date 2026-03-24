# Research Notes — UAV Airfoil Study
### Raj Deivashankar | Started March 2026

## March 23, 2026

### Topic: Airfoil coordinate system and plotting

**Observation:** axis('equal') in matplotlib is essential for airfoil plots
because airfoils are typically 8-15% thick. Without equal axes the thickness
is visually exaggerated with the scale between the x-axis and y-axis not being
uniform, making geometric comparison unreliable. This could cause me to incorrectly
judge which airfoils are thicker or more cambered when visually comparing plots,
leading to inaccurate preconceptions about the geometry-performance relationships.

### Topic: load_airfoil function — how file parsing works

**What the function does** The function filters through the raw coordinate file and adds each x and y coordinate to a list.The raw files are not clean data and this helps filter the data into something usable.

**The four reasons a line gets skipped:** 1 - If the line is empty, caught by if not line: | 2 - If the line doesn't have exactly 2 parts, caught by in len(parts) == 2 | 3 - If either of the two parts are too large, caught by if x > 1.5 or y > 1.5 | 4 - If the 2 parts can't be converted into numbers, caught by xcept ValueError

**Why this matters for the project:** If one of the checks was missing it would lead to the airfoil being plotted incorrectly. For example, the Clark Y file has a slightly different format that would cause one coordinate to be plotted at (61.0, 61.0), which would severely affect the plots and XFOIL analysis.