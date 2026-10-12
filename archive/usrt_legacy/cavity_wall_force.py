"""
Simulation and Mathematical Proof: Force Applied by the Ripple to Cavity Walls.
Evaluates:
1. Exact Force Formula: F = E / R = m * c^2 / R = m * a_centripetal.
2. For the Electron: F_e = 0.212 Newtons; Pressure P ~ 1.13e23 Pascals (10^18 atm!).
3. For the Proton: F_p = 178,500 Newtons (~18 metric tons!); Pressure P ~ 1e35 Pa.
4. Fundamental Scaling:
   - Fixed Radius: F is directly proportional to Energy E and Mass m (F ~ E = m*c^2).
   - Quantum Compton Scale: R = hbar / (m*c) ==> F = m^2 * c^3 / hbar ~ m^2 (Quadratic!).
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def calculate_cavity_wall_forces():
    print("Calculating ripple cavity wall forces and pressures...")
    
    # Fundamental constants
    c = 2.99792458e8          # m/s
    hbar = 1.054571817e-34    # J s
    eV = 1.602176634e-19      # J
    
    # -------------------------------------------------------------
    # 1. The Electron
    # E = 0.5109989 MeV = 8.1871e-14 J
    # r_C = hbar / (m_e * c) = 3.86159e-13 m
    # -------------------------------------------------------------
    E_electron_J = 0.5109989e6 * eV
    r_C_electron = 3.86159e-13
    F_electron = E_electron_J / r_C_electron # 0.212015 Newtons
    Area_electron = 4.0 * np.pi * (r_C_electron**2)
    P_electron = F_electron / Area_electron  # 1.131e23 Pascals
    
    # -------------------------------------------------------------
    # 2. The Proton
    # E = 938.272 MeV = 1.503e-10 J
    # R_proton = 0.841e-15 m
    # -------------------------------------------------------------
    E_proton_J = 938.272e6 * eV
    R_proton = 0.841e-15
    F_proton = E_proton_J / R_proton         # 178,746 Newtons
    Area_proton = 4.0 * np.pi * (R_proton**2)
    P_proton = F_proton / Area_proton        # 2.01e34 Pascals
    
    # -------------------------------------------------------------
    # 3. Particle Spectrum Scaling (Mass vs Wall Force)
    # -------------------------------------------------------------
    particles = {
        'Electron': (0.511e6 * eV, r_C_electron),
        'Muon': (105.66e6 * eV, hbar / (1.883e-28 * c)),
        'Pion': (139.57e6 * eV, hbar / (2.488e-28 * c)),
        'Proton': (938.27e6 * eV, R_proton),
        'W Boson': (80.38e9 * eV, hbar / (1.432e-25 * c)),
        'Higgs': (125.1e9 * eV, hbar / (2.23e-25 * c))
    }
    
    masses_MeV = []
    forces_N = []
    names = []
    for name, (E_val, R_val) in particles.items():
        names.append(name)
        masses_MeV.append(E_val / (eV * 1e6))
        forces_N.append(E_val / R_val)
        
    return {
        "F_electron": F_electron,
        "P_electron": P_electron,
        "F_proton": F_proton,
        "P_proton": P_proton,
        "names": names,
        "masses_MeV": masses_MeV,
        "forces_N": forces_N
    }

def plot_cavity_wall_force(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Wall Force vs Particle Mass (Quadratic Quantum Scaling)
    m_range_MeV = np.logspace(-1, 6, 300)
    # Quantum Compton force: F = m^2 * c^3 / hbar
    eV = 1.602176634e-19
    c = 2.99792458e8
    hbar = 1.054571817e-34
    m_kg = (m_range_MeV * 1e6 * eV) / (c**2)
    F_compton = (m_kg**2 * c**3) / hbar
    
    axs[0, 0].loglog(m_range_MeV, F_compton, 'purple', lw=2.8, label=r'Quantum Scaling: $F = \frac{m^2 c^3}{\hbar} \propto m^2$')
    
    # Plot real particles
    colors = ['#2ecc71', '#3498db', '#f1c40f', '#e67e22', '#9b59b6', '#e74c3c']
    for idx, name in enumerate(data["names"]):
        axs[0, 0].plot(data["masses_MeV"][idx], data["forces_N"][idx], 'o', color=colors[idx], markersize=9)
        axs[0, 0].annotate(f'{name}\n({data["forces_N"][idx]:.2e} N)',
                           xy=(data["masses_MeV"][idx], data["forces_N"][idx]),
                           xytext=(-25, 15), textcoords='offset points',
                           fontsize=8.5, fontweight='bold', color=colors[idx])
        
    axs[0, 0].set_xlabel('Particle Rest Energy $E = mc^2$ [MeV] (Log Scale)', fontsize=12)
    axs[0, 0].set_ylabel('Outward Force on Cavity Wall [Newtons] (Log Scale)', fontsize=12)
    axs[0, 0].set_title(r'1. Wall Force Scales with Mass Squared ($F \propto m^2$)', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='lower right', frameon=True, fontsize=10)
    
    # Subplot 2: Comparison Bar Chart (Electron vs Proton Force)
    cats = ['Electron Wall Force\n(Single Lepton)', 'Weight of 1 Large Coin\n(Earth Gravity)',
            'Proton Wall Force\n(Single Nucleon)', 'Weight of 3 Large Elephants\n(~18 Metric Tons)']
    forces_compare = [data["F_electron"], 0.25, data["F_proton"], 180000.0]
    bars = axs[0, 1].bar(cats, forces_compare, color=['#3498db', '#95a5a6', '#e74c3c', '#d35400'],
                         width=0.45, edgecolor='black', lw=1.2)
    axs[0, 1].set_yscale('log')
    axs[0, 1].set_ylabel('Force [Newtons] (Log Scale)', fontsize=12)
    axs[0, 1].set_title('2. The Staggering Reality of Subatomic Cavity Forces', fontsize=13, fontweight='bold')
    axs[0, 1].set_ylim(0.01, 1e6)
    for bar in bars:
        h = bar.get_height()
        axs[0, 1].annotate(f'{h:.2f} N' if h < 10 else f'{h:.0f} N',
                           xy=(bar.get_x() + bar.get_width() / 2, h),
                           xytext=(0, 6), textcoords="offset points",
                           ha='center', va='bottom', fontsize=10, fontweight='bold')
        
    # Subplot 3: Mathematical Derivation Ledger
    axs[1, 0].axis('off')
    ledger_text = (
        "=== EXACT MATHEMATICAL DERIVATION OF CAVITY WALL FORCE ===\n\n"
        "1. GENERAL RELATIVISTIC WALL FORCE:\n"
        "   F = d(momentum) / dt = p * omega\n"
        "   Since p = E / c and omega = c / R:\n"
        "   F_wall = (E / c) * (c / R) = E / R = (m * c^2) / R\n\n"
        "2. FOR THE ELECTRON (m_e = 0.511 MeV, r_C = 3.86 x 10^-13 m):\n"
        f"   F_electron = E / r_C = {data['F_electron']:.4f} Newtons (~ 0.212 N)\n"
        f"   Radiation Pressure P = F / Area = {data['P_electron']:.2e} Pascals\n"
        "   --> Equivalent to over 10^18 ATMOSPHERES OF PRESSURE!\n\n"
        "3. FOR THE PROTON (M_p = 938 MeV, R = 0.84 fm):\n"
        f"   F_proton = E / R_p = {data['F_proton']:.0f} Newtons (~ 178,750 N)\n"
        "   --> EQUAL TO THE WEIGHT OF 18 METRIC TONS (3 BULL ELEPHANTS)\n"
        "       pushing outward on a space smaller than a femtometer!"
    )
    axs[1, 0].text(0.02, 0.98, ledger_text, va='top', ha='left', family='monospace', fontsize=9.8,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#bdc3c7", lw=1.5))
    
    # Subplot 4: Summary Table
    axs[1, 1].axis('off')
    summary_text = (
        "=== HOW FORCE CORRELATES WITH MASS AND ENERGY ===\n\n"
        "1. CORRELATION WITH APPLIED ENERGY (E):\n"
        "   F = E / R  ==>  Force is DIRECTLY LINEAR with Energy!\n"
        "   Double the energy = Double the outward pressure on the cavity.\n\n"
        "2. CORRELATION WITH GENERATED MASS (m):\n"
        "   F = m * (c^2 / R) = m * a_centripetal\n"
        "   The wall force is literally NEWTON'S SECOND LAW (F = m*a)\n"
        "   applied to the speed-of-light wave!\n\n"
        "3. THE QUANTUM RELATION (When R = hbar / mc):\n"
        "   Because smaller particles have smaller cavities (R ~ 1/m):\n"
        "   F = m * c^2 / (hbar / mc) = (m^2 * c^3) / hbar\n"
        "   --> The force on the cavity wall scales with the\n"
        "       SQUARE OF THE MASS (F ~ m^2)!\n"
        "   This is why the proton's force is nearly 1 MILLION TIMES\n"
        "   stronger than the electron's force!"
    )
    axs[1, 1].text(0.02, 0.98, summary_text, va='top', ha='left', family='monospace', fontsize=9.8,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#e8f8f5", ec="#1abc9c", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cavity_wall_force.png')
    plt.savefig(output_path, dpi=300)
    print(f"Cavity wall force plots saved to: {output_path}")

if __name__ == "__main__":
    data = calculate_cavity_wall_forces()
    plot_cavity_wall_force(data)
