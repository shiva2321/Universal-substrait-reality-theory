"""
Simulation and Mathematical Modeling of:
1. Quantum Tunneling from 'Nothing' (Vilenkin Instanton / Hartle-Hawking No-Boundary).
2. The Pre-Geometric Condensation Phase Transition (Symmetric Phase -> Substrate Vacuum VEV).
3. Spacetime from Quantum Information (Ryu-Takayanagi Entanglement Distance).
"""

import numpy as np
import matplotlib.pyplot as plt

def simulate_vilenkin_tunneling_from_nothing():
    """
    Vilenkin Quantum Creation of the Universe from 'Nothing':
    De Sitter minisuperspace potential V(a) = a^2 - (Lambda / 3) * a^4.
    A universe of scale factor a tunnels from a = 0 (no space, no geometry)
    through the classically forbidden Euclidean barrier to a_0 = sqrt(3 / Lambda).
    Tunneling probability P ~ exp(- 2 * S_Euclidean / hbar).
    """
    print("Simulating quantum tunneling from 'Nothing'...")
    a_vals = np.linspace(0.0, 2.5, 400) # scale factor / substrate radius
    Lambda = 1.0 # cosmological constant / substrate expansion parameter
    
    # Minisuperspace effective potential
    V_a = a_vals**2 - (Lambda / 3.0) * a_vals**4
    
    # Turning point / nucleation radius
    a_0 = np.sqrt(3.0 / Lambda)
    
    return a_vals, V_a, a_0

def simulate_condensation_phase_transition():
    """
    Birth of the Substrate as a Cosmic Condensation (Symmetry Breaking):
    Free energy F(Phi, T) = alpha * (T - T_c) * |Phi|^2 + beta * |Phi|^4.
    At T > T_c (Pre-geometric phase): Minimum at |Phi| = 0 (No substrate, no metric).
    At T < T_c (Condensation): The substrate condenses with non-zero vacuum expectation
    value v_0 = sqrt(alpha * (T_c - T) / (2 * beta)).
    """
    print("Simulating pre-geometric condensation phase transition...")
    phi_vals = np.linspace(-2.5, 2.5, 300)
    
    # 3 temperatures: Above T_c, at T_c, below T_c
    F_hot = 1.5 * (phi_vals**2) + 0.3 * (phi_vals**4)      # T > T_c (Unbroken, no substrate)
    F_critical = 0.0 * (phi_vals**2) + 0.3 * (phi_vals**4) # T = T_c (Critical point)
    F_cold = - 1.2 * (phi_vals**2) + 0.3 * (phi_vals**4)   # T < T_c (Substrate is born: VEV v_0)
    
    # Minimum for F_cold
    v_0 = np.sqrt(1.2 / (2.0 * 0.3))
    
    return phi_vals, F_hot, F_critical, F_cold, v_0

def simulate_spacetime_from_entanglement():
    """
    Van Raamsdonk / Ryu-Takayanagi: Spacetime emergent from Entanglement Entropy.
    Distance d(A, B) between two regions in the substrate scales inversely with
    their mutual quantum entanglement I(A: B):
    d(A, B) ~ - log(I(A: B)).
    When entanglement goes to zero (I -> 0), distance diverges to infinity (space tears apart).
    """
    print("Simulating emergence of substrate distance from quantum entanglement...")
    mutual_information = np.logspace(-3, 1, 300)
    # Emergent spatial distance
    d_spacetime = - np.log(mutual_information / np.max(mutual_information) + 1e-4)
    
    return mutual_information, d_spacetime

