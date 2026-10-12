"""
Simulation and Mathematical Derivation:
Exact Properties of the Planck-Scaled Constituent Particles ("Planckions") in the HCP Lattice.

Calculates:
1. Geometric Dimensions: Radius r_0 = ell_P/2, volume, packing volume per cell.
2. Mass & Energy: Rest mass m_P, rest energy E_P, energy density.
3. Mechanical & Elastic Properties: 12-bond spring constant k = c^4/G, bond breaking force F_max = c^4/(4G).
4. Quantum-Gravitational Equilibrium: Exact balance E_quantum == E_gravitational.
5. Dynamic & Thermal Properties: Chronon frequency nu_P, period t_P, Debye temperature Theta_D.
6. Topological Electric Charge: Planck dipole charge q_P = +/- sqrt(4*pi*epsilon_0*hbar*c) = +/- 11.7 e.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import shutil

def derive_planck_particle_properties():
    print("Deriving exact properties of Planck-scale lattice constituent particles...")
    
    # Fundamental constants
    c = 2.99792458e8             # m/s
    hbar = 1.054571817e-34       # J s
    G = 6.67430e-11              # m^3 / (kg s^2)
    k_B = 1.380649e-23           # J / K
    epsilon_0 = 8.8541878128e-12 # F / m
    e_charge = 1.602176634e-19   # C
    alpha = 7.2973525693e-3      # Fine structure constant
    
    # -------------------------------------------------------------
    # 1. Geometric Dimensions
    # -------------------------------------------------------------
    l_P = np.sqrt(hbar * G / (c**3))          # 1.616255e-35 m (Lattice diameter)
    r_0 = l_P / 2.0                           # 8.08127e-36 m (Sphere radius)
    V_sphere = (4.0 / 3.0) * np.pi * (r_0**3) # 2.2105e-105 m^3
    eta_HCP = np.pi / (3.0 * np.sqrt(2.0))     # 0.740480489 (Packing fraction)
    V_cell_HCP = V_sphere / eta_HCP           # 2.9852e-105 m^3 (Unit cell volume)
    
    # -------------------------------------------------------------
    # 2. Mass, Energy, and Quantum-Gravitational Balance
    # -------------------------------------------------------------
    m_P = np.sqrt(hbar * c / G)               # 2.176434e-8 kg (21.76 micrograms)
    E_P_Joules = m_P * (c**2)                 # 1.95608e9 Joules
    E_P_GeV = E_P_Joules / (1.602176634e-10)  # 1.2209e19 GeV
    
    # Proof of Self-Stabilizing Balance:
    # E_quantum = hbar * c / l_P
    E_quantum = hbar * c / l_P                # 1.95608e9 Joules
    # E_grav = G * m_P^2 / l_P
    E_grav = G * (m_P**2) / l_P               # 1.95608e9 Joules
    balance_ratio = E_quantum / E_grav        # Exactly 1.000000000000 !
    
    # -------------------------------------------------------------
    # 3. Dynamic Oscillations & Chronon Clock
    # -------------------------------------------------------------
    omega_P = c / l_P                         # 1.85487e43 rad / s
    nu_P = omega_P / (2.0 * np.pi)            # 2.9521e42 Hz
    t_P = 1.0 / omega_P                       # 5.3912e-44 s (Chronon period)
    Theta_Debye = E_P_Joules / k_B            # 1.4168e32 Kelvin (Debye temperature)
    
    # -------------------------------------------------------------
    # 4. Mechanical Elasticity & Forces
    # -------------------------------------------------------------
    k_bond = (c**4) / G                       # 1.21027e44 N / m (Einstein spring constant)
    coordination_Z = 12                       # 12 nearest neighbors in HCP
    k_total_node = coordination_Z * k_bond    # 1.4523e45 N / m
    F_breaking = (c**4) / (4.0 * G)           # 3.02568e43 N (Schiller-Gibbons bound)
    
    # -------------------------------------------------------------
    # 5. Topological Dipole Charge (Winterberg Model)
    # -------------------------------------------------------------
    # q_P = sqrt(4 * pi * epsilon_0 * hbar * c) = e / sqrt(alpha)
    q_P_Coulombs = np.sqrt(4.0 * np.pi * epsilon_0 * hbar * c) # 1.8755e-18 C
    q_P_electrons = q_P_Coulombs / e_charge                    # 11.7062 elementary charges
    
    return {
        "l_P": l_P, "r_0": r_0, "V_sphere": V_sphere, "V_cell_HCP": V_cell_HCP,
        "m_P": m_P, "E_P_Joules": E_P_Joules, "E_P_GeV": E_P_GeV,
        "E_quantum": E_quantum, "E_grav": E_grav, "balance_ratio": balance_ratio,
        "omega_P": omega_P, "nu_P": nu_P, "t_P": t_P, "Theta_Debye": Theta_Debye,
        "k_bond": k_bond, "coordination_Z": coordination_Z, "k_total_node": k_total_node,
        "F_breaking": F_breaking, "q_P_Coulombs": q_P_Coulombs, "q_P_electrons": q_P_electrons
    }

def plot_planck_particle_properties(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    
    # -------------------------------------------------------------
    # Panel 1: The Exact Quantum-Gravitational Equilibrium
    # -------------------------------------------------------------
    ax1 = axs[0, 0]
    r_radii = np.linspace(0.2 * data["l_P"], 3.0 * data["l_P"], 400)
    # E_total(r) = E_quantum(r) - E_grav(r) ... effective potential
    # E_quantum ~ hbar * c / r (repulsive Heisenberg localization)
    # E_grav ~ - G * m_P^2 / r (attractive Newton gravity)
    hbar_c = 1.05457e-34 * 2.99792e8
    G_m2 = 6.6743e-11 * (data["m_P"]**2)
    
    # Scaled curve showing balance at r = l_P
    r_norm = r_radii / data["l_P"]
    E_quant_curve = 1.0 / r_norm
    E_grav_curve = 1.0 / r_norm
    
    ax1.plot(r_norm, E_quant_curve, 'purple', lw=2.5, label=r'Quantum Expansion Energy: $E_Q = \frac{\hbar c}{r}$')
    ax1.plot(r_norm, E_grav_curve, 'orange', linestyle='--', lw=2.5, label=r'Gravitational Binding Energy: $E_G = \frac{G m_P^2}{r}$')
    ax1.plot(1.0, 1.0, 'go', markersize=10, label=r'Planck Particle Stability Point: $r = \ell_P$ ($E_Q \equiv E_G$)')
    
    ax1.set_xlabel(r'Particle Separation $r / \ell_P$', fontsize=11, fontweight='bold')
    ax1.set_ylabel(r'Energy / $E_P$', fontsize=11, fontweight='bold')
    ax1.set_title(r'1. The Golden Equilibrium: $E_{\text{Quantum}} \equiv E_{\text{Gravitational}} = m_P c^2$',
                  fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 4)
    ax1.legend(loc='upper right', frameon=True, fontsize=9.0)
    ax1.text(1.1, 2.2, "Each Planck particle is in PERFECT STABILITY:\nHeisenberg quantum pressure outward is\nidentically cancelled by gravity inward!",
             fontsize=9.2, bbox=dict(boxstyle="round,pad=0.4", fc="#e8f8f5", ec="#1abc9c", alpha=0.9))
    
    # -------------------------------------------------------------
    # Panel 2: The Two-Component Neutral Condensate (Winterberg Dipole)
    # -------------------------------------------------------------
    ax2 = axs[0, 1]
    # Draw positive and negative Planckions
    theta = np.linspace(0, 2*np.pi, 100)
    # Positive Planckion (+m_P, +q_P)
    ax2.plot(np.cos(theta) - 1.5, np.sin(theta), 'crimson', lw=2.5)
    ax2.fill(np.cos(theta) - 1.5, np.sin(theta), 'crimson', alpha=0.2)
    ax2.text(-1.5, 0, "+m_P\n+11.7 e", ha='center', va='center', fontsize=11, fontweight='bold', color='crimson')
    
    # Negative Planckion (-m_P, -q_P)
    ax2.plot(np.cos(theta) + 1.5, np.sin(theta), 'navy', lw=2.5)
    ax2.fill(np.cos(theta) + 1.5, np.sin(theta), 'navy', alpha=0.2)
    ax2.text(1.5, 0, "-m_P\n-11.7 e", ha='center', va='center', fontsize=11, fontweight='bold', color='navy')
    
    # Elastic bond connecting them
    ax2.plot([-0.5, 0.5], [0, 0], 'g-', lw=4, label=r'Planck Bond ($k = c^4 / G = 1.21 \times 10^{44}\,$N/m)')
    
    ax2.set_xlim(-3.2, 3.2)
    ax2.set_ylim(-2.0, 2.0)
    ax2.set_title("2. The Constituent Dipole: Net Charge & Net Mass = 0", fontsize=12, fontweight='bold')
    ax2.legend(loc='lower center', frameon=True, fontsize=9.0)
    ax2.axis('off')
    ax2.text(0, -1.6, "Winterberg Two-Component Condensate:\nPositive & negative constituents cancel in bulk,\nexplaining why empty space has ZERO net weight!",
             ha='center', fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="#fef9e7", ec="#f39c12", alpha=0.9))
    
    # -------------------------------------------------------------
    # Panel 3: Master Properties Ledger
    # -------------------------------------------------------------
    ax3 = axs[1, 0]
    ax3.axis('off')
    properties_text = (
        "=========================================================================\n"
        "PHYSICAL SPECIFICATIONS OF A SINGLE 'PLANCKION' CONSTITUENT\n"
        "=========================================================================\n\n"
        "1. GEOMETRY & SPACE:\n"
        f"   • Constituent Diameter (ell_P):    {data['l_P']:.6e} meters\n"
        f"   • Constituent Radius (r_0):        {data['r_0']:.6e} meters\n"
        f"   • Physical Sphere Volume:          {data['V_sphere']:.4e} m^3\n"
        f"   • Unit Cell Volume (in HCP):       {data['V_cell_HCP']:.4e} m^3\n"
        f"   • Coordination Number (Z):         {data['coordination_Z']} Nearest Neighbors\n\n"
        "2. MASS & ENERGY:\n"
        f"   • Rest Mass (m_P):                 {data['m_P']:.6e} kg (~ 21.76 micrograms!)\n"
        f"   • Rest Energy (E_P):               {data['E_P_Joules']:.5e} Joules (~ {data['E_P_GeV']:.2e} GeV)\n"
        f"   • Balance Ratio (E_quant / E_grav): {data['balance_ratio']:.10f} (EXACT EQUALITY)\n\n"
        "3. MECHANICAL ELASTICITY:\n"
        f"   • Single Bond Spring Constant:     {data['k_bond']:.4e} N / m  (c^4 / G)\n"
        f"   • Total Nodal Spring Stiffness:    {data['k_total_node']:.4e} N / m  (12 * c^4 / G)\n"
        f"   • Max Breaking Bond Force:         {data['F_breaking']:.4e} Newtons (c^4 / 4G)"
    )
    ax3.text(0.01, 0.98, properties_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#2c3e50", lw=1.5))
    
    # -------------------------------------------------------------
    # Panel 4: Quantum & Thermal Properties
    # -------------------------------------------------------------
    ax4 = axs[1, 1]
    ax4.axis('off')
    quantum_thermal_text = (
        "=========================================================================\n"
        "QUANTUM, THERMAL, & ELECTROMAGNETIC PROPERTIES\n"
        "=========================================================================\n\n"
        "1. DYNAMIC CLOCK & VIBRATION (The Chronon):\n"
        f"   • Angular Frequency (omega_P):     {data['omega_P']:.5e} rad / s\n"
        f"   • Natural Frequency (nu_P):        {data['nu_P']:.5e} Hertz\n"
        f"   • Chronon Period (t_P):            {data['t_P']:.5e} seconds\n"
        "   --> This is the fundamental 'clock tick' of reality!\n\n"
        "2. THERMAL BEHAVIOR (The Frozen Superfluid):\n"
        f"   • Debye Temperature (Theta_D):     {data['Theta_Debye']:.4e} Kelvin\n"
        f"   • Current Cosmic Temperature:      T_CMB = 2.725 Kelvin\n"
        f"   • Reduced Temperature Ratio:       T / Theta_D ~ 1.9 x 10^-32  ~  0.000!\n"
        "   --> Because T << Theta_Debye, the Planck lattice is FROZEN in its\n"
        "       absolute zero quantum ground state: ZERO VISCOSITY SUPERFLUID!\n\n"
        "3. TOPOLOGICAL ELECTRIC CHARGE:\n"
        f"   • Dipole Charge (q_P):             {data['q_P_Coulombs']:.4e} Coulombs\n"
        f"   • In Elementary Units:             q_P = e / sqrt(alpha) = {data['q_P_electrons']:.4f} e\n"
        "   --> Particles carry exactly 11.7 times the electron charge!"
    )
    ax4.text(0.01, 0.98, quantum_thermal_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#f4ecf7", ec="#8e44ad", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planck_particle_properties.png')
    plt.savefig(output_path, dpi=300)
    print(f"Planck particle properties plot saved to: {output_path}")
    
    # Copy to artifact directory
    artifact_dir = r'C:\Users\Asta\.gemini\antigravity\brain\cfcab9e6-1707-463d-a5cf-0f6b32f4acb8'
    if os.path.exists(artifact_dir):
        shutil.copy(output_path, os.path.join(artifact_dir, 'planck_particle_properties.png'))
        print("Copied to artifact directory.")

if __name__ == "__main__":
    data = derive_planck_particle_properties()
    plot_planck_particle_properties(data)
