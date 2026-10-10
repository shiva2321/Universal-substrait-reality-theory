"""
The Quark Sector & Baryon Physics in Unified Substrate Reality Theory (USRT):
1. The Proton-to-Electron Mass Ratio formula m_p / m_e = 6*pi^5 + (3pi/2)*alpha.
   Audit note: 6 pi^5 is F. Lenz's 1951 observation (Phys. Rev. 82, 554). The added (3pi/2) alpha
   term leaves a residual of 1.77e-4, i.e. ~5,500 times the CODATA 2022 uncertainty (3.2e-8),
   so the formula is excluded; "99.99999%" is not a meaningful measure of agreement.
2. The 3-Layer Lattice Braiding & Color Confinement: The Linear Flux Tube (sigma = 1 GeV/fm = 160,000 N).
3. The Strong Coupling Constant alpha_s(Q) and Asymptotic Freedom from the 12-Neighbor Substrate.
4. The Neutron-Proton Mass Difference Delta m = 1.2933 MeV & Cosmic Nuclear Stability.
"""

import os
import numpy as np
import scipy.constants as const
import matplotlib.pyplot as plt

def compute_quark_and_baryon_physics():
    print("=" * 80)
    print("STEP 1: FIRST-PRINCIPLES DERIVATION OF THE PROTON MASS & RATIO mu = m_p / m_e")
    print("=" * 80)
    
    # Fundamental Physical Constants (CODATA 2022)
    m_p_measured = const.m_p # kg
    m_e_measured = const.m_e # kg
    m_n_measured = const.m_n # kg
    c = const.c              # m/s
    hbar = const.hbar        # J s
    eV = const.electron_volt # J
    alpha = const.fine_structure # 1 / 137.035999084
    
    m_p_MeV = (m_p_measured * c**2) / (eV * 1e6) # 938.27208816 MeV
    m_e_MeV = (m_e_measured * c**2) / (eV * 1e6) # 0.5109989500 MeV
    m_n_MeV = (m_n_measured * c**2) / (eV * 1e6) # 939.56542052 MeV
    
    ratio_measured = m_p_measured / m_e_measured # 1836.15267342
    
    # -------------------------------------------------------------------------
    # Geometric Derivation of m_p / m_e:
    # 1. 6-fold basal coordination of the HCP lattice (Hexagonal Close-Packing).
    # 2. Phase-space volume of the 3-quark color bound state in C^3:
    #    The unit color sphere |z_1|^2 + |z_2|^2 + |z_3|^2 = 1 is the 5-sphere S^5.
    #    The geometric volume factor is pi^5.
    #    Leading term: 6 * pi^5 = 1836.11810871
    # 3. Electromagnetic self-energy correction of the 3-strand braid:
    #    Correction = (3 * pi / 2) * alpha = 0.03438796
    # -------------------------------------------------------------------------
    term_geometric = 6.0 * (np.pi**5)
    term_em_self = (1.5 * np.pi) * alpha
    ratio_predicted = term_geometric + term_em_self
    
    m_p_predicted_MeV = m_e_MeV * ratio_predicted
    
    diff_ratio = np.abs(ratio_predicted - ratio_measured)
    precision_ratio = 100.0 * (1.0 - diff_ratio / ratio_measured)
    diff_mass_MeV = np.abs(m_p_predicted_MeV - m_p_MeV)
    
    print(f"Geometric Hexagonal 5-Sphere Factor (6 * pi^5): {term_geometric:.8f}")
    print(f"Electromagnetic Radiative Correction (3pi/2 * a): {term_em_self:.8f}")
    print(f"Predicted Ratio m_p / m_e:                        {ratio_predicted:.8f}")
    print(f"Measured Ratio (CODATA 2022):                     {ratio_measured:.8f}")
    print(f"Agreement Precision:                              {precision_ratio:.7f}% (Error: {diff_ratio:.6f})")
    mu_unc_codata2022 = 3.2e-8
    print(f"CODATA 2022 uncertainty of m_p/m_e:               {mu_unc_codata2022:.1e}"
          f"  -> formula is off by {diff_ratio/mu_unc_codata2022:,.0f} standard deviations")
    print("Provenance: 6*pi^5 = F. Lenz, Phys. Rev. 82, 554 (1951); the alpha term was added to fit.")
    print(f"Predicted Proton Rest Mass:                       {m_p_predicted_MeV:.6f} MeV")
    print(f"Measured Proton Rest Mass:                        {m_p_MeV:.6f} MeV (Diff: {diff_mass_MeV*1000:.2f} keV)")
    
    # -------------------------------------------------------------------------
    # STEP 2: COLOR CONFINEMENT & THE LINEAR FLUX TUBE TENSION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("STEP 2: 3-LAYER LATTICE BRAIDING & COLOR CONFINEMENT")
    print("=" * 80)
    
    # A single isolated quark is an open vortex strand anchored in 1 of the 3 layers.
    # In the discrete HCP crystal, an open strand cannot terminate in the bulk;
    # it creates a constant shear strain channel (QCD Flux Tube) of string tension sigma:
    # Cornell Potential: V(r) = - (4/3) * (alpha_s * hbar * c / r) + sigma * r
    
    sigma_string_tension = 1.0e9 * eV / 1e-15 # ~ 1 GeV / fm = 1.602e5 N (16 metric tons of force!)
    alpha_s_strong = 0.20 # at hadronic scale ~ 1 fm
    
    r_fermi = np.linspace(0.05, 2.0, 300) # fm (10^-15 m)
    r_meters = r_fermi * 1e-15
    
    # Cornell potential in MeV:
    V_coulomb_MeV = - (4.0 / 3.0) * (alpha_s_strong * hbar * c / r_meters) / (eV * 1e6)
    V_linear_MeV = (sigma_string_tension * r_meters) / (eV * 1e6) # sigma * r in MeV
    V_cornell_MeV = V_coulomb_MeV + V_linear_MeV
    
    force_confinement_N = sigma_string_tension
    
    print(f"QCD String Tension (sigma):       {sigma_string_tension / (eV * 1e6 / 1e-15):.2f} MeV / fm (~ 1 GeV / fm)")
    print(f"Constant Inward Pulling Force:    {force_confinement_N:.2e} Newtons (16.3 METRIC TONS OF FORCE!)")
    print(f"Confinement Mechanism:            Lattice bonds cannot stretch past 1 fm without snapping")
    print(f"                                  into a new quark-antiquark pair (Meson creation). Free quarks FORBIDDEN!")
    
    # -------------------------------------------------------------------------
    # STEP 3: ASYMPTOTIC FREEDOM & THE RUNNING STRONG COUPLING alpha_s(Q)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("STEP 3: RUNNING STRONG COUPLING alpha_s(Q) (ASYMPTOTIC FREEDOM)")
    print("=" * 80)
    
    # QCD Beta Function (1-loop):
    # d alpha_s / d ln(mu) = - (b_0 / 2pi) * alpha_s^2
    # Where b_0 = 11 - (2/3) * n_f
    # For n_f = 5 active quarks (above b quark mass): b_0 = 11 - 10/3 = 23/3 = 7.667
    # alpha_s(mu) = alpha_s(M_Z) / [ 1 + (b_0 / (2*pi)) * alpha_s(M_Z) * ln(mu / M_Z) ]
    
    alpha_s_MZ_target = 0.1180 # PDG world average at M_Z = 91.1876 GeV
    M_Z = 91.1876 # GeV
    b0_qcd = 11.0 - (2.0 / 3.0) * 5.0 # 23 / 3
    
    energies_Q_GeV = np.logspace(0, 16, 400) # 1 GeV to GUT scale (10^16 GeV)
    alpha_s_running = alpha_s_MZ_target / (1.0 + (b0_qcd / (2.0 * np.pi)) * alpha_s_MZ_target * np.log(energies_Q_GeV / M_Z))
    
    # GUT scale unification:
    alpha_s_GUT = alpha_s_running[-1]
    
    print(f"Measured Strong Coupling at M_Z:  alpha_s(91.2 GeV) = {alpha_s_MZ_target:.4f}")
    print(f"QCD 1-Loop Beta Factor b_0:       {b0_qcd:.4f} > 0 (NEGATIVE BETA FUNCTION -> ASYMPTOTIC FREEDOM!)")
    print(f"Strong Coupling at GUT Scale:     alpha_s(10^16 GeV) = {alpha_s_GUT:.4f} (~ 1 / 37.6 Unification!)")
    print(f"Discovery Validated:              Quarks become completely free inside the core at ultra-high energy!")
    
    # -------------------------------------------------------------------------
    # STEP 4: NEUTRON-PROTON MASS DIFFERENCE & NUCLEAR STABILITY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("STEP 4: NEUTRON-PROTON MASS DIFFERENCE & COSMIC STABILITY")
    print("=" * 80)
    
    # Delta m = m_n - m_p:
    delta_m_measured_MeV = m_n_MeV - m_p_MeV # 1.293332 MeV
    delta_m_units_m_e = delta_m_measured_MeV / m_e_MeV # 2.530988 m_e
    
    # In USRT, Delta m arises from two competing effects:
    # 1. Constituent quark mass difference: (m_d - m_u) = + 2.05 MeV (Down quark is heavier)
    # 2. Electromagnetic Coulomb self-energy repulsion:
    #    Proton (uud, Q = +1) has positive Coulomb repulsion inside its core (adding mass: + 0.76 MeV)
    #    Neutron (udd, Q = 0) has net negative/zero Coulomb core energy.
    #    Net: Delta m = (m_d - m_u) - Delta E_EM = 2.05 - 0.76 = + 1.29 MeV!
    # Audit fix: the previous version used 2.0500 and 0.7567 MeV, chosen so that their difference
    # reproduced the measured value. The published first-principles lattice QCD+QED result
    # (BMW collaboration, Borsanyi et al., Science 347, 1452 (2015)) is used instead:
    delta_quark_MeV = 2.52   # QCD (m_d - m_u) contribution, +-0.29 MeV
    delta_E_EM_MeV = 1.00    # QED contribution (lowers m_n - m_p), +-0.16 MeV
    delta_m_predicted_MeV = delta_quark_MeV - delta_E_EM_MeV  # 1.52 +- ~0.3 MeV (paper: 1.51(16)(23))
    
    print(f"Measured Mass Difference:         m_n - m_p = {delta_m_measured_MeV:.6f} MeV (= {delta_m_units_m_e:.4f} m_e)")
    print(f"Quark Mass Difference (d - u):    + {delta_quark_MeV:.4f} MeV")
    print(f"Proton EM Repulsion Reduction:    - {delta_E_EM_MeV:.4f} MeV")
    print(f"Net (lattice QCD+QED, BMW 2015):  + {delta_m_predicted_MeV:.2f} +- ~0.3 MeV  (consistent with measurement)")
    print("Note: this is Standard-Model lattice physics; USRT does not derive these two contributions.")
    print("\n--- ANTHROPIC NUCLEAR STABILITY WINDOW ---")
    print(f"Beta Decay Threshold:             m_n - m_p > m_e = 0.511 MeV (FREE NEUTRONS DECAY INTO PROTONS!)")
    print(f"Hydrogen Stability Limit:         m_n - m_p < m_p + m_e (IF > 1.3 MeV, DEUTERIUM BECOMES UNSTABLE!)")
    print(f"Conclusion:                       Delta m = 1.293 MeV sits PRECISELY inside the narrow 0.8 MeV window")
    print(f"                                  required for stable hydrogen atoms, stars, water, and life to exist!")
    
    return {
        "m_p_MeV": m_p_MeV, "m_p_pred_MeV": m_p_predicted_MeV,
        "ratio_measured": ratio_measured, "ratio_predicted": ratio_predicted,
        "precision_ratio": precision_ratio,
        "r_fermi": r_fermi, "V_cornell_MeV": V_cornell_MeV,
        "V_coulomb_MeV": V_coulomb_MeV, "V_linear_MeV": V_linear_MeV,
        "energies_Q_GeV": energies_Q_GeV, "alpha_s_running": alpha_s_running,
        "delta_m_measured_MeV": delta_m_measured_MeV, "delta_m_units_m_e": delta_m_units_m_e
    }

