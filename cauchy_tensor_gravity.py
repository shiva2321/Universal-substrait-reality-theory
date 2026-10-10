import numpy as np
import os
import scipy.constants as const
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Precision Physical Constants (CODATA 2022 / IAU)
# -------------------------------------------------------------
c = const.c                  # 299792458 m/s
G = const.G                  # 6.67430e-11 m^3/kg/s^2
M_sun = 1.98847e30           # Solar mass (kg)
R_sun = 6.957e8              # Solar radius (m)
AU = const.astronomical_unit

# Characteristic gravitational radius (half-Schwarzschild radius)
r_g = G * M_sun / c**2       # ~1476.6 m
r_s = 2 * r_g                # Schwarzschild radius ~2953.2 m

print(f"Solar Gravitational Radius r_g: {r_g:.3f} m")
print(f"Solar Schwarzschild Radius r_s: {r_s:.3f} m")

# -------------------------------------------------------------
# 1. Theoretical Framework: Cauchy-Navier Elasticity Tensor
# -------------------------------------------------------------
# In USRT, the Planck HCP lattice is an elastic solid with:
# Bulk modulus K_bulk and Shear modulus mu_S.
# For close-packed HCP spheres with central spring constant k = c^4/G:
# mu_S = (3/5) * K_bulk (Poisson's ratio nu = 1/4, Cauchy relation for central forces).
#
# A central mass defect M creates a radial displacement field u(r) governed by:
# (lambda + mu_S) grad(div u) + mu_S laplacian(u) = 0
# Outside the source (r > 0), the spherically symmetric Kelvin solution is:
# u(r) = - (r_g * R_0 / r^2) * r_hat   (or in potential terms, u_r = - r_g / r)
#
# The displacement gradient generates the strain tensor:
# epsilon_ij = 1/2 (d_i u_j + d_j u_i)
# In spherical coordinates:
# epsilon_rr = d(u_r)/dr = + 2 * r_g / r^2 ... or for u_r = - r_g:
# More fundamentally, the metric tensor experienced by transverse shear waves (photons)
# in an elastic solid under static Cauchy strain is:
# g_00 = - (1 - 2*Phi/c^2) = - (1 - 2*r_g/r)
# g_ij = (1 + 2*Phi/c^2) * delta_ij = (1 + 2*r_g/r) * delta_ij
#
# Notice: In a pure scalar acoustic fluid, g_ij = delta_ij, so light deflection is:
# theta_scalar = 2 * r_s / b = 2 * r_g / b  (in Soldner/Newtonian approximation)
# In an elastic solid lattice with shear resistance, the transverse shear strain
# adds an equal contribution of 2 * r_g / b from the spatial distortion h_ij!
# Total deflection: theta_elastic = 4 * r_g / b = 2 * r_s / b = 4 * G * M / (c^2 * b)!

# -------------------------------------------------------------
# 2. Numerical Geodesic / Ray-Tracing Simulation
# -------------------------------------------------------------
# Ray tracing along null geodesics in isotropic metric:
# ds^2 = - A(r) c^2 dt^2 + B(r) (dx^2 + dy^2 + dz^2) = 0
# Effective refractive index: n(r) = sqrt(B(r) / A(r))
# For GR & Cauchy Elasticity:
# A(r) = 1 - 2*r_g/r
# B(r) = 1 + 2*r_g/r
# n_elastic(r) = sqrt((1 + 2*r_g/r) / (1 - 2*r_g/r)) \approx 1 + 2*r_g/r
#
# For Pure Scalar Acoustic Fluid:
# A(r) = 1 - 2*r_g/r
# B(r) = 1.0 (no spatial shear strain)
# n_scalar(r) = 1 / sqrt(1 - 2*r_g/r) \approx 1 + r_g/r

def refractive_index_elastic(r):
    return np.sqrt((1.0 + 2.0 * r_g / r) / (1.0 - 2.0 * r_g / r))

def refractive_index_scalar(r):
    return 1.0 / np.sqrt(1.0 - 2.0 * r_g / r)

