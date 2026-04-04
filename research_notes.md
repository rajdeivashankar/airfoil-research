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

**What the function does:** The function filters through the raw coordinate file and adds each x and y coordinate to a list.The raw files are not clean data and this helps filter the data into something usable.

**The four reasons a line gets skipped:** 1 - If the line is empty, caught by if not line: | 2 - If the line doesn't have exactly 2 parts, caught by in len(parts) == 2 | 3 - If either of the two parts are too large, caught by if x > 1.5 or y > 1.5 | 4 - If the 2 parts can't be converted into numbers, caught by xcept ValueError

**Why this matters for the project:** If one of the checks was missing it would lead to the airfoil being plotted incorrectly. For example, the Clark Y file has a slightly different format that would cause one coordinate to be plotted at (61.0, 61.0), which would severely affect the plots and XFOIL analysis.

### Topic: Selig vs Lednicer format and convert_lednicer_to_selig

**What the two formats are:** There are two main formats in this data, Selig and Lednicer. Selig starts from the trailing edge and goes along the upper surface to the leading edge and then back to the trailing edge along the lower surface. Lednicer has two groups of data, one for the upper surface and one for the bottom surface, with both groups going from the leading edge to the trailing edge.

**Why XFOIL can't handle Lednicer directly:** XFOIL needs a continuous loop for the data in order to simulate how flow would affect the following coordinate. Selig provides this continuous loop while Lednicer provides two separate groups of data for the upper and lower surface.

**What the conversion does step by step:** The conversion takes each line of the data, determines if it is part of the upper or lower dataset, appends the coordinates to the correct list, then flips the order of the upper coordinates and appends the list of the lower coordinates to get a list of coordinates in a continuous loop.

**Why the leading edge duplicate matters:** Since the upper and lower datasets start at x = 0 in Lednicer, there is a duplicated point at the leading edge which affects the continuity of the loop. To resolve this the lower list bypasses the first valid coordinates on the lower dataset which corresponds to the repeated point.

## March 25, 2026

### Topic: Reynolds number research

**What is Reynolds number physically?**

The Reynolds number is a dimensionless quantity that compares **inertial forces** to **viscous forces** in a fluid flow. Inertial forces are related to the motion of the fluid (how much it resists changes in velocity), while viscous forces come from the fluid’s internal friction or “stickiness.”
Physically, this ratio tells us which effect dominates the flow:
- High Reynolds number → inertia dominates → flow tends to be turbulent  
- Low Reynolds number → viscosity dominates → flow is smoother and more laminar  
So, Reynolds number essentially describes the behavior or structure of the flow around an object.

**Why do small UAVs operate at low Reynolds numbers?**

Small UAVs operate at low Reynolds numbers mainly because of their **small size and relatively low speeds**. The Reynolds number depends on velocity and a characteristic length (like wing chord), so when the vehicle is small, the length scale is small, which lowers the Reynolds number.

At these low Reynolds numbers:
- Viscous effects become much more important  
- Boundary layers are thicker and more influential  
- Flow is more likely to stay laminar and separate earlier  

This means small UAV aerodynamics are dominated by viscosity, unlike large aircraft where inertial forces dominate.

**How does this connect to why I chose Re = 200,000 for our simulations?**

I simulated at Re=200,000 as a starting point representing typical small UAV cruise conditions because it falls within the typical low Reynolds number regime that small UAVs operate in. NASA explains that matching Reynolds number between experiments and real-world conditions is critical to correctly capturing the balance between inertial and viscous forces.

By simulating at Re = 200,000:
- We replicate the correct physics of the flow (especially viscous effects)
- We ensure the boundary layer behavior and drag characteristics are realistic
- Our results better represent actual UAV flight conditions  

If I used a much higher Reynolds number, I would incorrectly model the flow as more inertia-dominated, leading to inaccurate predictions of lift, drag, and flow separation.

## March 26, 2026

### Topic: XFOIL commands and what they do

**What each command does:**
- LOAD: Loads the airfoil coordinate file into XFOIL
- PANE: Splits the coordinate file into panels and organizes the data
- OPER: Enters the operating meny in XFOIL
- VISC: Enables viscous analysis
- {reynolds}: Sets up the Reynolds number
- ITER: Sets the maximum amount of iterations
- PACC: Turns on/off polar accumulation that saves results in a results file
- ASEQ: Sets the range and step of angles of attack that should be tested
- QUIT: Ends the XFOIL analysis

