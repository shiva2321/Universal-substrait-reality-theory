"""
Foundational Substrate Physics: Microscopic Origin of Spacetime.
Computes, for a close-packed (FCC, Z = 12) lattice of Planck-mass particles bound by a
Lennard-Jones potential V(r) = V0 [(a0/r)^12 - 2 (a0/r)^6]:
1. The bond stiffness k0 = 72 V0 / a0^2 and the compression/tension asymmetry.
2. Cauchy-Born elastic constants C11, C12, C44 (corrected: C11 = sqrt2 k/a, C12 = C44 = k/(sqrt2 a)).
3. The calibration of V0 that makes the Voigt-averaged shear speed equal to c
   (NOTE: this uses the measured c as an input; M0 = m_P and a0 = l_P also contain c).
4. Direction-dependent sound speeds (the lattice is elastically anisotropic).
5. The longitudinal phonon branch: its band MAXIMUM, and the fact that it has no gap.
6. The de Boer parameter, which equals sqrt(calibration constant) identically.

Audit note (2026-10): earlier versions of this script used C11 = 2 sqrt2 k/a and
mu = k/(5 sqrt2 a) (both wrong), hence the calibration constant 7.2 instead of 28.8, and
described the band maximum hbar*omega_max as an "energy gap". See audit/USRT_AUDIT_REPORT.md.
"""

import os

import numpy as np
import scipy.constants as const
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

