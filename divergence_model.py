import math
from xfoil_single import analyze_airfoil

def find_equilibrium_twist(naca, reynolds, alpha_0, K_theta, e, c, rho, V, span=1.0, tolerance_deg=0.001, max_iter=300, alpha_cap_deg=14.0):
    """Iterate to the equilibrium twist angle for one flight condition.

    Angles in degrees at the interface, radians internally.
    K_theta in N*m/rad, e and c in m, rho in kg/m^3, V in m/s.

    Returns a dict with 'status' in {'converged', 'diverged', 'xfoil_failure'}.
    """

    S = c * span                                    #Section reference area (unit span by default)
    q = 0.5 * rho * V**2                            #Dynamic pressure, constant through the loop
    tolerance = math.radians(tolerance_deg)

    theta = 0.0                                     #Initial guess: untwisted, radians
    theta_history = [0.0]                           #Track twist per iteration for G-ratio extraction

    for i in range(1, max_iter + 1):

        alpha_eff_deg = alpha_0 + math.degrees(theta)

        # Validity cap checked BEFORE calling XFOIL - it converges to garbage past ~20 deg
        if abs(alpha_eff_deg) > alpha_cap_deg:
            return {
                'status': 'diverged',
                'theta_deg': math.degrees(theta),
                'alpha_eff_deg': alpha_eff_deg,
                'iterations': i,
                'q': q,
                'reason': f'alpha_eff exceeded validity cap of {alpha_cap_deg} deg',
                'theta_history_deg': [math.degrees(t) for t in theta_history],
            }

        CL, CM = analyze_airfoil(naca, reynolds, round(alpha_eff_deg, 3))

        if CL is None:
            return {
                'status': 'xfoil_failure',
                'theta_deg': math.degrees(theta),
                'alpha_eff_deg': alpha_eff_deg,
                'iterations': i,
                'q': q,
                'reason': 'analyze_airfoil returned None - solver failure, not physics',
                'theta_history_deg': [math.degrees(t) for t in theta_history],
            }

        M_aero = q * S * CL * e + q * S * c * CM     #Moment about the elastic axis
        theta_new = M_aero / K_theta                 #Twist the spring permits, radians
        theta_history.append(theta_new)

        if abs(theta_new - theta) < tolerance:
            return {
                'status': 'converged',
                'theta_deg': math.degrees(theta_new),
                'alpha_eff_deg': alpha_0 + math.degrees(theta_new),
                'iterations': i,
                'q': q,
                'CL': CL,
                'CM': CM,
                'theta_history_deg': [math.degrees(t) for t in theta_history],
            }

        theta = theta_new

    return {
        'status': 'diverged',
        'theta_deg': math.degrees(theta),
        'alpha_eff_deg': alpha_0 + math.degrees(theta),
        'iterations': max_iter,
        'q': q,
        'reason': f'no convergence in {max_iter} iterations',
        'theta_history_deg': [math.degrees(t) for t in theta_history],
    }