**Why viscous analysis matters at low Reynolds numbers:**
Low Reynolds numbers have a high ratio of viscous forces to inertial forces, increasing the need of viscous analysis to get accurate results. Viscous mode activates XFOIL's boundary layer model which accounts for skin friction drag and flow separation.

**What would happen if we forgot PACC:**
The results of the XFOIL simulation would not save to a file resulting in an empty dataset since the data frame is built on that results file.

## March 27, 2026

### Topic: NACA 4-Digit Airfoil Nomenclature

**What does each digit in NACA 2412 mean physically?**

The NACA 4-digit airfoil naming system encodes the **shape of the airfoil geometry** using four digits:

For **NACA 2412**:

- **First digit (2)** → Maximum camber = **2% of chord**
  - This tells us how much the airfoil is curved.
  - Physically: how far the mean camber line deviates from a straight line.
  - Higher camber → more lift at lower angles of attack.

- **Second digit (4)** → Location of maximum camber = **40% of chord from the leading edge**
  - This determines *where* the airfoil is most curved.
  - Physically: shifts lift distribution along the wing.
  - Forward camber → more front-loaded lift, affects pitching moment.

- **Last two digits (12)** → Maximum thickness = **12% of chord**
  - This defines how thick the airfoil is.
  - Physically: impacts structural strength, drag, and stall behavior.
  - Thickness distribution is symmetric about the chord line.

So overall:
- Camber = 0.02c  
- Camber location = 0.4c  
- Thickness = 0.12c

### Connection to extract_geometry.py

The NACA 4-digit system defines airfoil geometry analytically, while `extract_geometry.py` reconstructs those same parameters numerically from coordinate data. The script separates upper and lower surfaces, interpolates them onto a normalized chord grid (x/c), and computes geometric features.

The camber line is calculated as the average of the upper and lower surfaces, and its maximum value (`max_camber`) corresponds to the first NACA digit (example: 0.02 for NACA 2412). The location of this maximum (`max_camber_loc`) matches the second digit (example: 0.4c). Thickness is computed as the difference between upper and lower surfaces, and its maximum (`max_thickness`) corresponds to the last two digits (example: 0.12c).

Additional parameters like `max_thickness_loc`, `le_thickness`, and `te_thickness` extend beyond the NACA definition and provide more detailed shape characterization. Metrics such as `camber_at_25` and `camber_area` help quantify how camber is distributed along the chord.

This connection allows validation that coordinate files match their NACA labels and ensures accurate geometry is used in simulations. Ultimately, the script bridges theoretical airfoil definitions and real data, allowing direct comparison between geometry and aerodynamic performance.

## March 29, 2026
### Topic: extract_metrics function — performance metrics and defensive programming

**What the function does overall:**
The function takes the raw data from the simulation and converts it into usable metrics that can be analyzed by the model.

**What idxmax() returns and how we use it to find stall angle:**
The function idxmax() returns the index of where the CL is the highest across the distribution along the airfoil. This is used to find the stall angle since lift rises until it drops sharply as you increase the angle of attack, so the point where the CL is the highest is where the alpha value is the stall angle.

**What CL_at_0 tells us physically:**
CL at 0 tells us how much lift an airfoil would generate with an angle of attack of 0 degrees. A symmetric airfoil has 0 camber and therefore generates no lift at an angle of attack of 0 degrees, while a cambered airfoil would generate some lift due to its shape. This value is a direct indicator of camber magnitude.

**Why abs().idxmin() instead of direct alpha=0 lookup:**
If XFOIL skips alpha=0 during a run, abs().idxmin() finds the angle of attack closest to zero and uses that CL value as an estimate instead of leaving an empty gap in the dataset.

**Why incomplete data matters for this research:**
Incomplete data matters for this research since different airfoils are not comparable to each other with the model if there is empty points in the datasets. With a dataset of 67 airfoils every dataset that isn't full decreases the accuracy of the model.

## March 30, 2026
### Lift-to-Drag Ratio (L/D) and UAV Efficiency

Lift-to-drag ratio (L/D) measures how much useful lift an airfoil or wing generates compared to the drag it produces. Physically, it represents aerodynamic efficiency. A higher L/D means the aircraft can produce the same lift with less energy lost to air resistance.