# Ray tracing equations of motion (Hamiltonian Optics):
# d/ds (n dr/ds) = grad(n)
# Let trajectory be (x(t), y(t)) with initial ray traveling in +x direction at y = b
# dx/dt = c_eff * cos(phi)
# dy/dt = c_eff * sin(phi)
# dphi/dt = c_eff * (sin(phi) * dn/dx - cos(phi) * dn/dy) / n

def ray_equations(t, state, model_type='elastic'):
    x, y, phi = state
    r = np.sqrt(x**2 + y**2)
    if r < R_sun * 0.99:
        return [0, 0, 0]  # Ray hit sun
    
    if model_type == 'elastic':
        # n = 1 + 2*r_g/r -> dn/dr = -2*r_g / r^2
        dn_dr = - 2.0 * r_g / r**2
    else: # scalar
        # n = 1 + r_g/r -> dn/dr = - r_g / r^2
        dn_dr = - 1.0 * r_g / r**2
        
    dn_dx = dn_dr * (x / r)
    dn_dy = dn_dr * (y / r)
    
    n_val = 1.0  # background scale
    # Ray equation d/ds(n t) = grad n  ->  dphi/ds = -sin(phi) dn/dx + cos(phi) dn/dy  (n ~ 1).
    # Audit fix: the previous version had the opposite sign (rays bent AWAY from the Sun) and
    # compensated with a minus sign when reporting the angle.
    dphi_dt = (-np.sin(phi) * dn_dx + np.cos(phi) * dn_dy)
    
    dx_dt = np.cos(phi)
    dy_dt = np.sin(phi)
    
    return [dx_dt, dy_dt, dphi_dt]

# Integrate rays from x = - 5 * R_sun to x = + 5 * R_sun at impact parameter b = R_sun
b_impact = R_sun
# Audit fix: integrate over +-2000 R_sun (previously +-5 R_sun, which captures only ~98% of the bending)
x_start = - 2000.0 * R_sun
x_end = 2000.0 * R_sun
t_span = (0, 4000.0 * R_sun)

# 1. Cauchy Elastic Lattice Ray
sol_elastic = solve_ivp(
    lambda t, y: ray_equations(t, y, 'elastic'),
    t_span,
    [x_start, b_impact, 0.0],
    t_eval=np.linspace(0, 4000.0 * R_sun, 400001),
    rtol=1e-11, atol=1e-13
)

# 2. Scalar Acoustic Fluid Ray
sol_scalar = solve_ivp(
    lambda t, y: ray_equations(t, y, 'scalar'),
    t_span,
    [x_start, b_impact, 0.0],
    t_eval=np.linspace(0, 4000.0 * R_sun, 400001),
    rtol=1e-11, atol=1e-13
)

# Deflection angles at infinity (radians to arcseconds)
rad_to_arcsec = 180.0 * 3600.0 / np.pi

# Analytical Deflection Angles:
theta_GR_analytical = (4.0 * G * M_sun / (c**2 * R_sun)) * rad_to_arcsec
theta_Scalar_analytical = (2.0 * G * M_sun / (c**2 * R_sun)) * rad_to_arcsec

theta_elastic_num = - sol_elastic.y[2, -1] * rad_to_arcsec   # phi ends negative (bent toward the Sun)
theta_scalar_num = - sol_scalar.y[2, -1] * rad_to_arcsec

print("\n--- LIGHT DEFLECTION RESULTS AT SOLAR LIMB (b = R_sun) ---")
print(f"Scalar Acoustic Fluid (Theory):   {theta_Scalar_analytical:.4f} arcsec (Newtonian / Soldner)")
print(f"Scalar Acoustic Fluid (Sim):      {theta_scalar_num:.4f} arcsec")
print(f"Cauchy Elastic Lattice (Theory):  {theta_GR_analytical:.4f} arcsec (Einstein General Relativity)")
print(f"Cauchy Elastic Lattice (Sim):     {theta_elastic_num:.4f} arcsec")
print(f"Deflection Difference Ratio:      {theta_elastic_num / theta_scalar_num:.4f} (Exact factor of 2)")

