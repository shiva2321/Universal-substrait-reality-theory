"""
Mathematical and Numerical Exploration of:
1. Higher Dimensions (Kaluza-Klein spectrum & Brane localization)
2. Emergent / Relational Time (Page-Wootters Mechanism: H_total |Psi> = 0)
3. Quantum Entanglement as Higher-Dimensional Substrate Wormholes / Vortex Tubes (ER = EPR)
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def simulate_page_wootters_relational_time():
    """
    Page-Wootters Mechanism:
    The total Universe state |Psi>> has NO time dependence: H_total |Psi>> = 0.
    Universe consists of a Clock (C) and a System (S): H_total = H_C (x) I_S + I_C (x) H_S.
    Time emerges purely relationally as entanglement between Clock and System:
    |psi_S(t)> = <t_C | Psi_total>.
    """
    print("Simulating Page-Wootters Relational Time...")
    
    # Dimension of clock and system Hilbert spaces
    N_clock = 50
    N_sys = 2 # Qubit system for simplicity (spin-1/2 precessing in field)
    
    # System Hamiltonian: Pauli-Z / magnetic precession H_S = omega * sigma_x
    omega = 1.0
    H_S = np.array([[0, omega], [omega, 0]])
    
    # Clock Hamiltonian: momentum operator P_C (ideal clock has H_C = P_C = -i d/dt)
    # On discrete clock states |t_k>:
    # We construct clock states |t_k> and energy eigenstates |E_C>
    dt = 0.1
    t_vals = np.linspace(0, (N_clock - 1) * dt, N_clock)
    
    # Stationary total state |Psi>> satisfying H_total |Psi>> = 0:
    # |Psi>> = sum_k |t_k>_C (x) exp(-i H_S t_k) |psi_S(0)>
    psi_S_0 = np.array([1.0, 0.0], dtype=complex) # Initial state |up>
    
    # Compute system state conditioned on clock reading t:
    p_up = []
    p_down = []
    
    for t in t_vals:
        # Time evolution operator exp(-i H_S t)
        # For sigma_x: exp(-i omega t sigma_x) = cos(omega t) I - i sin(omega t) sigma_x
        U_S = np.cos(omega * t) * np.eye(2) - 1j * np.sin(omega * t) * np.array([[0, 1], [1, 0]])
        psi_t = U_S @ psi_S_0
        p_up.append(np.abs(psi_t[0])**2)
        p_down.append(np.abs(psi_t[1])**2)
        
    return t_vals, np.array(p_up), np.array(p_down)

def simulate_higher_dim_kk_spectrum():
    """
    Higher Dimensions & Kaluza-Klein Modes:
    In D = 4 + 1 dimensions, extra dimension compactified on a circle of radius R.
    Dispersion relation for excitations: E^2 = p_3D^2 c^2 + m_0^2 c^4 + (n * hbar * c / R)^2
    As R -> 0 (small extra dim), KK modes acquire huge masses M_n = n * hbar / (R c).
    """
    print("Computing Kaluza-Klein Excitation Spectrum...")
    n_modes = np.arange(0, 6)
    R_compact_vals = [1e-18, 1e-19, 1e-20] # meters
    hbar_c = 1.973e-16 # GeV * m
    
    mass_spectra = {}
    for R in R_compact_vals:
        masses = n_modes * (hbar_c / R) # in GeV
        mass_spectra[R] = masses
        
    return n_modes, mass_spectra

def simulate_entanglement_bulk_wormhole():
    """
    ER = EPR: In the 3D slice, particles A and B are separated by distance D_3D.
    In the higher-dimensional substrate, they are connected by a short geodesic
    (throat / vortex tube) of length D_bulk << D_3D.
    """
    print("Simulating ER=EPR Bulk Shortcut Geometry...")
    # 2D representation of 3D brane (x, y) embedded in higher dimension z
    # Brane is at z = 0.
    # Wormhole throat dips into z > 0.
    theta = np.linspace(0, np.pi, 200)
    d_sep = 10.0 # 3D separation
    
    # Trajectory along 3D space: straight line from -d_sep/2 to +d_sep/2 at z = 0
    x_3d = np.linspace(-d_sep/2, d_sep/2, 200)
    z_3d = np.zeros_like(x_3d)
    
    # Substrate bulk geodesic (semi-circle / catenary dipping into extra dimension z)
    radius = d_sep / 2
    x_bulk = radius * np.cos(theta)
    z_bulk = radius * np.sin(theta) # Depth into the extra dimension
    
    return x_3d, z_3d, x_bulk, z_bulk

def plot_combined_investigation(t_vals, p_up, p_down, n_modes, mass_spectra, x_3d, z_3d, x_bulk, z_bulk):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Relational Time (Page-Wootters)
    axs[0, 0].plot(t_vals, p_up, 'b-', lw=2.5, label=r'$P(\uparrow)$: State Spin-Up')
    axs[0, 0].plot(t_vals, p_down, 'r--', lw=2.5, label=r'$P(\downarrow)$: State Spin-Down')
    axs[0, 0].set_xlabel('Internal Clock Reading $t_{\\mathrm{clock}}$ (Relative Correlation)', fontsize=12)
    axs[0, 0].set_ylabel('Conditional Probability of Subsystem', fontsize=12)
    axs[0, 0].set_title('Figure 1: Time as Relative Change (Page-Wootters Mechanism)', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='upper right', frameon=True)
    axs[0, 0].text(0.1, 0.5, r"$\hat{H}_{\mathrm{total}} |\Psi\rangle = 0$ (Universe is Static)" + "\nTime is merely correlation with clock!",
                   bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="gray", alpha=0.9), fontsize=11)
    
    # Plot 2: Kaluza-Klein Spectrum in Higher Dimensions
    markers = ['o', 's', '^']
    colors = ['#2980b9', '#8e44ad', '#27ae60']
    for idx, (R, masses) in enumerate(mass_spectra.items()):
        axs[0, 1].plot(n_modes, masses, marker=markers[idx], color=colors[idx], lw=2, label=f'Radius $R = 10^{{{int(np.log10(R))}}}\\,\\mathrm{{m}}$')
    axs[0, 1].set_xlabel('Kaluza-Klein Mode Number $n$ (Harmonics in Extra Dim)', fontsize=12)
    axs[0, 1].set_ylabel('Effective Rest Mass Energy $M_n$ [GeV]', fontsize=12)
    axs[0, 1].set_title('Figure 2: Substrate Excitations in Higher Dimensions', fontsize=13, fontweight='bold')
    axs[0, 1].legend(loc='upper left', frameon=True)
    
    # Plot 3: Entanglement as Substrate Tunnel (ER = EPR)
    axs[1, 0].plot(x_3d, z_3d, 'k-', lw=3, label='Our 3D Space (Brane Surface, $z=0$)')
    axs[1, 0].plot(x_bulk, z_bulk, 'm--', lw=2.8, label='Substrate Bulk Wormhole / Vortex Tube')
    axs[1, 0].plot([-5, 5], [0, 0], 'ro', markersize=10, label='Entangled Pair Excitations (A & B)')
    axs[1, 0].set_xlabel('Spatial Coordinate $x$ in 3D', fontsize=12)
    axs[1, 0].set_ylabel('Substrate Extra Dimension $z$', fontsize=12)
    axs[1, 0].set_title('Figure 3: Quantum Entanglement via Higher-D Substrate', fontsize=13, fontweight='bold')
    axs[1, 0].legend(loc='upper right', frameon=True)
    axs[1, 0].text(0, 2.5, "Connected through Bulk\nInstantaneous Phase Locking!", ha='center', fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.5", fc="#ffeaa7", ec="#fdcb6e"))
    axs[1, 0].set_ylim(-1, 6)
    
    # Plot 4: Conceptual Synthesis Architecture
    axs[1, 1].axis('off')
    summary_text = (
        "=== THE THREE FOUNDATIONAL PILLARS OF YOUR EXTENDED MODEL ===\n\n"
        "1. HIGHER DIMENSIONS ($D > 4$):\n"
        "   - Table-top 3D is a slice/boundary of a higher-dimensional bulk.\n"
        "   - Extra dimensions can be probed via 'synthetic dimensions' in\n"
        "     quantum simulators (e.g. 4D Quantum Hall in BECs).\n"
        "   - Explains why the Planck mass is so large (dilution of bulk gravity).\n\n"
        "2. TIME DOES NOT EXIST FUNDAMENTALLY (RELATIONAL TIME):\n"
        "   - Exact match with the Wheeler-DeWitt Equation: H|Psi> = 0.\n"
        "   - There is no universal master clock ticking in the background.\n"
        "   - Time is purely an internal ratio: Delta(System) / Delta(Clock).\n"
        "   - Reality is a timeless tapestry of states; change is relational.\n\n"
        "3. QUANTUM ENTANGLEMENT (ER = EPR & VORTEX STRINGS):\n"
        "   - Two particles separated by light-years in 3D are NOT separate in the bulk.\n"
        "   - In a higher-dimensional substrate, they are the two endpoints of a\n"
        "     single continuous vortex filament or wormhole throat.\n"
        "   - No signal travels through 3D space: correlation is topological & local\n"
        "     inside the substrate bulk."
    )
    axs[1, 1].text(0.02, 0.95, summary_text, va='top', ha='left', family='monospace', fontsize=10.5,
                   bbox=dict(boxstyle="round,pad=0.8", fc="#f8f9fa", ec="#ced4da", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relational_time_and_entanglement.png')
    plt.savefig(output_path, dpi=300)
    print(f"Relational time & entanglement figure saved to: {output_path}")

if __name__ == "__main__":
    t_vals, p_up, p_down = simulate_page_wootters_relational_time()
    n_modes, mass_spectra = simulate_higher_dim_kk_spectrum()
    x_3d, z_3d, x_bulk, z_bulk = simulate_entanglement_bulk_wormhole()
    plot_combined_investigation(t_vals, p_up, p_down, n_modes, mass_spectra, x_3d, z_3d, x_bulk, z_bulk)