For UAVs, L/D is more important than maximum lift alone because efficiency—not just force generation—determines performance. A design with very high lift but also high drag will require more power, reducing flight time and range. In contrast, a high L/D airfoil allows the UAV to sustain flight with less energy, improving endurance and overall efficiency.

This is why metrics like maximum CL/CD (a proxy for L/D) are used in analysis. They directly reflect how effectively an airfoil converts aerodynamic forces into useful flight performance.

## March 31, 2026
### Topic: Boundary Layer Separation and Connections to XFOIL Convergence Loss

**What is boundary layer separation physically?**

Boundary layer separation occurs when the airflow near a surface loses enough energy that it can no longer stay attached. As the flow moves into a region of increasing pressure (adverse pressure gradient), it slows down, stops, and can even reverse direction. This causes the flow to detach from the surface, forming a turbulent wake and reducing lift while increasing drag.

**What conditions affect when separation occurs?**

Earlier separation:
- High angle of attack  
- Low Reynolds number  
- Laminar boundary layer  
- Steep pressure recovery  

Later separation:
- Turbulent boundary layer (more mixing, more energy)  
- Higher Reynolds number  
- Smooth, gradual airfoil shape  
- Added energy to the flow (e.g., roughness or control methods)

**Why does XFOIL lose convergence near stall?**

XFOIL assumes mostly attached flow. Near stall, separation becomes large and unstable, with reversed and chaotic flow. This violates XFOIL’s assumptions, causing the numerical solution to break down and fail to converge.

## April 1, 2026
### Topic: `clean_results()` — data cleaning rationale and convergence artifact identification

**What `CD < 0.008` is catching:**
When XFOIL's iteration loop hasn't converged for a given angle of attack, the boundary layer calculation never settles on a physical solution, so drag components don't add up correctly and CD comes out near zero or negative. Real airfoils always have some drag. Any value below 0.008 is a convergence artifact, not a real aerodynamic result.

**Why `|CL/CD| > 150` is the second filter:**
A near-zero CD in the denominator causes the ratio to explode toward infinity regardless of CL. Real airfoils at low Reynolds numbers top out around CL/CD of 100-120 in ideal conditions — the best airfoil in the dataset, E216, came in at 99.2. Anything above 150 is a math artifact from a bad CD value, not a high-performing airfoil. The two filters work together: CD < 0.008 catches the most obvious garbage values, CL/CD > 150 catches anything that slips through with slightly less extreme but still unrealistic drag.

**Why duplicate alpha values exist and why we keep the last:**
Duplicates occur when the batch loop picks up both the original Lednicer file and the converted Selig file for the same airfoil, simulating it twice at the same angles of attack. We keep the last result because it came from the correctly formatted converted file that XFOIL can handle properly.

## April 2, 2026

## April 3, 2026
### Topic: `extract_geometry.py` — surface separation, interpolation, and geometry calculations

**What `le_idx = np.argmin(coords[:, 0])` does:**
Finds the index of the point with the minimum x value. Since airfoil coordinates are normalized so x=0 is the leading edge and x=1 is the trailing edge, the minimum x point is the leading edge. This becomes the split point between upper and lower surfaces — the one point both surfaces share.

**Why interpolation onto a common x grid is necessary:**
Raw coordinates can't be used directly for three reasons:
- Mismatched x positions — upper and lower surfaces don't have points at the same x locations
- Unequal point counts — numpy can't subtract arrays of different lengths
- Uneven spacing — raw files cluster points near the leading edge

Interpolating both surfaces onto 100 evenly spaced points from x=0.01 to x=0.99 resolves all three problems.

**Camber line: `camber_line = (y_upper + y_lower) / 2`**
The camber line is the locus of midpoints between upper and lower surfaces at every x. A symmetric airfoil has `y_upper = -y_lower` everywhere, so the camber line = 0, which is why symmetric airfoils produce `CL_at_0 = 0`.

**Thickness: `thickness = y_upper - y_lower`**
The full gap between upper and lower surfaces at each x. Subtraction gives the gap; averaging would give the midpoint (camber). Same two numbers, different operations, completely different geometric properties.

**Connection to NACA nomenclature:**
These formulas reconstruct the same parameters encoded in NACA 4-digit names. For NACA 2412: `max_camber=0.02`, `max_camber_loc=0.4`, `max_thickness=0.12` should match digits 2, 4, 12. This lets us validate the geometry extraction is working correctly.

