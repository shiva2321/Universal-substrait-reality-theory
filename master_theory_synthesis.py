"""
Master Theory Synthesis & Architectural Verification:
Unified Substrate Reality Theory (USRT).

Consolidates all derivations across the 10 Pillars:
1. Substrate Medium & Elasticity: mu_P = c^7/(hbar*G^2), rho_P = c^5/(hbar*G^2), c = sqrt(mu/rho).
2. Spacetime Lattice: HCP close-packing (eta = 74.05%), Z = 12 bonds, k = c^4/G, F_max = c^4/(4G).
3. Cavitation Gravity: Delta rho = -M/r, Mercury precession, Cassini (gamma = 1.0).
4. Particles as Trapped Light: Electron cavity r_C = hbar/(mc), nu_Z = 123.6 EHz, F_wall = 0.212 N.
5. Electron Mass Formula: m_e = m_P * (sqrt(3)/2) * exp(-3/(8*alpha)).
6. Cosmogenesis: Instanton nucleation from a=0 -> a_0, condensation phase transition, inflation.
7. Light as Shear Waves: E = -du/dt, B = curl(u), Maxwell equations from Cauchy elasticity.
8. Relational Time: Wheeler-DeWitt Page-Wootters H|Psi> = 0, Chronon t_P = 5.39e-44 s.
9. Dark Sector: psiDM Bose condensate core (r_core ~ 1.5 kpc), Volovik P_vac = 0 dark energy.
10. Quantum Entanglement: 5D vortex filament (Bell CHSH).

AUDIT NOTE (see audit/USRT_AUDIT_REPORT.md): the original dashboard hard-coded
"[PASSED]" for six benchmarks and a "99.992% exponent accuracy" for the electron.
The statuses below are now either COMPUTED here or LABELLED with where the number
actually comes from (an input, a standard-physics formula, or a failed check).
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import shutil

def run_master_synthesis():
    print("Executing Master Synthesis and Architectural Verification...")
    
    # Fundamental constants
    c = 2.99792458e8             # m/s
    hbar = 1.054571817e-34       # J s
    G = 6.67430e-11              # m^3 / (kg s^2)
    G_rel_unc = 0.00015 / 6.67430   # CODATA 2022 relative uncertainty of G (2.2e-5)
    alpha = 7.2973525693e-3      # Fine structure constant
    m_e_measured = 9.1093837e-31 # kg
    
    # 1. Planck Scale Metrics
    l_P = np.sqrt(hbar * G / (c**3))
    m_P = np.sqrt(hbar * c / G)
    mu_P = (c**7) / (hbar * (G**2))
    rho_P = (c**5) / (hbar * (G**2))
    k_bond = (c**4) / G          # NOTE: units of N (a force), not N/m (a stiffness)
    F_max = (c**4) / (4.0 * G)
    
    # 2. Electron Mass Formula (this dashboard's version, without the fitted alpha-correction)
    K_hcp = np.sqrt(3.0) / 2.0
    S_instanton = 3.0 / (8.0 * alpha)
    m_e_predicted = m_P * K_hcp * np.exp(-S_instanton)
    
    # Original metric: error divided by ln(m_P/m_e) = 51.5 (inflates agreement ~50x).
    exponent_accuracy = 100.0 * (1.0 - np.abs(np.log(m_P / m_e_predicted) - np.log(m_P / m_e_measured)) / np.log(m_P / m_e_measured))
    mass_rel_error = (m_e_predicted - m_e_measured) / m_e_measured
    # Uncertainty of a prediction m_P * f(alpha): m_P carries sqrt(G) -> 0.5 * 2.2e-5
    mass_sigma = abs(np.log(m_e_predicted / m_e_measured)) / (0.5 * G_rel_unc)
    
    # 3. Bell CHSH: what a LOCAL shared-phase vortex model actually gives
    # (audit/a03_bell_models.py). For a shared hidden phase the correlation is
    # the triangle function E(d) = -1 + 2|d|/pi on [0, pi].
    def E_local(a, b):
        d = abs((a - b + np.pi) % (2*np.pi) - np.pi)
        return -1.0 + 2.0 * d / np.pi
    a0, a1, b0, b1 = 0.0, np.pi/2, np.pi/4, 3*np.pi/4
    S_local = abs(E_local(a0, b0) - E_local(a0, b1) + E_local(a1, b0) + E_local(a1, b1))
    
    # 4. Mercury: scalar (density-only) cavity sector, PPN gamma = 0, beta = 1
    gr_mercury = 42.98
    scalar_mercury = gr_mercury * (2.0 + 2.0*0.0 - 1.0) / 3.0
    
    # 5. Benchmarks, labelled by where the number comes from
    benchmarks = {
        "Cassini |gamma - 1|": {"theory": "gamma=1 (GR metric typed in); scalar cavity gives gamma=0",
                                 "measured": 2.3e-5, "status": "GR INPUT / scalar sector FAILS"},
        "Mercury Precession (arcsec/cy)": {"theory": f"{gr_mercury} (GR formula); scalar only {scalar_mercury:.2f}",
                                           "measured": 43.00, "status": "GR INPUT / scalar sector FAILS"},
        "Pound-Rebka Redshift": {"theory": 2.46e-15, "measured": 2.50e-15,
                                 "status": "NON-DISCRIMINATING (any metric theory with correct g00)"},
        "GW170817 |c_g - c|/c": {"theory": "c_g = c ASSUMED", "measured": 3.0e-15,
                                 "status": "ASSUMED (lattice anisotropy 17-33% not addressed)"},
        "Bell CHSH Parameter S": {"theory": f"{S_local:.3f} (local vortex model)", "measured": "2.4-2.8 (loophole-free)",
                                  "status": "FAILS as local model; 2.828 only if QM rule is typed in"},
        "Core-Cusp Galaxy Core": {"theory": "soliton core (standard psiDM, Schive 2014)", "measured": "cores",
                                  "status": "PRIOR ART; m~1e-22 eV disfavoured by Lyman-alpha"},
        "Electron mass": {"theory": f"{m_e_predicted*c**2/1.602176634e-13:.6f} MeV", "measured": "0.51099895 MeV",
                          "status": f"EXCLUDED at {mass_sigma:,.0f} sigma (fitted forms reach 42 sigma)"},
    }
    
    print("\n=== AUDITED BENCHMARK TABLE ===")
    for name, b in benchmarks.items():
        print(f"  {name:32s} theory: {str(b['theory']):55s} measured: {str(b['measured']):24s} -> {b['status']}")
    print(f"\n  Electron: 'exponent accuracy' {exponent_accuracy:.3f}% is the error divided by ln(m_P/m_e) = 51.5;")
    print(f"            the actual mass error is {mass_rel_error:+.3e} vs measurement precision ~1.1e-5 (G-limited).")
    print(f"  k_bond = c^4/G = {k_bond:.3e} N  -- a FORCE, not a spring constant (N/m).")
    
    return {
        "l_P": l_P, "m_P": m_P, "mu_P": mu_P, "rho_P": rho_P,
        "k_bond": k_bond, "F_max": F_max,
        "m_e_predicted": m_e_predicted, "m_e_measured": m_e_measured,
        "exponent_accuracy": exponent_accuracy, "mass_rel_error": mass_rel_error,
        "mass_sigma": mass_sigma, "S_local": S_local, "scalar_mercury": scalar_mercury,
        "benchmarks": benchmarks
    }

def plot_master_dashboard(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    
    # -------------------------------------------------------------
    # Panel 1: The 10 Pillars, each with its audited status
    # -------------------------------------------------------------
    ax1 = axs[0, 0]
    ax1.axis('off')
    pillars_text = (
        "=========================================================================\n"
        "THE 10 PILLARS OF USRT -- WITH AUDITED STATUS\n"
        "=========================================================================\n\n"
        "1. SUBSTRATE MEDIUM: mu_P = rho_P c^2 by definition (c is an input).\n"
        "   [IDENTITY] -- and a de Boer quantum liquid has zero shear modulus.\n"
        "2. HCP LATTICE: elastically anisotropic (17-33% in c) -> conflicts with\n"
        "   isotropy bounds; 'k = c^4/G' has units of force. [FAILS AS STATED]\n"
        "3. CAVITATION GRAVITY: u_r = -r_g/r is not a Navier-Cauchy solution;\n"
        "   GP cavity force is screened (exp(-r)/r). [GR METRIC TYPED IN]\n"
        "4. TRAPPED LIGHT: Einstein-box inertia is real physics; loop model gives\n"
        "   spin 1, g = 1 (not 1/2, 2). [PRIOR ART / FAILS g-TEST]\n"
        f"5. ELECTRON MASS: misses by {abs(data['mass_rel_error']):.1e}; fitted version 42 sigma;\n"
        "   look-elsewhere: 62% of random targets get a 'match'. [NUMEROLOGY]\n"
        "6. COSMOGENESIS: Vilenkin tunnelling is standard. [PRIOR ART]\n"
        "7. LIGHT AS SHEAR WAVES: longitudinal branch is GAPLESS; static E needs\n"
        "   unbounded displacement. [OPEN PROBLEM; cf. Levin-Wen]\n"
        "8. RELATIONAL TIME: Page-Wootters 1983. [PRIOR ART, sound]\n"
        "9. DARK SECTOR: psiDM is Hu-Barkana-Gruzinov/Schive; Volovik vacuum.\n"
        "   [PRIOR ART]; SO(10) singlet is a fermion -> cannot form the BEC.\n"
        "10. ENTANGLEMENT: local vortex model computes S = "
        f"{data['S_local']:.3f} (Bell bound).\n"
        "    [FAILS] -- 2.828 appears only when the QM rule is typed in."
    )
    ax1.text(0.01, 0.98, pillars_text, va='top', ha='left', family='monospace', fontsize=8.8,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#2c3e50", lw=1.5))
    
    # -------------------------------------------------------------
    # Panel 2: Empirical Benchmark Scorecard (computed / labelled)
    # -------------------------------------------------------------
    ax2 = axs[0, 1]
    ax2.axis('off')
    scorecard_text = (
        "=========================================================================\n"
        "EMPIRICAL BENCHMARK SCORECARD (AUDITED)\n"
        "=========================================================================\n\n"
        "TEST 1: CASSINI SHAPIRO DELAY  |gamma - 1| <= 2.3e-5\n"
        "   gamma = 1 only because the GR metric is written in by hand.\n"
        "   Scalar cavity alone: gamma = 0          --> [GR INPUT / FAILS]\n\n"
        "TEST 2: MERCURY PERIHELION  43.0 arcsec/cy\n"
        f"   GR formula 42.98; scalar sector {data['scalar_mercury']:.2f}  --> [GR INPUT / FAILS]\n\n"
        "TEST 3: POUND-REBKA REDSHIFT  (2.50 +/- 0.25)e-15\n"
        "   2.46e-15 = gh/c^2, any metric theory      --> [NON-DISCRIMINATING]\n\n"
        "TEST 4: GW170817  |c_g - c|/c <= 3e-15\n"
        "   c_g = c assumed, not derived             --> [ASSUMED]\n\n"
        "TEST 5: BELL CHSH  (QM 2.828; experiment > 2)\n"
        f"   Local vortex model computed: S = {data['S_local']:.3f}   --> [FAILS]\n\n"
        "TEST 6: ELECTRON REST MASS\n"
        f"   'Exponent accuracy' {data['exponent_accuracy']:.3f}% (error / 51.5)\n"
        f"   Mass error {data['mass_rel_error']:+.2e} = {data['mass_sigma']:,.0f} sigma  --> [EXCLUDED]"
    )
    ax2.text(0.01, 0.98, scorecard_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdf2f2", ec="#c0392b", lw=1.5))
    
    # -------------------------------------------------------------
    # Panel 3: What the Theory Still Lacks
    # -------------------------------------------------------------
    ax3 = axs[1, 0]
    ax3.axis('off')
    limits_text = (
        "=========================================================================\n"
        "WHAT THE THEORY STILL LACKS: OPEN PROBLEMS\n"
        "=========================================================================\n\n"
        "1. A MEDIUM THAT IS BOTH A SUPERFLUID AND A SHEAR-RIGID SOLID:\n"
        "   Lambda* = sqrt(28.8) = 5.37 >> 1 means a quantum liquid (mu = 0).\n\n"
        "2. LORENTZ INVARIANCE FROM A LATTICE:\n"
        "   FCC/HCP central-force lattices are anisotropic at ALL wavelengths.\n"
        "   Needs a mechanism (Collins et al. 2004 fine-tuning problem).\n\n"
        "3. ONLY TWO PHOTON POLARIZATIONS:\n"
        "   An elastic medium has a gapless longitudinal mode; need gauge\n"
        "   redundancy (Levin-Wen string nets, Volovik He-3A).\n\n"
        "4. LONG-RANGE 1/r GRAVITY FROM A CAVITY:\n"
        "   GP density depletion decays as exp(-sqrt2 r/xi)/r. A 1/r force needs\n"
        "   a gapless mediator (superflow / Bjerknes forces).\n\n"
        "5. MASS SPECTRUM:\n"
        "   Electron/proton/DM formulas are fits (Nottale, Lenz, Koide/Brannen).\n"
        "   Koide Q = 2/3 holds to 0.4 sigma -- real, unexplained, not derived here."
    )
    ax3.text(0.01, 0.98, limits_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#e74c3c", lw=1.5))
    
    # -------------------------------------------------------------
    # Panel 4: Overall status
    # -------------------------------------------------------------
    ax4 = axs[1, 1]
    ax4.axis('off')
    credibility_text = (
        "=========================================================================\n"
        "OVERALL STATUS (AUDIT)\n"
        "=========================================================================\n\n"
        "VERDICT: A SPECULATIVE RESEARCH PROGRAMME, NOT A DERIVED THEORY\n\n"
        "SOUND INGREDIENTS (mostly prior art, worth citing and building on):\n"
        "   - Analog / emergent gravity in superfluids (Volovik, Unruh, Barcelo)\n"
        "   - Emergent photons from lattice gauge redundancy (Levin-Wen)\n"
        "   - Page-Wootters relational time\n"
        "   - Inertia of confined energy (Einstein's box)\n"
        "   - Fermionic quantisation of Hopf solitons (Krusch-Speight)\n"
        "   - Koide's lepton relation (empirical)\n\n"
        "NOT YET SUPPORTED:\n"
        "   [ ] Dark-energy, singularity, core-cusp claims are prior-art inputs\n"
        "   [ ] Gravity tests pass only where the GR metric was typed in\n"
        "   [ ] Bell violation needs a nonlocal rule that is put in by hand\n"
        "   [ ] Mass 'derivations' are fitted formulas (look-elsewhere effect)\n\n"
        "NEXT STEP: one model, one parameter set, one falsifiable prediction."
    )
    ax4.text(0.01, 0.98, credibility_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fef9e7", ec="#f39c12", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_theory_synthesis.png')
    plt.savefig(output_path, dpi=300)
    print(f"Master synthesis dashboard saved to: {output_path}")
    
    # Copy to artifact directory
    artifact_dir = r'C:\Users\Asta\.gemini\antigravity\brain\cfcab9e6-1707-463d-a5cf-0f6b32f4acb8'
    if os.path.exists(artifact_dir):
        shutil.copy(output_path, os.path.join(artifact_dir, 'master_theory_synthesis.png'))
        print("Copied to artifact directory.")

if __name__ == "__main__":
    data = run_master_synthesis()
    plot_master_dashboard(data)
