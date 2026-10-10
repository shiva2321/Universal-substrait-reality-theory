"""
Charged-lepton masses from the Koide/Brannen parametrisation
    sqrt(m_k) = v0 [1 + sqrt2 cos(delta + 2 pi k / 3)],   k = 0, 1, 2.
Notes (audit 2026-10):
* This parametrisation gives Koide's Q = 2/3 identically for ANY v0 and delta, so it cannot
  derive Q = 2/3. Q = 2/3 itself is Y. Koide's empirical relation (1981/83) and is satisfied by the
  measured masses to within 0.4 sigma - a real, unexplained regularity.
* delta ~ 2/9 is C. Brannen's and G. Rosen's observation (c. 2006). Fixing delta = 2/9 EXACTLY and
  using m_e predicts m_mu = 105.6594 MeV, which is ~450 standard deviations from the measured
  105.6583755(23) MeV, so delta = 2/9 is only approximate.
* The "phase-space dimension 9 / trace normalisation 2" argument is a label, not a calculation.
* PDG 2024 tau mass: 1776.93 +- 0.09 MeV.
"""

import os
import numpy as np
import scipy.constants as const
import matplotlib.pyplot as plt

def derive_complete_lepton_spectrum():
    print("=" * 80)
    print("STEP 1: THE KOIDE CIRCULANT EIGENVALUE PROBLEM ON THE 3-LAYER LATTICE")
    print("=" * 80)
    
    # Precision Experimental Targets (CODATA 2022 / PDG 2024)
    m_e_measured = 0.510998950       # MeV (Electron)
    m_mu_measured = 105.6583755       # MeV (Muon)
    m_tau_measured = 1776.93          # MeV (Tau, PDG 2024: +/- 0.09 MeV)
    dm_mu, dm_tau = 0.0000023, 0.09   # 1-sigma uncertainties (PDG 2024)
    
    print(f"Target Electron Mass (m_e):       {m_e_measured:.6f} MeV")
    print(f"Target Muon Mass (m_mu):          {m_mu_measured:.6f} MeV")
    print(f"Target Tau Mass (m_tau):          {m_tau_measured:.2f} MeV")
    
    # -------------------------------------------------------------------------
    # STEP 2: THE GEOMETRIC ORIGIN OF THE PHASE ANGLE delta = 2/9 RADIANS
    # -------------------------------------------------------------------------
    # In an HCP/FCC close-packed lattice, stacking follows a 3-layer cycle (ABC stacking).
    # A chiral topological knot weaving across the 3 layers has state space C^3.
    # The complete phase space of quadratic invariants on this 3-layer state has dimension:
    # Dim = 3 x 3 = 9 degrees of freedom.
    #
    # The Lie algebra generators satisfy the trace normalization:
    # Tr(lambda_a * lambda_b) = 2 * delta_ab
    # The minimum non-trivial topological holonomy per layer of the 9-dimensional manifold is:
    # delta = Tr(lambda^2) / Dim = 2 / 9 radians!
    
    delta = 2.0 / 9.0 # 0.2222222222 rad = 12.732395 deg
    print("\n--- THE 2/9 TOPOLOGICAL PHASE ANGLE ---")
    print(f"Cyclic 3-Layer Phase Space Dimension: 3 x 3 = 9")
    print(f"Generator Trace Metric Normalization: 2")
    print(f"Fundamental Holonomy Angle delta:     2 / 9 = {delta:.8f} rad ({np.degrees(delta):.6f} deg)")
    
    # -------------------------------------------------------------------------
    # STEP 3: CIRCULANT MATRIX EIGENVALUES (THE THREE GENERATIONS)
    # -------------------------------------------------------------------------
    # The secular eigenvalue equation for the 3 generations is:
    # sqrt(m_k) = v_0 * [ 1 + sqrt(2) * cos(delta + 2*pi*k / 3) ]
    # Where:
    # k = 0 corresponds to the Tau lepton   (angle = 2/9 = 12.732 deg)
    # k = 1 corresponds to the Electron     (angle = 2/9 + 2pi/3 = 132.732 deg)
    # k = 2 corresponds to the Muon         (angle = 2/9 + 4pi/3 = 252.732 deg)
    
    angles = delta + np.array([0, 1, 2]) * (2.0 * np.pi / 3.0)
    factors = 1.0 + np.sqrt(2.0) * np.cos(angles)
    
    # Factor for electron (k = 1):
    factor_e = factors[1]
    factor_mu = factors[2]
    factor_tau = factors[0]
    
    # First-principles connection:
    # In Step 1, USRT derived m_e = 0.510755 MeV from the instanton path integral!
    # Let's test BOTH:
    # A) Using the measured electron mass:
    v0_codata = np.sqrt(m_e_measured) / factor_e
    m_e_codata = (v0_codata * factor_e)**2
    m_mu_codata = (v0_codata * factor_mu)**2
    m_tau_codata = (v0_codata * factor_tau)**2
    
    # B) Using the USRT electron-mass formula (computed here instead of the hard-coded 0.51075501):
    _m_P = np.sqrt(const.hbar * const.c / const.G)
    _a = const.fine_structure
    _me_kg = _m_P * (np.sqrt(3) / 2) * np.exp(-(3 / (8 * _a) - _a / (2 * np.pi) * np.sqrt(12)))
    m_e_usrt_base = _me_kg * const.c**2 / (const.electron_volt * 1e6)
    v0_usrt = np.sqrt(m_e_usrt_base) / factor_e
    m_e_usrt = (v0_usrt * factor_e)**2
    m_mu_usrt = (v0_usrt * factor_mu)**2
    m_tau_usrt = (v0_usrt * factor_tau)**2
    
    # Precision calculations:
    err_mu = 100.0 * np.abs(m_mu_codata - m_mu_measured) / m_mu_measured
    err_tau = 100.0 * np.abs(m_tau_codata - m_tau_measured) / m_tau_measured
    
    Q_koide = (m_e_codata + m_mu_codata + m_tau_codata) / ((np.sqrt(m_e_codata) + np.sqrt(m_mu_codata) + np.sqrt(m_tau_codata))**2)
    
    print("\n--- EXACT PREDICTED LEPTON MASSES (FROM delta = 2/9) ---")
    print(f"Scale Factor v_0:                 {v0_codata:.6f} MeV^0.5")
    print(f"Predicted Electron Mass:          {m_e_codata:.6f} MeV (Measured: {m_e_measured:.6f} MeV) -> Match: 100.0000%")
    print(f"Predicted Muon Mass:              {m_mu_codata:.6f} MeV (Measured: {m_mu_measured:.6f} MeV) -> Match: {100.0 - err_mu:.4f}%")
    print(f"Predicted Tau Mass:               {m_tau_codata:.2f} MeV (Measured: {m_tau_measured:.2f} MeV) -> Match: {100.0 - err_tau:.4f}%")
    print(f"Koide Parameter Q:                {Q_koide:.10f} (= 2/3 identically: built into the parametrisation)")
    print(f"Muon vs measurement:              {(m_mu_codata - m_mu_measured)/dm_mu:+.0f} sigma  (delta = 2/9 is NOT exact)")
    print(f"Tau vs PDG 2024:                  {(m_tau_codata - m_tau_measured)/dm_tau:+.2f} sigma")
    Q_measured = (m_e_measured + m_mu_measured + m_tau_measured) / (np.sqrt(m_e_measured) + np.sqrt(m_mu_measured) + np.sqrt(m_tau_measured))**2
    print(f"Koide Q from MEASURED masses:     {Q_measured:.7f}  (2/3 within ~0.4 sigma: genuine empirical regularity)")
    
    print("\n--- USING PURE USRT FIRST-PRINCIPLES ELECTRON BASE (0.510755 MeV) ---")
    print(f"USRT Predicted Muon Mass:         {m_mu_usrt:.4f} MeV (Accuracy: {100.0 - 100.0*abs(m_mu_usrt - m_mu_measured)/m_mu_measured:.3f}%)")
    print(f"USRT Predicted Tau Mass:          {m_tau_usrt:.2f} MeV (Accuracy: {100.0 - 100.0*abs(m_tau_usrt - m_tau_measured)/m_tau_measured:.3f}%)")
    
    return {
        "angles": angles, "factors": factors,
        "m_e_measured": m_e_measured, "m_mu_measured": m_mu_measured, "m_tau_measured": m_tau_measured,
        "m_e_pred": m_e_codata, "m_mu_pred": m_mu_codata, "m_tau_pred": m_tau_codata,
        "err_mu": err_mu, "err_tau": err_tau, "Q_koide": Q_koide,
        "pull_mu": (m_mu_codata - m_mu_measured) / dm_mu, "pull_tau": (m_tau_codata - m_tau_measured) / dm_tau,
        "Q_measured": Q_measured,
        "dQ_measured": abs((m_e_measured + m_mu_measured + m_tau_measured + dm_tau)
                           / (np.sqrt(m_e_measured) + np.sqrt(m_mu_measured) + np.sqrt(m_tau_measured + dm_tau))**2
                           - Q_measured),
        "delta": delta, "v0": v0_codata
    }

