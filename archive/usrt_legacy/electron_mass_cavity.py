"""
Simulation and Mathematical Proof: The Electron as a Circulating Trapped Wave Cavity.
Evaluates:
1. Circulating Wave (Zitterbewegung / Williamson-van der Mark Soliton):
   A massless transverse shear wave (photon-like ripple) circulating at speed c
   in a closed loop of radius r_C = hbar / (m_e * c) = 3.86e-13 m.
2. Exact Derivation of:
   - Rest Mass: E = hbar * omega = m_e * c^2 = 0.511 MeV.
   - Quantum Spin: S = r_C * (E / c) = hbar / 2.
   - Magnetic Moment: mu = I * Area = e * hbar / (2 * m_e) = mu_B (Bohr Magneton).
3. Self-Induced Substrate Cavity Profile keeping the wave trapped.

AUDIT NOTE (see audit/USRT_AUDIT_REPORT.md):
   r_C is defined from the measured m_e, so E = m_e c^2 and mu = mu_B are
   identities, not derivations. The angular momentum actually computed is
   L = r_C E / c = hbar (spin 1); the factor 1/2 was typed in. With L = hbar
   the g-factor is 1, not the measured 2.0023. The cavity profile in panel 2
   is a hand-drawn Gaussian, not a solved field equation.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def calculate_electron_soliton():
    print("Calculating electron circulating wave parameters...")
    
    # Fundamental constants
    c = 2.99792458e8     # m/s
    hbar = 1.054571817e-34 # J*s
    e_charge = 1.602176634e-19 # C
    m_e = 9.1093837e-31  # kg
    eV = 1.602176634e-19 # J
    
    # 1. Compton wavelength and reduced radius
    lambda_C = (2.0 * np.pi * hbar) / (m_e * c) # 2.426e-12 m
    r_C = hbar / (m_e * c)                       # 3.86159e-13 m (Reduced Compton radius)
    
    # 2. Circulation frequency (Zitterbewegung frequency)
    omega_Z = c / r_C                           # 7.76344e20 rad/s
    nu_Z = omega_Z / (2.0 * np.pi)              # 1.23559e20 Hz
    
    # 3. Trapped wave energy (Rest Mass)
    E_joules = hbar * omega_Z                   # 8.1871e-14 J
    E_MeV = (E_joules / eV) / 1e6               # 0.5109989 MeV
    
    # 4. Angular momentum of the circulating wave
    # AUDIT: computed honestly, L = r_C * p = r_C * (E / c) = hbar (spin-1, not 1/2).
    # The original code then *assigned* S = hbar/2 by hand ("double cover");
    # nothing in this loop model produces the factor 1/2.
    L_orbital = r_C * (E_joules / c)
    S_spin = L_orbital
    
    # 5. Effective current and magnetic moment
    # Current I = e * nu_Z
    I_current = e_charge * nu_Z
    # Area = pi * r_C^2
    Area = np.pi * (r_C**2)
    # Magnetic dipole moment mu = I * Area
    mu_calc = I_current * Area                  # 9.2740e-24 J/T
    mu_Bohr = (e_charge * hbar) / (2.0 * m_e)   # 9.2740e-24 J/T
    # AUDIT: mu = I*A = e c r_C / 2 = e hbar / (2 m_e) is an identity once
    # r_C = hbar/(m_e c) is chosen; it is not a prediction. The physical
    # check is the g-factor: g = 2 m_e mu / (e L). With L = hbar this gives
    # g = 1, whereas the measured electron has g = 2.00231930436.
    g_factor = 2.0 * m_e * mu_calc / (e_charge * L_orbital)
    print(f"  L = r_C * E / c          = {L_orbital/hbar:.6f} hbar  (code previously asserted hbar/2)")
    print(f"  mu = I * A               = {mu_calc/mu_Bohr:.6f} mu_B (identity given r_C = hbar/m_e c)")
    print(f"  g = 2 m_e mu / (e L)     = {g_factor:.6f}   (measured g_e = 2.00231930436)")
    print("  AUDIT: the circulating-loop picture is the Williamson-van der Mark / Hestenes")
    print("  zitterbewegung model (prior art). As coded it gives spin 1 and g = 1, not 1/2 and 2.")

    return {
        "lambda_C": lambda_C,
        "r_C": r_C,
        "omega_Z": omega_Z,
        "nu_Z": nu_Z,
        "E_MeV": E_MeV,
        "S_spin": S_spin,
        "mu_calc": mu_calc,
        "mu_Bohr": mu_Bohr,
        "g_factor": g_factor,
        "hbar": hbar
    }

def simulate_electron_cavity_profile(r_C):
    print("Simulating self-induced substrate cavity of the electron...")
    # Radial coordinate in units of r_C
    r = np.linspace(0.01, 6.0, 300)
    
    # Circulating toroidal current density: peak at r = r_C
    sigma = 0.4
    rho_wave = np.exp(-((r - 1.0)**2) / (2.0 * sigma**2)) / (r * np.sqrt(2 * np.pi) * sigma)
    rho_wave /= np.max(rho_wave)
    
    # Self-induced substrate depletion (cavity well)
    # The radiation pressure of the light-speed wave displaces the substrate fluid:
    delta_rho_sub = - 0.65 * np.exp(-((r - 1.0)**2) / (2.0 * (sigma * 1.5)**2))
    rho_substrate = 1.0 + delta_rho_sub
    
    # Effective potential confining the wave
    V_confine = delta_rho_sub * 2.5
    
    return r, rho_wave, rho_substrate, V_confine

def plot_electron_mass_cavity(p, r, rho_wave, rho_sub, V_conf):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: The Circulating Trapped Wave Trajectory
    theta = np.linspace(0, 2 * np.pi, 200)
    x_circ = np.cos(theta)
    y_circ = np.sin(theta)
    axs[0, 0].plot(x_circ, y_circ, 'r-', lw=3, label=r'Trapped Light Wave Orbit ($v = c$)')
    axs[0, 0].plot(0, 0, 'ko', markersize=8, label=r'Center of Mass ($v = 0$, Rest Mass $m_e$)')
    # Draw velocity arrows along circle
    for t_val in [0, np.pi/2, np.pi, 3*np.pi/2]:
        px, py = np.cos(t_val), np.sin(t_val)
        vx, vy = -np.sin(t_val) * 0.3, np.cos(t_val) * 0.3
        axs[0, 0].arrow(px, py, vx, vy, head_width=0.08, head_length=0.08, fc='red', ec='red')
        
    axs[0, 0].set_aspect('equal')
    axs[0, 0].set_xlim(-1.6, 1.6)
    axs[0, 0].set_ylim(-1.6, 1.6)
    axs[0, 0].set_xlabel(r'Spatial Coordinate $x / r_C$', fontsize=12)
    axs[0, 0].set_ylabel(r'Spatial Coordinate $y / r_C$', fontsize=12)
    axs[0, 0].set_title(r'1. The Electron: Light Ripple Trapped in a Loop ($r_C = 3.86 \times 10^{-13}\,\mathrm{m}$)', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='upper right', frameon=True)
    axs[0, 0].text(0, -1.35, r"Circulation speed: $v = c$" + "\n" + r"Center-of-mass: $v = 0 \rightarrow m_e = E_{\mathrm{trapped}} / c^2 = 0.511\,\mathrm{MeV}$",
                   ha='center', fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="#ffeaa7", ec="#fdcb6e"))
    
    # Subplot 2: Self-Induced Substrate Cavity Profile
    axs[0, 1].plot(r, rho_sub, 'b-', lw=2.5, label=r'Substrate Density $\rho(r)/\rho_0$')
    axs[0, 1].plot(r, rho_wave, 'r--', lw=2.0, label='Circulating Wave Energy Density')
    axs[0, 1].axhline(1.0, color='gray', linestyle=':', label='Unperturbed Vacuum Background')
    axs[0, 1].fill_between(r, rho_sub, 1.0, color='blue', alpha=0.15, label='Self-Induced Cavity Well')
    axs[0, 1].set_xlabel(r'Radial Distance $r / r_C$', fontsize=12)
    axs[0, 1].set_ylabel('Normalized Density', fontsize=12)
    axs[0, 1].set_title('2. The Electron’s Self-Induced Cavity Well', fontsize=13, fontweight='bold')
    axs[0, 1].legend(loc='lower right', frameon=True)
    axs[0, 1].set_ylim(0.2, 1.2)
    
    # Subplot 3: Derivation Ledger & Exact Match with Nature
    axs[1, 0].axis('off')
    ledger_text = (
        "=== LOOP-ELECTRON LEDGER (AUDITED) ===\n\n"
        f"1. INPUT RADIUS:  r_C = hbar / (m_e * c) = {p['r_C']*1e13:.3f} x 10^-13 m\n"
        "   (m_e is an INPUT here; everything below is an identity)\n"
        f"2. LOOP FREQUENCY: nu = c / (2*pi*r_C)   = {p['nu_Z']*1e-20:.4f} x 10^20 Hz\n"
        f"3. LOOP ENERGY:    E = hbar*omega        = {p['E_MeV']:.4f} MeV (= m_e c^2 by construction)\n\n"
        "4. ANGULAR MOMENTUM (computed):\n"
        f"   L = r_C * (E / c) = {p['S_spin']/p['hbar']:.3f} hbar   -> spin 1, NOT 1/2\n"
        "   (the original ledger inserted a factor 1/2 by hand)\n\n"
        "5. MAGNETIC MOMENT:\n"
        f"   mu = I * Area = {p['mu_calc']:.4e} J/T = mu_B (identity)\n"
        f"   g = 2 m_e mu / (e L) = {p['g_factor']:.3f}   vs measured 2.0023\n"
        "   => model FAILS the g-factor test (prior art: Williamson-\n"
        "      van der Mark 1997, Hestenes zitterbewegung)"
    )
    axs[1, 0].text(0.02, 0.98, ledger_text, va='top', ha='left', family='monospace', fontsize=10.0,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#bdc3c7", lw=1.5))
    
    # Subplot 4: Summary Table
    axs[1, 1].axis('off')
    summary_text = (
        "=== THE TRAPPED-WAVE PICTURE (CONJECTURE) ===\n\n"
        "1. THE IDEA (sound part: Einstein-box inertia):\n"
        "   Any confined energy E has inertia E/c^2. A ripple\n"
        "   trapped in a cavity therefore has rest mass.\n"
        "   (Open: why E = 0.511 MeV, and spin 1/2 / g = 2.)\n\n"
        "2. HOW IT IS TRAPPED:\n"
        "   - A free light ripple travels in a straight line at c.\n"
        "     Because it moves at c, it has NO rest mass (m = 0).\n"
        "   - When the ripple twists into a circular topological knot\n"
        "     (Zitterbewegung / toroidal vortex), it travels in a circle\n"
        "     at c, but its center-of-mass is STATIONARY (v_cm = 0)!\n\n"
        "3. THE ORIGIN OF MASS (E = mc^2):\n"
        "   - Because the ripple's energy is trapped in one location,\n"
        "     trying to push the electron requires pushing the trapped\n"
        "     wave energy against the substrate.\n"
        "   - That trapped energy manifests macroscopically as INERTIA:\n"
        "     m_e = E_trapped / c^2 = 0.511 MeV.\n\n"
        "4. THE SELF-CONTAINED CAVITY:\n"
        "   - The circulating wave pushes the substrate fluid outward,\n"
        "     carving its own microscopic density cavity well.\n"
        "   - The wave is trapped inside the very hole it carves!"
    )
    axs[1, 1].text(0.02, 0.98, summary_text, va='top', ha='left', family='monospace', fontsize=10.0,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#e8f8f5", ec="#1abc9c", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'electron_mass_cavity.png')
    plt.savefig(output_path, dpi=300)
    print(f"Electron mass cavity plots saved to: {output_path}")

if __name__ == "__main__":
    params = calculate_electron_soliton()
    r, rho_wave, rho_sub, V_conf = simulate_electron_cavity_profile(params["r_C"])
    plot_electron_mass_cavity(params, r, rho_wave, rho_sub, V_conf)