def analyze_foundational_substrate():
    print("=" * 80)
    print("STEP 1: MICROSCOPIC PARAMETERS (Planck units - these already contain c, hbar and G)")
    print("=" * 80)

    hbar = const.hbar
    c_measured = const.c

    # M_0 = sqrt(hbar c / G) and a_0 = sqrt(hbar G / c^3): the speed of light is an INPUT here.
    M_0 = np.sqrt(hbar * const.c / const.G)
    a_0 = np.sqrt(hbar * const.G / const.c**3)

    # Cauchy-Born for an FCC nearest-neighbour central-spring lattice (bond stiffness k):
    #   C11 = sqrt(2) k/a,  C12 = C44 = k/(sqrt(2) a)
    #   Voigt shear modulus mu_V = (C11 - C12 + 3 C44)/5 = (2 sqrt2 / 5) k/a
    #   rho_0 = sqrt(2) M_0 / a_0^3,  k = 72 V_0 / a_0^2  (Lennard-Jones, see Step 2)
    #   => mu_V / rho_0 = (2/5) * 72 * V_0/M_0 = 28.8 V_0 / M_0
    # Requiring the average shear speed to equal the measured c FIXES V_0 (a calibration, not a prediction):
    calibration_constant = 0.4 * 72.0  # 28.8 (the original script used 7.2 because of the C_ij error)
    V_0 = (M_0 * c_measured**2) / calibration_constant

    print(f"Constituent Mass M_0 = m_P:       {M_0:.6e} kg   (contains c)")
    print(f"Equilibrium Spacing a_0 = l_P:    {a_0:.6e} m    (contains c)")
    print(f"Well depth V_0 = M_0 c^2 / {calibration_constant:.1f}:  {V_0:.6e} J  (calibrated with the MEASURED c)")

    # -------------------------------------------------------------------------
    # STEP 2: ASYMMETRIC MICROSCOPIC POTENTIAL V(r)
    # -------------------------------------------------------------------------
    # In any real physical medium, inter-particle interactions follow an
    # asymmetric anharmonic potential (e.g., Mie/Lennard-Jones potential):
    # V(r) = V_0 * [ (a_0 / r)^12 - 2 * (a_0 / r)^6 ]
    #
    # At r = a_0:
    # V(a_0) = - V_0 (minimum, equilibrium)
    # dV/dr |_{a_0} = 0
    # d^2V/dr^2 |_{a_0} = k_0 (bond spring constant)
    
    r_norm = np.linspace(0.82, 1.6, 500) # r / a_0
    r_actual = r_norm * a_0
    
    # Dimensionless Lennard-Jones potential
    V_norm = (1.0 / (r_norm**12)) - 2.0 * (1.0 / (r_norm**6))
    V_actual = V_0 * V_norm
    
    # Force F(r) = - dV/dr:
    # dV/dr = V_0/a_0 * [ -12 (a_0/r)^13 + 12 (a_0/r)^7 ] = 12 * (V_0/a_0) * [ (a_0/r)^7 - (a_0/r)^13 ]
    F_norm = 12.0 * ((1.0 / (r_norm**7)) - (1.0 / (r_norm**13)))
    F_actual = (V_0 / a_0) * F_norm
    
    # Second derivative at equilibrium r = a_0:
    # d^2V/dr^2 |_{a_0} = V_0 / a_0^2 * [ 12*13 - 12*7 ] = 72 * (V_0 / a_0^2)
    k_0 = 72.0 * (V_0 / (a_0**2))
    
    print("\n--- NON-LINEAR ANHARMONICITY & ASYMMETRY ---")
    print(f"Equilibrium Bond Stiffness k_0:   {k_0:.6e} N/m")
    
    # Test asymmetry: Compressing by 10% vs Stretching by 10%
    # r = 0.9 * a_0 (Compression):
    V_compress_10 = V_0 * ((1.0 / (0.9**12)) - 2.0 * (1.0 / (0.9**6)))
    # r = 1.1 * a_0 (Stretching):
    V_stretch_10 = V_0 * ((1.0 / (1.1**12)) - 2.0 * (1.0 / (1.1**6)))
    
    energy_ratio_asymmetry = (V_compress_10 - (-V_0)) / (V_stretch_10 - (-V_0))
    print(f"Energy to compress by 10%:        {(V_compress_10 + V_0):.4e} J")
    print(f"Energy to stretch by 10%:         {(V_stretch_10 + V_0):.4e} J")
    print(f"Asymmetry Factor (Compression/Tension): {energy_ratio_asymmetry:.2f}x harder to compress!")
    
    # -------------------------------------------------------------------------
    # STEP 3: CAUCHY-BORN LATTICE ELASTICITY & EMERGENT LIGHT SPEED
    # -------------------------------------------------------------------------
    # In an HCP/FCC close-packed crystal with 12 nearest neighbors (Z = 12):
    # Packing fraction eta = pi / (3 * sqrt(2)) = 0.74048
    # Effective volume per particle V_cell = a_0^3 / sqrt(2)
    V_cell = (a_0**3) / np.sqrt(2.0)
    
    # 1. Macroscopic Substrate Density:
    rho_0 = M_0 / V_cell
    
    # 2. Cauchy-Born elastic constants (FCC, nearest-neighbour central springs):
    C11 = np.sqrt(2.0) * k_0 / a_0
    C12 = k_0 / (np.sqrt(2.0) * a_0)
    C44 = C12
    mu_0 = (C11 - C12 + 3.0 * C44) / 5.0          # Voigt-averaged shear modulus
    K_bulk = (C11 + 2.0 * C12) / 3.0              # bulk modulus

    # 3. Voigt-averaged ("isotropic") speeds:
    c_transverse = np.sqrt(mu_0 / rho_0)
    c_longitudinal = np.sqrt((K_bulk + (4.0/3.0) * mu_0) / rho_0)

    # 4. The real crystal is anisotropic (Zener ratio 2 C44/(C11-C12) = 2): speeds by direction
    speeds = {
        "[100]": (np.sqrt(C44 / rho_0), np.sqrt(C44 / rho_0), np.sqrt(C11 / rho_0)),
        "[110]": (np.sqrt((C11 - C12) / (2 * rho_0)), np.sqrt(C44 / rho_0),
                  np.sqrt((C11 + C12 + 2 * C44) / (2 * rho_0))),
        "[111]": (np.sqrt((C11 - C12 + C44) / (3 * rho_0)), np.sqrt((C11 - C12 + C44) / (3 * rho_0)),
                  np.sqrt((C11 + 2 * C12 + 4 * C44) / (3 * rho_0))),
    }

    print("\n--- ELASTIC CONSTANTS AND SOUND SPEEDS (corrected Cauchy-Born) ---")
    print(f"Substrate Equilibrium Density rho_0:  {rho_0:.6e} kg/m^3")
    print(f"C11, C12 = C44:                       {C11:.4e}, {C12:.4e} Pa")
    print(f"Voigt Shear Modulus mu_0:             {mu_0:.6e} Pa")
    print(f"Bulk Modulus K_bulk:                  {K_bulk:.6e} Pa")
    print(f"Zener anisotropy 2C44/(C11-C12):      {2 * C44 / (C11 - C12):.3f}  (1 = isotropic)")
    print(f"Average transverse speed c_t:         {c_transverse:.6e} m/s  (= c by the calibration in Step 1)")
    print(f"Average longitudinal speed c_l:       {c_longitudinal:.4e} m/s")
    for d, (t1, t2, l) in speeds.items():
        print(f"  direction {d}: transverse {t1/c_measured:.4f} c, {t2/c_measured:.4f} c;"
              f" longitudinal {l/c_measured:.4f} c")
    print("Light speed would depend on direction by tens of percent; experiment bounds this at ~1e-17.")

    # -------------------------------------------------------------------------
    # STEP 4: THE LONGITUDINAL BRANCH - BAND MAXIMUM, NOT A GAP
    # -------------------------------------------------------------------------
    # 1D-chain estimate of the dispersion: omega_l(k) = 2 (c_l/a_0) sin(k a_0 / 2).
    # omega_l(0) = 0: compression waves exist at ALL low frequencies (no gap).
    # hbar * omega_l(pi/a_0) is the HIGHEST possible longitudinal phonon energy (top of the band).
    omega_long_max = 2.0 * (c_longitudinal / a_0)
    E_long_gap_Joules = hbar * omega_long_max          # kept name for the plot: this is the band top
    E_long_gap_GeV = E_long_gap_Joules / (const.electron_volt * 1e9)
    lam_visible = 500e-9
    E_long_visible_eV = hbar * c_longitudinal * 2 * np.pi / lam_visible / const.electron_volt

    print("\n--- THE LONGITUDINAL BRANCH ---")
    print(f"Lowest longitudinal phonon energy:    0 (as k -> 0)  -> there is NO energy gap")
    print(f"Longitudinal band maximum (k=pi/a0):  {E_long_gap_GeV:.4e} GeV  (top of the band, not a gap)")
    print(f"Longitudinal phonon at 500 nm:        {E_long_visible_eV:.2f} eV  (optical energies excite it)")
    print("Conclusion: an elastic-solid vacuum would carry longitudinal waves at everyday energies;")
    print("            the 'ether objection' is not removed by the hard-core repulsion.")

    # -------------------------------------------------------------------------
    # STEP 5: DE BOER PARAMETER (WHY IT'S A SUPERFLUID, NOT A FROZEN SOLID)
    # -------------------------------------------------------------------------
    # In condensed matter physics, the de Boer parameter Lambda* measures the ratio
    # of zero-point quantum kinetic energy to potential well depth:
    # Lambda* = hbar / (a_0 * sqrt(M_0 * V_0))
    #
    # If Lambda* < 0.1: Classical crystal (freezes into a brittle solid like Argon/Lead).
    # If Lambda* > 0.3: Quantum fluid (zero-point motion melts the crystal even at T=0, like Helium-4!).
    Lambda_de_boer = hbar / (a_0 * np.sqrt(M_0 * V_0))
    
    print("\n--- QUANTUM FLUIDITY VS CLASSICAL SOLID ---")
    print(f"De Boer Quantum Parameter Lambda*:    {Lambda_de_boer:.4f}")
    print(f"sqrt(calibration constant):           {np.sqrt(calibration_constant):.4f}  (identical: Lambda* = sqrt(X)")
    print("                                      because hbar = l_P m_P c; it is not an independent result)")
    if Lambda_de_boer > 0.3:
        print("Verdict: Lambda* > 0.3 -> by the de Boer criterion this lattice would quantum-MELT (like He-4).")
        print("         A liquid has zero static shear modulus, which contradicts the shear-wave light of Step 3.")
    else:
        print("Verdict: Classical solid lattice.")
        
    return {
        "r_norm": r_norm, "V_actual": V_actual, "F_actual": F_actual,
        "c_transverse": c_transverse, "c_longitudinal": c_longitudinal,
        "E_long_gap_GeV": E_long_gap_GeV, "Lambda_de_boer": Lambda_de_boer,
        "E_long_visible_eV": E_long_visible_eV,
        "k_0": k_0, "rho_0": rho_0, "mu_0": mu_0
    }

