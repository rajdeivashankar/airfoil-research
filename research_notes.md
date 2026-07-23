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

**The four reasons a line gets skipped:** 

  1 - If the line is empty, caught by if not line:

  2 - If the line doesn't have exactly 2 parts, caught by in len(parts) == 2

  3 - If either of the two parts are too large, caught by if x > 1.5 or y > 1.5
  
  4 - If the 2 parts can't be converted into numbers, caught by xcept ValueError

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

**What `idxmax()` returns and how we use it to find stall angle:**
The function `idxmax()` returns the index of where the CL is the highest across the distribution along the airfoil. This is used to find the stall angle since lift rises until it drops sharply as you increase the angle of attack, so the point where the CL is the highest is where the alpha value is the stall angle.

**What `CL_at_0` tells us physically:**
CL at 0 tells us how much lift an airfoil would generate with an angle of attack of 0 degrees. A symmetric airfoil has 0 camber and therefore generates no lift at an angle of attack of 0 degrees, while a cambered airfoil would generate some lift due to its shape. This value is a direct indicator of camber magnitude.

**Why `abs().idxmin()` instead of direct alpha=0 lookup:**
If XFOIL skips alpha=0 during a run, `abs().idxmin()` finds the angle of attack closest to zero and uses that CL value as an estimate instead of leaving an empty gap in the dataset.

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
### Topic: Camber Line and Connection to Lift

**What does the camber line represent physically?**

The camber line is the curve halfway between the upper and lower surfaces of an airfoil. Physically, it represents the airfoil’s overall curvature and how “bent” the shape is. A symmetric airfoil has a flat camber line, while a cambered airfoil has a curved one.

**How does camber generate lift?** 

Camber changes how air flows over the airfoil. On a cambered airfoil, the upper surface accelerates the flow more and lowers pressure, while the lower surface maintains relatively higher pressure. It also deflects air downward more effectively, contributing to lift through both pressure difference and momentum change. Compared to a symmetric airfoil, a cambered one produces lift even at zero angle of attack.

**Why does more camber mean more lift at low angles of attack?**

More camber increases the airfoil’s curvature, which strengthens the pressure difference between the upper and lower surfaces. This allows the airfoil to generate higher lift even at small angles of attack, effectively shifting the lift curve upward and increasing lift at low speeds.

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

## Camber Area vs. Maximum Camber

Maximum camber measures the single greatest distance between the camber line and the chord line, capturing the peak curvature of an airfoil. However, it does not describe how that curvature is distributed along the chord. Two airfoils can have the same maximum camber but very different overall shapes if one remains cambered over a larger portion of the chord.

Camber area, computed as the integral of the absolute camber line, captures the total amount of camber present across the entire airfoil. It acts as a measure of overall curvature rather than just the peak value. As a result, camber area may correlate more strongly with aerodynamic performance metrics because it reflects both the magnitude and distribution of camber, whereas maximum camber only reflects the largest local deviation.

## June 19, 2026
## Topic: Correlation matrix interpretation and binning analysis in `analyze_geometry.py`

**Why thickness correlates weakly with CL/CD but strongly with min_CD:**
Thickness has a direct, strong physical effect on drag — more surface area and a blunter profile increase skin friction drag and pressure drag, which is why `max_thickness` correlates strongly with `min_CD`. But thickness has only a weak, indirect effect on lift. Camber is what actually generates lift, by changing how flow accelerates over the top surface versus the bottom. Since `max_CL/CD` is a ratio dominated by the lift side for well-designed airfoils, and thickness barely moves the lift side, thickness ends up looking almost irrelevant to CL/CD (R=0.060) even though it clearly matters for drag alone.

**What `pd.cut()` does and why binning reveals more than a single correlation number:**
`pd.cut()` takes a continuous numeric column (e.g. `max_camber`) and slices it into discrete ranges like "0-2%", "2-4%", etc. Every airfoil is assigned to one bin based on its value, and we can compute the mean CL/CD within each bin.

A correlation coefficient like R=0.723 (max_camber vs max_CL/CD) assumes a linear relationship — it measures how well a straight line fits the data. The camber bin results show a parabola instead:

- 0-2%: mean CL/CD = 61.6
- 2-4%: mean CL/CD = 73.9
- 4-6%: mean CL/CD = 82.3 (peak)
- 6-8%: mean CL/CD = 81.7
- 8-12%: mean CL/CD = 79.5

