"""Velocity sweep for the aeroelastic divergence model.
Sweeps V, records equilibrium twist, brackets q_D, and cross-checks
against the G-extrapolation from subcritical convergence rates."""

import math
from divergence_model import find_equilibrium_twist

# ---- Reynolds decision ----
# 'fixed': one Re for the whole sweep (simpler; Re set near the divergence
#          regime ~500k since that's the condition q_D actually describes).
# 'computed': Re = rho*V*c/mu recomputed each step (internally consistent,
#          but every velocity hits different XFOIL runs).
RE_MODE = 'fixed'
RE_FIXED = 500000
MU = 1.81e-5

def reynolds_for(V, c, rho):
    if RE_MODE == 'computed':
        return int(rho * V * c / MU)
    return RE_FIXED

def run_sweep(naca='2412', alpha_0=2.0, K_theta=45.0, e=0.05, c=0.25,
              rho=1.225, span=1.0, V_min=5.0, V_max=40.0, V_step=1.0,
              max_iter=300):

    results = []
    V = V_min
    while V <= V_max + 1e-9:
        Re = reynolds_for(V, c, rho)
        r = find_equilibrium_twist(
            naca=naca, reynolds=Re, alpha_0=alpha_0, K_theta=K_theta,
            e=e, c=c, rho=rho, V=V, span=span, max_iter=max_iter
        )
        results.append({
            'V': V,
            'q': r['q'],
            'Re': Re,
            'status': r['status'],
            'theta_deg': r.get('theta_deg'),
            'iterations': r['iterations'],
            'reason': r.get('reason', ''),
            'history': r.get('theta_history_deg', []),
        })
        print(f"V={V:5.1f}  q={r['q']:7.1f}  Re={Re:7d}  "
              f"{r['status']:14s}  theta={r.get('theta_deg', float('nan')):7.3f}  "
              f"a_eff={(alpha_0 + r.get('theta_deg', float('nan'))):6.2f}  "
              f"iters={r['iterations']}")
        V += V_step
    return results


def analyze_sweep(results):
    conv = [p for p in results if p['status'] == 'converged']
    div  = [p for p in results if p['status'] == 'diverged']
    fail = [p for p in results if p['status'] == 'xfoil_failure']

    print("\n" + "=" * 50)
    print(f"converged: {len(conv)}   diverged: {len(div)}   "
          f"xfoil_failure: {len(fail)}")

    # --- Bracket the flip (converged -> diverged), skipping failures ---
    last_conv = max((p['V'] for p in conv), default=None)
    first_div = min((p['V'] for p in div), default=None)
    if last_conv is not None and first_div is not None:
        q_last = 0.5 * 1.225 * last_conv**2
        q_first = 0.5 * 1.225 * first_div**2
        print(f"\nBracket: q_D between {q_last:.0f} Pa (V={last_conv}) "
              f"and {q_first:.0f} Pa (V={first_div})")

    # --- G-extrapolation from the lowest few converged points ---
    print("\nG-extrapolation (subcritical points only):")
    G_points = []
    for p in sorted(conv, key=lambda x: x['V'])[:5]:
        h = p['history']
        if len(h) >= 4:
            d1, d2 = h[1] - h[0], h[2] - h[1]
            if abs(d1) > 1e-9:
                G = abs(d2 / d1)
                q_D_est = p['q'] / G if G > 0 else float('nan')
                G_points.append((p['q'], G, q_D_est))
                print(f"  V={p['V']:4.1f}  q={p['q']:6.1f}  G={G:.4f}  "
                      f"-> q_D~{q_D_est:.0f} Pa  (V_D~{math.sqrt(2*q_D_est/1.225):.1f} m/s)")

    if fail:
        print("\nWARNING - xfoil_failure points (NOT divergence):")
        for p in fail:
            print(f"  V={p['V']}  alpha ran past XFOIL's range - {p['reason']}")

    return {'last_converged_V': last_conv, 'first_diverged_V': first_div,
            'G_points': G_points, 'n_failures': len(fail)}


if __name__ == '__main__':
    results = run_sweep(alpha_0=0.0)
    summary = analyze_sweep(results)