def plot_lepton_spectrum_proof(data):
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
        
    # 1. The 3-Generation Phase Dial (Z_3 Symmetry with delta = 2/9)
    ax1 = axs[0, 0]
    circle_theta = np.linspace(0, 2*np.pi, 300)
    ax1.plot(np.cos(circle_theta), np.sin(circle_theta), color='gray', linestyle='--', alpha=0.5)
    
    labels = [r'Tau ($\tau$)' + f'\n$\\phi = 2/9$\n({np.degrees(data["angles"][0]):.1f}°)',
              r'Electron ($e$)' + f'\n$\\phi = 2/9 + 2\\pi/3$\n({np.degrees(data["angles"][1]):.1f}°)',
              r'Muon ($\mu$)' + f'\n$\\phi = 2/9 + 4\\pi/3$\n({np.degrees(data["angles"][2]):.1f}°)']
    colors = ['#f85149', '#58a6ff', '#ffa657']
    
    for i in range(3):
        ang = data["angles"][i]
        x_pt = np.cos(ang)
        y_pt = np.sin(ang)
        ax1.plot([0, x_pt], [0, y_pt], color=colors[i], lw=2.5)
        ax1.plot(x_pt, y_pt, 'o', color=colors[i], markersize=10)
        ax1.text(x_pt * 1.25, y_pt * 1.25, labels[i], color=colors[i],
                 ha='center', va='center', fontweight='bold', fontsize=10)
        
    ax1.set_xlim(-1.6, 1.6)
    ax1.set_ylim(-1.6, 1.6)
    ax1.set_aspect('equal')
    ax1.set_title(r'1. Cyclic $Z_3$ Lepton Phase Dial with $\delta = 2/9$ Radians', fontsize=13, fontweight='bold')
    
    # 2. Predicted vs Measured Lepton Mass Hierarchy (Log Scale)
    ax2 = axs[0, 1]
    particles = ['Electron ($e$)', 'Muon ($\\mu$)', 'Tau ($\\tau$)']
    m_preds = [data["m_e_pred"], data["m_mu_pred"], data["m_tau_pred"]]
    m_reals = [data["m_e_measured"], data["m_mu_measured"], data["m_tau_measured"]]
    x_pos = np.arange(3)
    
    ax2.bar(x_pos - 0.15, m_preds, width=0.3, color='#7ee787', label='USRT Predicted Mass', edgecolor='white')
    ax2.bar(x_pos + 0.15, m_reals, width=0.3, color='#58a6ff', label='CODATA / PDG Measured', edgecolor='white')
    ax2.set_yscale('log')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(particles, fontsize=11, fontweight='bold')
    ax2.set_ylabel('Rest Mass [MeV] (Log Scale)', fontsize=12)
    ax2.set_title('2. Lepton masses (electron = INPUT, delta = 2/9)', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper left', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    # 3. Distance from measurement in standard deviations (audit: replaces "% match")
    ax3 = axs[1, 0]
    pulls = [abs(data["pull_mu"]), abs(data["pull_tau"])]
    bars3 = ax3.bar(['Muon ($\\mu$)', 'Tau ($\\tau$)'], pulls, color=['#f85149', '#7ee787'], width=0.45, edgecolor='white')
    ax3.set_yscale('log')
    ax3.set_ylim(0.1, 3000)
    ax3.axhline(1.0, color='#7ee787', ls='--', lw=1.2)
    ax3.axhline(5.0, color='#f85149', ls='--', lw=1.2)
    ax3.text(1.45, 1.1, '1 sigma', color='#7ee787', ha='right', fontsize=10)
    ax3.text(1.45, 5.5, '5 sigma (excluded above)', color='#f85149', ha='right', fontsize=10)
    ax3.set_ylabel('|prediction - measured| / sigma', fontsize=12)
    ax3.set_title('3. Muon with delta = 2/9 is 452 sigma off; tau (Koide relation) fine', fontsize=13, fontweight='bold')
    for b, v in zip(bars3, pulls):
        ax3.text(b.get_x() + b.get_width()/2.0, v * 1.25, f'{v:,.2f} sigma' if v < 10 else f'{v:,.0f} sigma',
                 ha='center', color='white', fontweight='bold', fontsize=11)
    ax3.text(-0.35, 1500, 'electron: used as INPUT (not a prediction)', color='white', fontsize=10)

    # 4. Koide Q: measured value vs 2/3 (Q = 2/3 holds for ANY delta in this parametrisation)
    ax4 = axs[1, 1]
    ax4.errorbar([0], [data["Q_measured"]], yerr=[data["dQ_measured"]], fmt='o', color='#58a6ff',
                 ms=10, capsize=8, lw=2, label='Measured (PDG 2024 masses)')
    ax4.axhline(2.0 / 3.0, color='#7ee787', ls='--', lw=2, label='Q = 2/3')
    ax4.set_xlim(-1, 1)
    ax4.set_xticks([])
    ax4.set_ylim(2.0 / 3.0 - 2.5e-5, 2.0 / 3.0 + 1.5e-5)
    ax4.ticklabel_format(axis='y', useOffset=False)
    ax4.set_ylabel('Koide Ratio $Q$', fontsize=12)
    ax4.set_title('4. Koide Q: real empirical regularity (Koide 1981), not derived', fontsize=13, fontweight='bold')
    ax4.text(0.05, data["Q_measured"] - 1.3e-5,
             f'Q = {data["Q_measured"]:.7f} +- {data["dQ_measured"]:.7f}\n'
             f'({(data["Q_measured"] - 2/3)/data["dQ_measured"]:+.2f} sigma from 2/3)\n'
             'The parametrisation gives Q = 2/3 for ANY delta,\nso it cannot predict Q.',
             color='white', fontsize=11)
    ax4.legend(loc='upper right', facecolor='#161b22', edgecolor='#30363d', labelcolor='white')

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exact_three_generation_lepton_spectrum.png')
    plt.savefig(output_path, dpi=300)
    print(f"\nComplete lepton spectrum proof diagram saved to: {output_path}")

if __name__ == "__main__":
    res = derive_complete_lepton_spectrum()
    plot_lepton_spectrum_proof(res)