A single R value can never capture "there's an optimal middle range, and too much or too little both hurt performance" — that non-linear shape only shows up when you bin the data and look at the pattern directly.

**Why 4-6% camber is the optimal range:**
Below 4%, the airfoil isn't generating enough lift to be efficient. Above 6%, the additional camber starts adding drag (more curvature, more flow acceleration, more pressure drag) faster than it adds useful lift. The 4-6% range balances lift generation against the drag penalty of excess curvature.

**Why thickness also shows a parabolic relationship:**
- <8%: mean CL/CD = 57.75
- 8-10%: mean CL/CD = 67.03
- 10-12%: mean CL/CD = 73.07
- 12-15%: mean CL/CD = 73.75 (peak)
- >15%: mean CL/CD = 67.10

The high end (>15%) underperforms because thickness mainly adds skin friction and pressure drag without helping lift. The low end (<8%) underperforms for a different reason: very thin airfoils at low Reynolds numbers are prone to laminar separation bubbles and abrupt stall. At low Re the boundary layer is naturally thick and laminar, and a very thin airfoil doesn't have enough surface curvature to keep flow attached around the leading edge. The flow separates early, adding its own drag penalty and risking premature stall. So thin airfoils don't just fail to gain extra lift — they actively lose efficiency from separation. 12-15% is the sweet spot where neither the high-thickness drag problem nor the low-thickness separation problem dominates.

**Follow-up reading:** laminar separation bubbles at low Reynolds numbers — connects directly to earlier boundary layer separation notes and should strengthen the discussion section of the paper.

## July 22, 2026 - Divergence theory + single-point XFOIL function

### Divergence concepts (Dowell prep)

Static divergence model: wing section on torsional spring, lift at the AC, elastic axis a distance e behind it. Lift x e gives a nose-up moment, twist raises lift, spring resists. Three key results:

- **EA position:** q_D = K_theta / (e c S CL_alpha), so divergence speed scales as 1/e. Moving the EA toward the AC shrinks the moment arm and weakens the feedback loop. At e = 0 the loop is severed (q_D -> infinity). EA ahead of the AC flips the sign and the feedback becomes self-correcting. This is why forward-swept wings (X-29) needed aeroelastic tailoring.
- **Stiffness:** the aerodynamic moment grows with q but K_theta does not, so q_D is linear in K_theta. Stiffer wing = less twist per unit moment = higher divergence speed.
- **At q_D:** solving the moment balance gives theta = (initial AoA term) / (K_theta - q e c S CL_alpha). The denominator is the effective stiffness. Below q_D it is positive and theta is finite. At exactly q_D it passes through zero - theta is singular, no equilibrium exists, and theta grows asymptotically as q approaches q_D from below. Above q_D the twist runs away until stall or structural failure. Framing that matters: q_D is an eigenvalue problem (at what q can the wing hold nonzero twist with zero input), and divergence is static, which distinguishes it from flutter.

### analyze_airfoil() - xfoil_single.py

Spring model needs one call per iteration: alpha in, (CL, CM) out. Single-point version of run_xfoil() - ALFA instead of ASEQ, NACA generator instead of coordinate files. Own file because run_xfoil_batch.py has no main guard, so importing from it would launch the full sweep. Returns (None, None) on timeout, missing file, or no valid data row, and rejects any row whose alpha does not match the request within 0.01 deg.

### Verification

- Sign convention confirmed: NACA 2412 at alpha = 0, Re 200k gives CM = -0.0608. Camber physically produces a nose-down moment, and XFOIL reports it as negative, so in XFOIL negative CM = nose-down and positive CM = nose-up (standard nose-up-positive convention). The divergence moment balance treats nose-up as the positive, destabilizing direction (nose-up twist raises alpha, which raises lift), so XFOIL's sign matches and CM feeds into the spring model directly with no sign flip. CL = 0.28 consistent with the 2412's ~-2 deg zero-lift angle.
- Repeat calls give identical values (stale-file cleanup works).
- Failure envelope: converges at 5 deg, returns (None, None) at 40 deg, but converges at 25 deg to plausible-looking post-stall numbers (CL = 0.69). Converged does not mean correct.

### Implication for the spring model

(None, None) alone is not a sufficient tripwire since XFOIL converges quietly in deep stall. The loop needs a validity cap (~14-15 deg effective alpha) and must record three outcomes separately: equilibrium below cap (below q_D), twist past cap (diverged), XFOIL failure (tool, not physics). q_D comes from the boundary between the first two, so keeping tool failures out of that bookkeeping protects the estimate.

