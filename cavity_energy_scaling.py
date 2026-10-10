"""
Simulation and Mathematical Modeling of:
1. Minimum Energy Required for Substrate Cavity (Virtual vs. Permanent 1.022 MeV vs. Planck).
2. The Correlation Between Energy E and the Well Profile:
   - Well Depth Phi(r) = - G * E / (c^2 * r) (Linear with E).
   - Compton-Schwarzschild Radius Turnaround: R(E) = hbar*c / E + 2*G*E / c^4.
3. 2D/3D Cross-Sections of Cavity Wells at Increasing Energy Levels.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def calculate_energy_cavity_scaling():
    print("Computing energy vs. cavity well scaling relations...")
    
    # Fundamental constants
    G = 6.67430e-11      # m^3 / (kg s^2)
    c = 2.99792458e8     # m/s
    hbar = 1.054571817e-34 # J s
    eV = 1.602176634e-19 # J
    
    # 1. Compton-Schwarzschild Duality (Cavity Radius vs Energy)
    # Energy span from 10^-3 eV to 10^30 eV (spanning 33 orders of magnitude)
    log_E_eV = np.linspace(-3, 30, 400)
    E_joules = (10.0**log_E_eV) * eV
    
    # Quantum Compton radius: R_quantum = hbar * c / E
    R_compton = (hbar * c) / E_joules
    
    # Classical Schwarzschild cavity radius: R_grav = 2 * G * E / c^4
    R_schwarzschild = (2.0 * G * E_joules) / (c**4)
    
    # Total effective cavity boundary radius (Generalized Uncertainty Principle)
    R_total_cavity = R_compton + R_schwarzschild
    
    # Minimum turning point (The Planck Scale)
    E_planck_J = np.sqrt((hbar * c**5) / (2.0 * G))
    E_planck_eV = E_planck_J / eV
    l_planck = np.sqrt((hbar * G) / (c**3))
    
    # 2. Radial Potential Well Profiles for 4 Different Energy Multipliers
    r_axis = np.linspace(0.2, 5.0, 300)
    energies_relative = [1.0, 2.0, 5.0, 10.0]
    cavity_profiles = {}
    for E_rel in energies_relative:
        # Profile: Phi(r) = - (E_rel) / (r + 0.3)
        cavity_profiles[E_rel] = - (E_rel) / (r_axis + 0.3)
        
    return {
        "log_E_eV": log_E_eV,
        "R_compton": R_compton,
        "R_schwarzschild": R_schwarzschild,
        "R_total_cavity": R_total_cavity,
        "E_planck_eV": E_planck_eV,
        "l_planck": l_planck,
        "r_axis": r_axis,
        "cavity_profiles": cavity_profiles
    }

def plot_cavity_energy_scaling(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Cavity Radius vs Energy (The Compton-Schwarzschild "V" Curve)
    log_E = data["log_E_eV"]
    axs[0, 0].loglog(10.0**log_E, data["R_total_cavity"], 'purple', lw=3, label=r'Total Cavity Radius $R(E) = \frac{\hbar c}{E} + \frac{2GE}{c^4}$')
    axs[0, 0].loglog(10.0**log_E, data["R_compton"], 'b--', lw=1.8, label=r'Quantum Regime ($R \propto 1/E$, Compton Wave)')
    axs[0, 0].loglog(10.0**log_E, data["R_schwarzschild"], 'r--', lw=1.8, label=r'Gravitational Regime ($R \propto E$, Black Hole Horizon)')
    
    # Mark Planck Point
    axs[0, 0].plot(data["E_planck_eV"], data["l_planck"] * np.sqrt(2), 'yo', markersize=10, markeredgecolor='k', label='The Planck Turning Point')
    axs[0, 0].annotate(r'Planck Minimum Scale ($\ell_P \approx 10^{-35}\,\mathrm{m}$)' + '\n' + r'$E_{\mathrm{Planck}} \approx 1.22 \times 10^{19}\,\mathrm{eV}$',
                       xy=(data["E_planck_eV"], data["l_planck"] * np.sqrt(2)),
                       xytext=(20, 30), textcoords='offset points',
                       arrowprops=dict(arrowstyle="->", color='black', lw=1.5),
                       fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffeaa7", ec="#fdcb6e"))
    
    # Mark Electron (1.022 MeV)
    E_electron = 1.022e6
    R_electron = (1.054e-34 * 3e8) / (E_electron * 1.602e-19)
    axs[0, 0].plot(E_electron, R_electron, 'go', markersize=9)
    axs[0, 0].annotate('Permanent Matter Threshold\n(Electron Pair: 1.022 MeV)',
                       xy=(E_electron, R_electron), xytext=(-60, 25), textcoords='offset points',
                       arrowprops=dict(arrowstyle="->", color='green', lw=1.5),
                       fontsize=9.0, fontweight='bold', color='green')
    
    axs[0, 0].set_xlabel('Excitation Energy $E$ [eV] (Log Scale)', fontsize=12)
    axs[0, 0].set_ylabel('Cavity Radius $R$ [meters] (Log Scale)', fontsize=12)
    axs[0, 0].set_title('1. Cavity Size vs Energy: The Quantum-Gravitational Turnaround', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='lower left', frameon=True, fontsize=9.5)
    axs[0, 0].set_ylim(1e-36, 1e10)
    
    # Subplot 2: Cavity Well Depth vs Energy
    r_ax = data["r_axis"]
    colors = ['#3498db', '#2ecc71', '#e67e22', '#e74c3c']
    for idx, (E_mult, prof) in enumerate(data["cavity_profiles"].items()):
        axs[0, 1].plot(r_ax, prof, color=colors[idx], lw=2.5, label=f'Energy = {E_mult:.0f}x ($E_0$)')
        axs[0, 1].fill_between(r_ax, prof, 0, color=colors[idx], alpha=0.08)
        
    axs[0, 1].set_xlabel('Radial Distance from Core $r / r_0$', fontsize=12)
    axs[0, 1].set_ylabel(r'Cavity Gravitational Potential $\Phi(r)$', fontsize=12)
    axs[0, 1].set_title(r'2. Well Depth $\Phi(r) \propto -E$: Linear Depth Scaling', fontsize=13, fontweight='bold')
    axs[0, 1].legend(loc='lower right', frameon=True, fontsize=10)
    axs[0, 1].text(2.0, -8.0, "Exact Linear Correlation:\nDouble the Energy (2E) = Double the Depth!\nTen times Energy (10E) = 10x Deeper Hole!",
                   fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="red", alpha=0.9))
    
    # Subplot 3: 2D Contour Map of Cavity Deepening
    X, Y = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
    R_2D = np.sqrt(X**2 + Y**2) + 0.3
    # High energy cavity
    Phi_2D = - 5.0 / R_2D
    im3 = axs[1, 0].imshow(Phi_2D, extent=[-3, 3, -3, 3], cmap='cividis', vmin=-10, vmax=0)
    contours = axs[1, 0].contour(X, Y, Phi_2D, levels=8, colors='cyan', alpha=0.7)
    axs[1, 0].clabel(contours, inline=True, fontsize=8, fmt='%.1f')
    axs[1, 0].set_title('3. Equipotential Contour of Substrate Cavity Well', fontsize=13, fontweight='bold')
    axs[1, 0].set_xlabel('Spatial Dimension X', fontsize=11)
    axs[1, 0].set_ylabel('Spatial Dimension Y', fontsize=11)
    plt.colorbar(im3, ax=axs[1, 0], fraction=0.046, pad=0.04, label=r'Well Depth $\Phi_{\mathrm{well}}$')
    
    # Subplot 4: Summary Table
    axs[1, 1].axis('off')
    summary_text = (
        "=== QUANTITATIVE CORRELATION SUMMARY ===\n\n"
        "1. WHAT IS THE MINIMUM ENERGY NEEDED?\n"
        "   - VIRTUAL CAVITY (Fluctuation): Any infinitesimal E > 0\n"
        "     survives for Heisenberg time Delta_t <= hbar / (2*E).\n"
        "   - PERMANENT SELF-SUSTAINING CAVITY (Matter Knot):\n"
        "     E_min = 2 * m_e * c^2 = 1.022 MeV (Electron-positron threshold).\n"
        "     Below 1.022 MeV, the cavity unzips and radiates away as light!\n"
        "   - BLACK HOLE CAVITY (Complete Substrate Void):\n"
        "     E_planck = 1.22 x 10^19 GeV (Cavity depth reaches 100%).\n\n"
        "2. WHAT IS THE CORRELATION WITH ENERGY E?\n"
        "   - WELL DEPTH IS STRICTLY LINEAR:\n"
        "     Phi(r) = - G * E / (c^2 * r)  ==>  Depth ~ E\n"
        "     Twice the energy = Twice as deep well.\n\n"
        "   - CAVITY RADIUS FOLLOWS A V-SHAPED DUALITY:\n"
        "     a) Below Planck Scale (Quantum): R ~ 1 / E\n"
        "        More energy squeezes the wave into a SMALLER, tighter cavity.\n"
        "     b) Above Planck Scale (Gravity): R ~ E\n"
        "        More energy expands the event horizon into a WIDER cavity!\n"
        "     c) Turning Point: Exactly at the Planck length l_P ~ 10^-35 m!"
    )
    axs[1, 1].text(0.02, 0.98, summary_text, va='top', ha='left', family='monospace', fontsize=9.8,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#bdc3c7", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cavity_energy_scaling.png')
    plt.savefig(output_path, dpi=300)
    print(f"Cavity energy scaling plots saved to: {output_path}")

if __name__ == "__main__":
    data = calculate_energy_cavity_scaling()
    plot_cavity_energy_scaling(data)