def plot_foundational_substrate(data):
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig.patch.set_facecolor('#0d1117')
    
    for ax in axs.flat:
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        
    r = data["r_norm"]
    V = data["V_actual"] / 1e9 # in GigaJoules
    F = data["F_actual"] / 1e44 # normalized
    
    # 1. Asymmetric Inter-Particle Potential V(r)
    ax1 = axs[0, 0]
    ax1.plot(r, V, color='#58a6ff', lw=3, label=r'Lattice Potential $V(r)$')
    ax1.axhline(0, color='gray', linestyle='--', alpha=0.6)
    ax1.axvline(1.0, color='#ffa657', linestyle=':', lw=2, label=r'Equilibrium Spacing $a_0$')
    ax1.fill_between(r, V, 5, where=(r < 1.0), color='#f85149', alpha=0.3, label='Steep Compression Wall')
    ax1.fill_between(r, V, 0, where=(r >= 1.0), color='#7ee787', alpha=0.2, label='Soft Transverse Well')
    ax1.set_ylim(-3.0, 5.0)
    ax1.set_xlabel(r'Inter-Particle Distance $r / a_0$', fontsize=12)
    ax1.set_ylabel('Potential Energy [GJ]', fontsize=12)
    ax1.set_title('1. Microscopic Asymmetric Substrate Potential', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 2. Restoring Force F(r)
    ax2 = axs[0, 1]
    ax2.plot(r, F, color='#f85149', lw=3, label='Restoring Force $F(r)$')
    ax2.axhline(0, color='gray', linestyle='--')
    ax2.axvline(1.0, color='#ffa657', linestyle=':')
    ax2.set_ylim(-5.0, 10.0)
    ax2.set_xlabel(r'Separation $r / a_0$', fontsize=12)
    ax2.set_ylabel(r'Force [$\times 10^{44}\,$N]', fontsize=12)
    ax2.set_title('2. Extreme Hard-Core Repulsive Wall ($r < a_0$)', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 3. Acoustic Phonon Dispersion & Energy Gap
    ax3 = axs[1, 0]
    k_vals = np.linspace(0, np.pi, 300) # k * a_0
    omega_trans = np.sin(k_vals / 2.0) * (data["c_transverse"] / 1e8)
    omega_long = np.sin(k_vals / 2.0) * (data["c_longitudinal"] / 1e8)
    
    ax3.plot(k_vals / np.pi, omega_trans, color='#7ee787', lw=3, label='Transverse Mode (Light/Photons)')
    ax3.plot(k_vals / np.pi, omega_long, color='#f85149', lw=3, linestyle='--', label='Longitudinal Mode (Compression)')
    ax3.set_xlabel(r'Wavevector $k \cdot a_0 / \pi$ (Brillouin Zone)', fontsize=12)
    ax3.set_ylabel(r'Frequency $\omega \cdot a_0$ [Arbitrary Units]', fontsize=12)
    ax3.set_title('3. Dispersion: both branches start at $\\omega = 0$ (no gap)', fontsize=13, fontweight='bold')
    ax3.legend(loc='upper left', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 4. Energy Scale Hierarchy & Freeze-Out
    ax4 = axs[1, 1]
    categories = ['Visible Light\n(2 eV)', 'Longitudinal phonon\nat 500 nm', 'Longitudinal band\nMAXIMUM']
    energies_log = [np.log10(2e-9), np.log10(data["E_long_visible_eV"] * 1e-9), np.log10(data["E_long_gap_GeV"])]
    bar_colors = ['#58a6ff', '#ffa657', '#f85149']
    bars = ax4.bar(categories, energies_log, color=bar_colors, width=0.5, edgecolor='white')
    ax4.set_ylabel(r'Log$_{10}$(Energy [GeV])', fontsize=12)
    ax4.set_title('4. Longitudinal phonons span 0 ... band maximum', fontsize=13, fontweight='bold')
    for bar in bars:
        h = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, h + 1.0 if h >= 0 else h - 2.5,
                 f'$10^{{{int(h)}}}$ GeV', ha='center', color='white', fontweight='bold')
    ax4.set_ylim(-12, 23)
    
    plt.tight_layout()
    output_path = os.path.join(HERE, 'foundational_substrate_potential.png')
    plt.savefig(output_path, dpi=300)
    print(f"\nFoundational potential diagram saved to: {output_path}")

if __name__ == "__main__":
    data = analyze_foundational_substrate()
    plot_foundational_substrate(data)