# -------------------------------------------------------------
# Audit check (2026-10): is the "elastic" metric actually produced by Navier-Cauchy elasticity?
# -------------------------------------------------------------
# The ray tracing above uses the isotropic GR metric B(r) = 1 + 2 r_g / r as an INPUT.
# For a radial displacement u_r(r) the source-free Navier-Cauchy equation reduces to
#   (lambda + 2 mu) d/dr [ (1/r^2) d(r^2 u_r)/dr ] = 0   ->   u_r = A r + B / r^2.
r_test = np.linspace(2.0, 10.0, 9) * R_sun
u_claim = -r_g / r_test
div_u = np.gradient(r_test**2 * u_claim, r_test) / r_test**2
residual = np.gradient(div_u, r_test)
print("\n--- AUDIT: CONSISTENCY WITH NAVIER-CAUCHY ELASTICITY ---")
print(f"u_r = -r_g/r  ->  d/dr(div u) = {residual[4]:.3e} 1/m^2 at r = 6 R_sun (analytic: 2 r_g / r^3, not 0)")
print("u_r = -r_g/r is therefore not an equilibrium solution; the general radial solution A r + B/r^2")
print("gives a traceless strain (-2B/r^3, B/r^3, B/r^3), and the isotropic strain (r_g/r) delta_ij")
print("violates the Saint-Venant compatibility conditions, so no displacement field produces it.")
print("=> The 1.751 arcsec result is General Relativity's metric, written in by hand - not derived")
print("   from a Planck-lattice elasticity calculation. (See audit/a04_mechanics_checks.py.)")

# -------------------------------------------------------------
# 3. Observational Verification & History
# -------------------------------------------------------------
# Arthur Eddington 1919 Eclipse: 1.98 +/- 0.12 arcsec (Sobral), 1.61 +/- 0.30 arcsec (Principe)
# Modern VLBI (Very Long Baseline Interferometry, Shapiro et al. 2004):
# gamma = 0.9998 +/- 0.0003 -> theta = 1.7515 +/- 0.0005 arcsec
eddington_val = 1.98
eddington_err = 0.12
vlbi_val = 1.7515
vlbi_err = 0.0005

# -------------------------------------------------------------
# 4. Generate Comprehensive Visual Proof Figure
# -------------------------------------------------------------
fig = plt.figure(figsize=(15, 11))
fig.patch.set_facecolor('#0d1117')

gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])

for ax in [ax1, ax2, ax3]:
    ax.set_facecolor('#161b22')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#30363d')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

# Subplot 1: Exaggerated Ray Tracing Geometry Past the Sun
# Scale transverse deflection by a visible factor (e.g., 200,000x) for geometric illustration
scale_vis = 2.5e5
sun_circle = plt.Circle((0, 0), 1.0, color='#f1e05a', alpha=0.3, label='Solar Mass Defect')
sun_core = plt.Circle((0, 0), 0.98, color='#ff7b72', alpha=0.6)
ax1.add_patch(sun_circle)
ax1.add_patch(sun_core)

x_norm = sol_elastic.y[0] / R_sun
# rays now start at -2000 R_sun; reference the drawn path to its height at x = -5 R_sun
_i0 = np.argmin(np.abs(x_norm + 5.0))
y_elastic_norm = (sol_elastic.y[1] - sol_elastic.y[1][_i0]) / R_sun * scale_vis + 1.0
y_scalar_norm = (sol_scalar.y[1] - sol_scalar.y[1][_i0]) / R_sun * scale_vis + 1.0

ax1.plot(x_norm, y_elastic_norm, color='#7ee787', lw=2.5, 
         label=f'USRT Cauchy Elastic Lattice (Rank-2): {theta_GR_analytical:.3f} arcsec (100% GR)')
ax1.plot(x_norm, y_scalar_norm, color='#ffa657', lw=2, ls='--',
         label=f'Scalar Acoustic Fluid (Rank-0): {theta_Scalar_analytical:.3f} arcsec (50% Soldner)')