def plot_origin_of_substrate(a_vals, V_a, a_0, phi_vals, F_hot, F_crit, F_cold, v_0, I_mut, d_space):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Quantum Tunneling from Nothing (Vilenkin Instanton)
    axs[0, 0].plot(a_vals, V_a, 'r-', lw=2.5, label='Minisuperspace Potential $V(a)$')
    axs[0, 0].axhline(0, color='gray', linestyle='--', lw=1.2)
    axs[0, 0].axvspan(0, a_0, color='red', alpha=0.15, label='Classically Forbidden Barrier (No Geometry)')
    axs[0, 0].plot([0, a_0], [0, 0], 'bo', markersize=8)
    axs[0, 0].annotate(r'Nothingness ($a = 0$)', xy=(0, 0), xytext=(10, 20), textcoords='offset points',
                       arrowprops=dict(arrowstyle="->", color='blue'), fontsize=10, fontweight='bold')
    axs[0, 0].annotate(r'Substrate Nucleation ($a = a_0$)', xy=(a_0, 0), xytext=(10, 20), textcoords='offset points',
                       arrowprops=dict(arrowstyle="->", color='green'), fontsize=10, fontweight='bold')
    axs[0, 0].set_xlabel('Substrate Scale / Radius $a$', fontsize=12)
    axs[0, 0].set_ylabel('Effective Potential $V(a)$', fontsize=12)
    axs[0, 0].set_title(r'1. Quantum Tunneling from "Nothing" (Vilenkin Instanton)', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='lower left', frameon=True)
    axs[0, 0].text(0.3, -0.6, "Spontaneous quantum leap across Euclidean barrier:\nUniverse pops into being without prior time!",
                   fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="red", alpha=0.9))
    
    # Subplot 2: Cosmic Condensation (Phase Transition)
    axs[0, 1].plot(phi_vals, F_hot, 'b--', lw=2.0, label='Pre-Geometric Hot Phase ($T > T_c$, $\\Phi = 0$)')
    axs[0, 1].plot(phi_vals, F_cold, 'purple', lw=2.8, label=r'Substrate Vacuum ($T < T_c$, $|\Phi| = v_0$)')
    axs[0, 1].plot([-v_0, v_0], [np.min(F_cold), np.min(F_cold)], 'go', markersize=10, label=r'True Vacuum Ground State ($v_0 = \sqrt{\rho_0}$)')
    axs[0, 1].set_xlabel(r'Substrate Order Parameter $\Phi$', fontsize=12)
    axs[0, 1].set_ylabel('Cosmic Free Energy Potential $F(\\Phi)$', fontsize=12)
    axs[0, 1].set_title('2. The Cosmic Condensation Event (Substrate "Freezing")', fontsize=13, fontweight='bold')
    axs[0, 1].legend(loc='upper center', frameon=True, fontsize=10)
    axs[0, 1].text(0, -0.8, "Substrate 'condensed' into existence,\ncreating space and vacuum density!",
                   ha='center', fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="purple", alpha=0.9))
    
    # Subplot 3: Spacetime from Quantum Information (Van Raamsdonk)
    axs[1, 0].semilogx(I_mut, d_space, 'g-', lw=2.5, label='Emergent Spatial Distance $d(A, B)$')
    axs[1, 0].set_xlabel('Mutual Quantum Entanglement $I(A:B)$ [Log Scale]', fontsize=12)
    axs[1, 0].set_ylabel('Effective Distance in Substrate', fontsize=12)
    axs[1, 0].set_title(r'3. "It from Bit": Substrate as Pure Quantum Entanglement', fontsize=13, fontweight='bold')
    axs[1, 0].legend(loc='upper right', frameon=True)
    axs[1, 0].text(1e-2, 6.0, "High Entanglement = Close in Space\nZero Entanglement = Space Tears Apart!\nSubstrate IS quantum information.",
                   fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="#e8f8f5", ec="#1abc9c", alpha=0.9))
    
    # Subplot 4: Synthesis Architecture
    axs[1, 1].axis('off')
    summary_text = (
        "=== THE 3 SCIENTIFIC ANSWERS TO: WHERE DID IT COME FROM? ===\n\n"
        "1. THE TEMPORAL FALLACY (Hawking's North Pole):\n"
        "   - Asking 'what happened BEFORE the substrate?' is like asking\n"
        "     'what is north of the North Pole?'.\n"
        "   - Time is an internal relational property OF the substrate.\n"
        "   - There was NO 'time before' the substrate existed!\n\n"
        "2. QUANTUM TUNNELING FROM NOTHING (Vilenkin & Hartle-Hawking):\n"
        "   - In quantum gravity, 'Nothing' (zero geometry, zero matter) is\n"
        "     unstable to quantum tunneling.\n"
        "   - The substrate spontaneously tunneled into existence as a\n"
        "     metastable ground state droplet via Euclidean instantons.\n\n"
        "3. THE CONDENSATION PHASE TRANSITION (The Cosmic Freeze):\n"
        "   - Before our substrate, reality was a hot, symmetric,\n"
        "     dimensionless quantum soup.\n"
        "   - Just as steam condenses into liquid water, reality underwent\n"
        "     a phase transition, condensing into the superfluid substrate!\n\n"
        "4. 'IT FROM BIT' (Pure Quantum Information):\n"
        "   - The substrate is NOT physical 'stuff' or matter.\n"
        "   - The substrate is the geometric projection of entangled quantum\n"
        "     qubits in abstract Hilbert space (Van Raamsdonk / Susskind)."
    )
    axs[1, 1].text(0.02, 0.98, summary_text, va='top', ha='left', family='monospace', fontsize=9.8,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#bdc3c7", lw=1.5))
    
    plt.tight_layout()
    output_path = r'f:\Reality_theory\origin_of_substrate.png'
    plt.savefig(output_path, dpi=300)
    print(f"Origin of substrate plots saved to: {output_path}")

if __name__ == "__main__":
    a_vals, V_a, a_0 = simulate_vilenkin_tunneling_from_nothing()
    phi_vals, F_hot, F_crit, F_cold, v_0 = simulate_condensation_phase_transition()
    I_mut, d_space = simulate_spacetime_from_entanglement()
    plot_origin_of_substrate(a_vals, V_a, a_0, phi_vals, F_hot, F_crit, F_cold, v_0, I_mut, d_space)
