from divergence_model import find_equilibrium_twist

result = find_equilibrium_twist(
    naca='2412', reynolds=200000, alpha_0=2.0,
    K_theta=45.0,   # N*m/rad
    e=0.05,         # m
    c=0.25,         # m
    rho=1.225,      # kg/m^3
    V=11.8          # m/s — matches Re=200k at c=0.25 (was 15.0, which is Re~254k)
)
print(result)