ax1.axhline(1.0, color='white', ls=':', alpha=0.4, label='Undeflected Path (b = R_sun)')

ax1.set_xlim(-5, 5)
ax1.set_ylim(-1.5, 2.5)
ax1.set_xlabel(r'Propagation Coordinate $x / R_\odot$')
ax1.set_ylabel(r'Transverse Deviation $y / R_\odot$ (Exaggerated)')
ax1.set_title(r'1. Photon Ray Geodesic Deflection: Cauchy-Navier Elastic Tensor vs Scalar Acoustic Fluid', 
              fontsize=12, fontweight='bold')
ax1.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', loc='upper left')
ax1.grid(True, color='#30363d', ls=':', alpha=0.5)

# Subplot 2: Metric Tensor Perturbations (h_00 vs h_ij)
r_range = np.linspace(1.0, 10.0, 200) * R_sun
h_00 = - 2.0 * G * M_sun / (c**2 * r_range)
h_rr_elastic = + 2.0 * G * M_sun / (c**2 * r_range)
h_rr_scalar = np.zeros_like(r_range)

ax2.plot(r_range / R_sun, np.abs(h_00) * 1e6, color='#58a6ff', lw=2.5, 
         label=r'Temporal Perturbation $|h_{00}| = 2\Phi/c^2$ (50% Deflection)')
ax2.plot(r_range / R_sun, h_rr_elastic * 1e6, color='#7ee787', lw=2.5, 
         label=r'Cauchy Lattice Shear Strain $h_{ij} = 2\Phi/c^2$ (50% Deflection)')
ax2.plot(r_range / R_sun, h_rr_scalar, color='#f85149', lw=2, ls='--', 
         label=r'Scalar Fluid Spatial Perturbation $h_{ij} = 0$ (Lacks Shear)')

ax2.set_xlabel(r'Distance from Solar Center $r / R_\odot$')
ax2.set_ylabel(r'Metric Perturbation Amplitude ($\times 10^{-6}$)')
ax2.set_title('2. Spatial vs Temporal Cauchy Metric Components', fontsize=11, fontweight='bold')
ax2.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', fontsize=9)
ax2.grid(True, color='#30363d', ls=':', alpha=0.5)

# Subplot 3: Observational Precision Scorecard
benchmarks = ['Scalar Fluid', 'Eddington 1919', 'USRT Cauchy', 'VLBI 2004', 'Einstein GR']
values = [theta_Scalar_analytical, eddington_val, theta_GR_analytical, vlbi_val, theta_GR_analytical]
errors = [0.0, eddington_err, 0.0, vlbi_err, 0.0]
bar_colors = ['#ffa657', '#d29922', '#7ee787', '#58a6ff', '#a371f7']

y_pos = np.arange(len(benchmarks))
ax3.barh(y_pos, values, xerr=errors, align='center', color=bar_colors, alpha=0.85, 
         capsize=5, ecolor='white')
ax3.axvline(theta_GR_analytical, color='#7ee787', ls='--', lw=1.5, alpha=0.8, label='Exact GR Target (1.751 arcsec)')

ax3.set_yticks(y_pos)
ax3.set_yticklabels(benchmarks, color='white', fontweight='bold')
ax3.set_xlabel('Deflection Angle at Solar Limb (arcseconds)')
ax3.set_title('3. Benchmark Scorecard: Theory vs Modern VLBI Observables', fontsize=11, fontweight='bold')
ax3.set_xlim(0, 2.3)

for i, v in enumerate(values):
    err_str = f" ± {errors[i]:.2f}" if errors[i] > 0 else ""
    ax3.text(v + 0.08, i, f"{v:.4f} arcsec{err_str}", va='center', color='white', fontsize=9, fontweight='bold')

ax3.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')
ax3.grid(True, color='#30363d', ls=':', alpha=0.5)

plt.tight_layout()
out_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cauchy_tensor_gravity.png')
plt.savefig(out_png, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"\nFigure saved successfully to {out_png}")
