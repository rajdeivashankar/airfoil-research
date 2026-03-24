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

### Topic: Selig vs Lednicer format and convert_lednicer_to_selig

**What the two formats are:** There are two main formats in this data, Selig and Lednicer. Selig starts from the trailing edge and goes along the upper surface to the leading edge and then back to the trailing edge along the lower surface. Lednicer has two groups of data, one for the upper surface and one for the bottom surface, with both groups going from the leading edge to the trailing edge.

**Why XFOIL can't handle Lednicer directly:** XFOIL needs a continuous loop for the data in order to simulate how flow would affect the following coordinate. Selig provides this continuous loop while Lednicer provides two separate groups of data for the upper and lower surface.

**What the conversion does step by step:** The conversion takes each line of the data, determines if it is part of the upper or lower dataset, appends the coordinates to the correct list, then flips the order of the upper coordinates and appends the list of the lower coordinates to get a list of coordinates in a continuous loop.

**Why the leading edge duplicate matters:** Since the upper and lower datasets start at x = 0 in Lednicer, there is a duplicated point at the leading edge which affects the continuity of the loop. To resolve this the lower list bypasses the first valid coordinates on the lower dataset which corresponds to the repeated point.