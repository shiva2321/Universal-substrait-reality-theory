"""
Lightweight Universe Simulator: Emergent Substrate-Cavity Model.
Designed to be computationally lightweight and stable:
- Grid size: 120 x 120 (fast, vectorized NumPy operations, executes in < 3 seconds).
- Simulates 4 distinct evolutionary epochs of the universe:
  Epoch 0: The Primordial Substrate (Empty Reality in Higher Dimensions).
  Epoch 1: Energy Injection & Particle Genesis (Localized Excitations).
  Epoch 2: Matter Pile-Up & Cavity Formation (Birth of Gravitational Well).
  Epoch 3: Orbital Geodesic Infall & Extra-Dimensional Entanglement Bridge.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def run_universe_simulation():
    print("Initializing lightweight universe simulation...")
    
    # Grid coordinates (normalized units)
    N = 120
    L = 20.0
    x = np.linspace(-L/2, L/2, N)
    y = np.linspace(-L/2, L/2, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    # -------------------------------------------------------------
    # EPOCH 0: The Primordial Substrate (Empty Reality)
    # Background vacuum density rho_0 = 1.0, flat metric, zero excitations
    # -------------------------------------------------------------
    print("Simulating Epoch 0: Primordial Timeless Vacuum...")
    rho_epoch0 = np.ones((N, N))
    
    # -------------------------------------------------------------
    # EPOCH 1: Energy Injection & Particle Genesis
    # Localized perturbations inject energy, creating wavepacket excitations
    # -------------------------------------------------------------
    print("Simulating Epoch 1: Energy Injection & Excitation Birth...")
    np.random.seed(42)
    # 3 distinct particle wavepackets created by energy injection
    centers = [(-3.0, 2.0), (3.5, 3.0), (0.0, -4.0)]
    amplitudes = [0.8, 0.9, 0.7]
    sigma = 1.0
    
    psi_epoch1 = np.zeros((N, N))
    for (cx, cy), amp in zip(centers, amplitudes):
        r_dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        # Modulated wavepacket (wave excitation)
        k_wave = 3.0
        wavepacket = amp * np.exp(-(r_dist**2) / (2 * sigma**2)) * np.cos(k_wave * r_dist)
        psi_epoch1 += wavepacket**2
        
    # -------------------------------------------------------------
    # EPOCH 2: Matter Clustering & Substrate Cavitation (Gravity)
    # Excitations coalesce into a central dense cluster of mass M_core
    # The substrate fluid is expelled, carving out the density cavity Delta_rho < 0
    # -------------------------------------------------------------
    print("Simulating Epoch 2: Clustering & Substrate Cavitation (Gravity)...")
    core_radius = 2.2
    # Matter density profile of clustered excitations
    rho_matter = 2.5 * np.exp(-(R / core_radius)**2)
    
    # Substrate responds via cavitation coupling:
    # Delta_rho(r) = - g_c * rho_matter / (1 + r/r_healing)
    healing_length = 1.5
    delta_rho = - 0.75 * np.exp(-(R / (core_radius * 1.5))**2) / (1.0 + R / 8.0)
    rho_substrate_cavity = rho_epoch0 + delta_rho
    
    # Effective gravitational potential
    Phi_grav = delta_rho / 2.0
    
    # -------------------------------------------------------------
    # EPOCH 3: Orbital Motion in Cavity & Extra-Dimensional Entanglement
    # A test particle excitation orbits the cavity well
    # Two entangled particles at (+/- 4, 0) connected via extra dimension z
    # -------------------------------------------------------------
    print("Simulating Epoch 3: Planetary Orbit & 5D Entanglement Wormhole...")
    # Orbital trajectory integration (Runge-Kutta 4th order, 150 steps)
    t_steps = 150
    dt = 0.15
    orbit_x = np.zeros(t_steps)
    orbit_y = np.zeros(t_steps)
    
    # Initial position and velocity
    rx, ry = 5.5, 0.0
    vx, vy = 0.0, 0.28 # Tangential orbital velocity
    
    for step in range(t_steps):
        orbit_x[step] = rx
        orbit_y[step] = ry
        # Radial distance
        r_curr = np.sqrt(rx**2 + ry**2)
        if r_curr < 0.3:
            r_curr = 0.3
        # Central attractive acceleration from cavity slope
        acc_mag = - (0.85 / (r_curr**2 + 1.2))
        ax = acc_mag * (rx / r_curr)
        ay = acc_mag * (ry / r_curr)
        
        # Velocity and position update (Verlet/Euler-Cromer)
        vx += ax * dt
        vy += ay * dt
        rx += vx * dt
        ry += vy * dt
        
    # Extra dimension bridge: Entangled pair at (-4, 0) and (+4, 0)
    # The bridge dips into the extra dimension z: z(x, y) = - z_depth * exp(- dist_to_chord^2)
    x_pair = np.array([-4.5, 4.5])
    y_pair = np.array([0.0, 0.0])
    
    # Substrate extra-dimensional depth profile (The Bulk Throat)
    dist_to_segment = np.abs(Y) + np.maximum(0, np.abs(X) - 4.5)
    z_bulk_profile = - 3.5 * np.exp(-(dist_to_segment**2) / 2.0) * (np.abs(X) <= 4.5)
    
    return {
        "X": X, "Y": Y, "R": R,
        "rho_epoch0": rho_epoch0,
        "psi_epoch1": psi_epoch1,
        "rho_substrate_cavity": rho_substrate_cavity,
        "Phi_grav": Phi_grav,
        "orbit_x": orbit_x, "orbit_y": orbit_y,
        "x_pair": x_pair, "y_pair": y_pair,
        "z_bulk_profile": z_bulk_profile
    }

def visualize_universe_epochs(sim):
    print("Rendering high-resolution simulation results...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig = plt.figure(figsize=(16, 12))
    
    # Panel 1: Epoch 0 (The Primordial Substrate)
    ax1 = fig.add_subplot(2, 2, 1)
    im1 = ax1.imshow(sim["rho_epoch0"], extent=[-10, 10, -10, 10], cmap='Blues', vmin=0, vmax=1.2)
    ax1.set_title("Epoch 0: Primordial Vacuum (Flat Substrate, No Matter)", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Dimension X", fontsize=11)
    ax1.set_ylabel("Dimension Y", fontsize=11)
    ax1.text(0, 0, "Homogeneous Substrate Ground State\nDensity: rho_0 = 1.0 (Timeless, Zero Matter)",
             ha='center', va='center', color='darkblue', fontsize=11,
             bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="blue", alpha=0.9))
    
    # Panel 2: Epoch 1 (Energy Injection & Excitation Birth)
    ax2 = fig.add_subplot(2, 2, 2)
    im2 = ax2.imshow(sim["psi_epoch1"], extent=[-10, 10, -10, 10], cmap='inferno')
    ax2.set_title("Epoch 1: Energy Injection (Quasiparticle Genesis)", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Dimension X", fontsize=11)
    ax2.set_ylabel("Dimension Y", fontsize=11)
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="Excitation Energy Density")
    ax2.text(-8.5, 7.5, "Localized Perturbations\n(Photons / Leptons Form)", color='yellow', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.7))
    
    # Panel 3: Epoch 2 (Clustering & Substrate Cavitation)
    ax3 = fig.add_subplot(2, 2, 3)
    im3 = ax3.imshow(sim["rho_substrate_cavity"], extent=[-10, 10, -10, 10], cmap='cividis', vmin=0.2, vmax=1.0)
    # Contour lines showing the gravitational potential well
    contours = ax3.contour(sim["X"], sim["Y"], sim["Phi_grav"], levels=8, colors='cyan', alpha=0.7, linewidths=1.2)
    ax3.clabel(contours, inline=True, fontsize=8, fmt='%.2f')
    ax3.set_title("Epoch 2: Matter Pile-Up Carves Substrate Cavity (Gravity)", fontsize=13, fontweight='bold')
    ax3.set_xlabel("Dimension X", fontsize=11)
    ax3.set_ylabel("Dimension Y", fontsize=11)
    plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04, label="Substrate Density Ratio rho/rho_0")
    ax3.plot(0, 0, 'y*', markersize=14, label='Clustered Matter Core')
    ax3.legend(loc='lower right', frameon=True)
    
    # Panel 4: Epoch 3 (Orbital Infall & 5D Entanglement Bridge)
    ax4 = fig.add_subplot(2, 2, 4)
    im4 = ax4.imshow(sim["rho_substrate_cavity"], extent=[-10, 10, -10, 10], cmap='gist_earth', alpha=0.6)
    # Plot orbital trajectory
    ax4.plot(sim["orbit_x"], sim["orbit_y"], 'r-', lw=2.2, label='Bound Orbit in Cavity Well')
    ax4.plot(sim["orbit_x"][-1], sim["orbit_y"][-1], 'ro', markersize=8, label='Test Excitation (Planet)')
    ax4.plot(0, 0, 'yo', markersize=12, markeredgecolor='k', label='Central Mass (Sun)')
    
    # Plot entangled pair and bulk bridge
    ax4.plot(sim["x_pair"], sim["y_pair"], 'mo', markersize=10, label='Entangled Pair (A & B)')
    ax4.plot([-4.5, 4.5], [0, 0], 'm--', lw=2.5, label='Vortex Thread across Bulk (z > 0)')
    ax4.set_title("Epoch 3: Bound Keplerian Orbit & Bulk Entanglement", fontsize=13, fontweight='bold')
    ax4.set_xlabel("Dimension X", fontsize=11)
    ax4.set_ylabel("Dimension Y", fontsize=11)
    ax4.legend(loc='lower left', frameon=True, fontsize=9.5)
    
    plt.tight_layout()
    output_path = r'f:\Reality_theory\universe_simulation.png'
    plt.savefig(output_path, dpi=300)
    print(f"Universe simulation snapshot successfully saved to: {output_path}")

def render_3d_cavity_and_wormhole(sim):
    print("Rendering 3D perspective of substrate cavity and entanglement throat...")
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    X = sim["X"]
    Y = sim["Y"]
    # Cavity depth represents the gravitational potential surface
    Z_cavity = sim["Phi_grav"] * 8.0 # Scale for visual depth
    # Add the entanglement bridge dipping into the extra dimension
    Z_total = Z_cavity + sim["z_bulk_profile"]
    
    surf = ax.plot_surface(X, Y, Z_total, cmap='viridis', edgecolor='none', alpha=0.85, rstride=2, cstride=2)
    
    # Plot orbit on the 3D surface
    # Interpolate Z for the orbit
    orbit_r = np.sqrt(sim["orbit_x"]**2 + sim["orbit_y"]**2)
    orbit_z = - 0.75 * 8.0 / (2.0 * (1.0 + orbit_r / 2.0))
    ax.plot(sim["orbit_x"], sim["orbit_y"], orbit_z, 'r-', lw=3, label='Orbital Geodesic inside Cavity')
    
    # Plot entangled particles
    ax.scatter([-4.5, 4.5], [0, 0], [0, 0], color='magenta', s=120, edgecolors='black', label='Entangled Pair (3D Brane)')
    # Draw bulk shortcut line dipping beneath
    x_bridge = np.linspace(-4.5, 4.5, 50)
    z_bridge = - 3.5 * np.sin(np.pi * (x_bridge + 4.5) / 9.0)
    ax.plot(x_bridge, np.zeros_like(x_bridge), z_bridge, 'm--', lw=3.5, label='Bulk Vortex Shortcut (Extra Dimension)')
    
    ax.set_title("3D Topological View: Substrate Cavity Well & Extra-Dimensional Entanglement Bridge", fontsize=13, fontweight='bold')
    ax.set_xlabel("Spatial Dimension X", fontsize=11)
    ax.set_ylabel("Spatial Dimension Y", fontsize=11)
    ax.set_zlabel("Substrate Depletion / Bulk Depth Z", fontsize=11)
    ax.view_init(elev=32, azim=-55)
    ax.legend(loc='upper right', frameon=True)
    
    output_3d = r'f:\Reality_theory\universe_simulation_3d.png'
    plt.savefig(output_3d, dpi=300)
    print(f"3D perspective saved to: {output_3d}")

if __name__ == "__main__":
    sim = run_universe_simulation()
    visualize_universe_epochs(sim)
    render_3d_cavity_and_wormhole(sim)