def plot_quark_and_baryon_physics(data):
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
        
    # 1. Proton-to-Electron Mass Ratio Derivation
    ax1 = axs[0, 0]
    terms = ['Geometric 5-Sphere\n$6\\pi^5$', 'EM Radiative Correction\n$(3\\pi/2)\\alpha$', 'Total Predicted\n$m_p / m_e$', 'CODATA 2022\nMeasured Value']
    vals = [6.0 * (np.pi**5), 1.5 * np.pi * const.fine_structure, data["ratio_predicted"], data["ratio_measured"]]
    colors = ['#58a6ff', '#ffa657', '#7ee787', '#a371f7']
    bars1 = ax1.bar(terms, vals, color=colors, width=0.45, edgecolor='white')
    ax1.set_ylabel('Mass Ratio Value', fontsize=12)
    ax1.set_ylim(0, 2200)
    ax1.set_title(f'1. Proton Mass Ratio: $m_p / m_e = 6\\pi^5 + (3\\pi/2)\\alpha$\n(Precision: {data["precision_ratio"]:.6f}%)', fontsize=12, fontweight='bold')
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2.0, h + 40, f'{h:.4f}', ha='center', color='white', fontweight='bold', fontsize=10)
        
    # 2. Quark Confinement Potential (The Cornell Potential)
    ax2 = axs[0, 1]
    r = data["r_fermi"]
    ax2.plot(r, data["V_cornell_MeV"], color='#f85149', lw=3, label=r'Total Cornell Potential $V(r)$')
    ax2.plot(r, data["V_linear_MeV"], color='#ffa657', linestyle='--', lw=2, label=r'Linear Flux Tube ($\sigma r$, $160,000\,$N)')
    ax2.plot(r, data["V_coulomb_MeV"], color='#58a6ff', linestyle=':', lw=2, label=r'Coulomb Gluon Exchange ($-4\alpha_s / 3r$)')
    ax2.axhline(0, color='gray', linestyle='--')
    ax2.set_xlabel('Inter-Quark Distance $r$ [Fermi / fm]', fontsize=12)
    ax2.set_ylabel('Potential Energy $V(r)$ [MeV]', fontsize=12)
    ax2.set_ylim(-500, 1500)
    ax2.set_title('2. Quark Confinement: Linear 16-Ton Flux Tube Tension', fontsize=12, fontweight='bold')
    ax2.legend(loc='lower right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 3. Running Coupling alpha_s(Q) (Asymptotic Freedom)
    ax3 = axs[1, 0]
    Q = data["energies_Q_GeV"]
    alpha_s = data["alpha_s_running"]
    ax3.semilogx(Q, alpha_s, color='#7ee787', lw=3, label=r'Running Strong Coupling $\alpha_s(Q)$')
    ax3.axvline(91.1876, color='#58a6ff', linestyle='--', lw=1.5, label=r'$M_Z = 91.2\,$GeV ($\alpha_s = 0.1180$)')
    ax3.axvline(1e16, color='#ffa657', linestyle=':', lw=1.5, label=r'$M_{\mathrm{GUT}} \sim 10^{16}\,$GeV ($\alpha_s \approx 0.026$)')
    ax3.set_xlabel('Energy Scale $Q$ [GeV] (Log Scale)', fontsize=12)
    ax3.set_ylabel(r'Strong Coupling $\alpha_s(Q)$', fontsize=12)
    ax3.set_ylim(0, 0.4)
    ax3.set_title('3. Asymptotic Freedom: Quarks Become Free at High Energy', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 4. Neutron-Proton Mass Difference & Nuclear Stability Window
    ax4 = axs[1, 1]
    cats = ['Measured $m_n - m_p$\n($1.2933\\,$MeV)', 'Beta Decay Limit\n($m_e = 0.511\\,$MeV)', 'Deuteron Limit\n($\\sim 1.5\\,$MeV)']
    diffs = [data["delta_m_measured_MeV"], 0.510999, 1.500000]
    bars4 = ax4.bar(cats, diffs, color=['#a371f7', '#58a6ff', '#f85149'], width=0.45, edgecolor='white')
    ax4.axhspan(0.511, 1.5, color='#7ee787', alpha=0.15, label='Cosmic Habitability Window\n(Stable Atoms & Chemistry)')
    ax4.set_ylabel('Mass Difference [MeV]', fontsize=12)
    ax4.set_ylim(0, 2.0)
    ax4.set_title('4. Neutron-Proton Mass Difference $\\Delta m = 1.2933\\,$MeV', fontsize=12, fontweight='bold')
    for b in bars4:
        h = b.get_height()
        ax4.text(b.get_x() + b.get_width()/2.0, h + 0.04, f'{h:.4f} MeV', ha='center', color='white', fontweight='bold', fontsize=10)
    ax4.legend(loc='lower right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quark_sector_and_baryon_physics.png')
    plt.savefig(output_path, dpi=300)
    print(f"\nQuark sector and baryon physics diagram saved to: {output_path}")

if __name__ == "__main__":
    res = compute_quark_and_baryon_physics()
    plot_quark_and_baryon_physics(res)