## July 22, 2026 - divergence_model.py verification

### Test configuration

Baseline case unless noted otherwise:

| Parameter | Value |
|---|---|
| Airfoil | NACA 2412 |
| Re (fixed) | 200,000 |
| alpha_0 | 2.0 deg |
| K_theta | 45.0 N*m/rad |
| e | 0.05 m |
| c | 0.25 m |
| span | 1.0 m (so S = 0.25 m^2) |
| rho | 1.225 kg/m^3 |
| tolerance | 0.001 deg |
| max_iter | 50 |
| alpha_cap | 14.0 deg |

V = 11.8 m/s chosen so that Re = rho*V*c/mu matches the fixed Re = 200k input. The original test value of 15.0 m/s was inconsistent (Re ~254k) and was corrected before testing.

### Test 1 - subcritical equilibrium (V = 11.8 m/s, q = 85.28 Pa)

Result: status = converged, theta = 0.3271 deg, alpha_eff = 2.3271 deg, 5 iterations, CL = 0.547, CM = -0.0612.

Hand-verified against the moment balance:
- Lift-offset term: q*S*CL*e = 85.28 * 0.25 * 0.547 * 0.05 = +0.583 N*m
- Camber moment term: q*S*c*CM = 85.28 * 0.25 * 0.25 * (-0.0612) = -0.326 N*m
- Net: 0.257 N*m, divided by K_theta = 45 gives 0.005714 rad = 0.327 deg

Matches the code output exactly. Note the two terms oppose each other: the camber's nose-down moment cancels roughly 56% of the lift's nose-up moment. CM_ac has a large effect on equilibrium twist while contributing nothing to q_D, which is the theoretical point demonstrated numerically.

### Test 2 - divergence branch (V = 60 m/s, q = 2205 Pa)

Result: status = diverged, theta = 34.27 deg, alpha_eff = 36.27 deg, 3 iterations, reason = alpha_eff exceeded validity cap.

Exited via the alpha cap rather than max_iter, which is the clean divergence signal. Twist grew rather than contracting, as expected above q_D.

### Test 3 - solver failure branch (V = 60 m/s, alpha_cap raised to 90 deg)

Result: status = xfoil_failure, same theta and iteration count as Test 2, reason = analyze_airfoil returned None.

Raising the cap let alpha_eff = 36.27 deg reach XFOIL, which failed to converge there. Confirms two things: the three-outcome bookkeeping distinguishes tool failure from physical divergence, and the validity cap does real protective work rather than duplicating the None check. Cap restored to 14 deg afterward.

### Test 4 - convergence history

theta_history_deg for the baseline case:
[0.0, 0.2765, 0.3192, 0.3255, 0.3268, 0.3271]

Successive step ratios (contraction factor G): 0.155, 0.146, 0.217, 0.200

The first two ratios sit on the predicted G = q/q_D = 85.28/587 = 0.145. The later ratios drift upward because the increments (0.0014 deg and smaller) fall to the same scale as the 3-decimal alpha rounding passed to XFOIL and XFOIL's own output precision. Conclusion for the sweep: compute G from the first two or three ratios only.

### q_D cross-check

- Analytical, using q_D = K_theta / (e * S * CL_alpha) with CL_alpha ~ 6.1/rad: q_D ~ 587 Pa, V_D ~ 31 m/s
- Empirical, from q/G at a single subcritical point: 550 to 584 Pa depending on which ratio is used

Agreement within a few percent from one subcritical run, which validates the extrapolation method before any sweep has been done.

### Open limitation - Reynolds consistency

The fixed Re = 200k input corresponds physically to V = 11.8 m/s. At the predicted V_D of ~31 m/s the true Re is ~525k, a factor of 2.6 higher. Every test above is therefore internally consistent only at the low-velocity end. The fixed-Re simplification is defensible because q_D depends on CL_alpha, which is the least Re-sensitive quantity in this regime, but the gap at V_D is larger than originally assumed and needs to be addressed rather than just documented. Options: run the sweep at a Re representative of the near-divergence regime (~500k), or compute Re from V at each step. Decide before the production sweep.

### Status

All three return paths verified. Arithmetic verified by hand. Contraction factor matches theory. Function is ready for the velocity sweep.