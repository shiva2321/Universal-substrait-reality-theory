"""
Simulation and Mathematical Proof:
1. Visualizing 3D/Higher-D Substrate Lattices, Waves, and Spherical Cavities.
2. The 3D Vortex Ring (Smoke Ring / Hopfion): How particles circulate in 3D.
3. The Wave vs Photon Resolution: Photons as Solitonic Shear Phonons of the Medium.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import shutil

def run_3d_visualization_simulation():
    print("Generating 3D cavity, toroidal vortex, and photon wavepacket models...")
    
    # -------------------------------------------------------------
    # 1. Toroidal Vortex (3D Smoke Ring / Hopfion) Coordinates
    # -------------------------------------------------------------
    # Major radius R_torus = 2.0, minor radius r_tube = 0.7
    R_major = 2.5
    r_minor = 0.9
    theta_torus = np.linspace(0, 2*np.pi, 60)
    phi_torus = np.linspace(0, 2*np.pi, 60)
    Theta_t, Phi_t = np.meshgrid(theta_torus, phi_torus)
    
    # 3D Torus parametric equations
    X_torus = (R_major + r_minor * np.cos(Phi_t)) * np.cos(Theta_t)
    Y_torus = (R_major + r_minor * np.cos(Phi_t)) * np.sin(Theta_t)
    Z_torus = r_minor * np.sin(Phi_t)
    
    # Vortex circulation streamlines (helical knot on torus surface)
    t_knot = np.linspace(0, 4*np.pi, 200)
    knot_x = (R_major + r_minor * np.cos(3 * t_knot)) * np.cos(t_knot)
    knot_y = (R_major + r_minor * np.cos(3 * t_knot)) * np.sin(t_knot)
    knot_z = r_minor * np.sin(3 * t_knot)
    
    # -------------------------------------------------------------
    # 2. 3D Spherical Cavity Depletion Well (Gravity Bubble)
    # -------------------------------------------------------------
    N_3d = 40
    coords = np.linspace(-4, 4, N_3d)
    X3, Y3, Z3 = np.meshgrid(coords, coords, coords)
    R3 = np.sqrt(X3**2 + Y3**2 + Z3**2) + 0.1
    # 3D Density depletion: rho(r) = rho_0 * (1 - 1.2 / r) for r > 1.2
    rho_3d = 1.0 - 1.5 / (R3 + 0.5)
    
    # Radial slice of the 3D cavity
    r_slice = np.linspace(0.2, 5.0, 200)
    rho_profile_3d = 1.0 - 1.2 / (r_slice + 0.4)
    
    # -------------------------------------------------------------
    # 3. Wave vs Photon: Continuous Wave vs Localized Wavepacket
    # -------------------------------------------------------------
    x_line = np.linspace(-12, 12, 600)
    # Classical infinite wave
    wave_continuous = 0.5 * np.cos(3.0 * x_line)
    
    # Quantum Photon Wavepacket: Localized solitonic envelope
    sigma_photon = 2.0
    k_photon = 4.0
    envelope = np.exp(- (x_line**2) / (2 * sigma_photon**2))
    photon_wavepacket = envelope * np.cos(k_photon * x_line)
    energy_density = envelope**2 # Proportional to probability / E = h*nu
    
    return {
        "X_torus": X_torus, "Y_torus": Y_torus, "Z_torus": Z_torus,
        "knot_x": knot_x, "knot_y": knot_y, "knot_z": knot_z,
        "r_slice": r_slice, "rho_profile_3d": rho_profile_3d,
        "x_line": x_line, "wave_continuous": wave_continuous,
        "photon_wavepacket": photon_wavepacket, "energy_density": energy_density
    }

def plot_3d_and_photon_visualizations(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig = plt.figure(figsize=(16, 12))
    
    # -------------------------------------------------------------
    # Panel 1: 3D Particle Cavity = A Smoke Ring / Torus (Hopfion)
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.plot_surface(data["X_torus"], data["Y_torus"], data["Z_torus"],
                     color='cyan', alpha=0.35, edgecolor='teal', lw=0.3)
    ax1.plot(data["knot_x"], data["knot_y"], data["knot_z"],
             'r-', lw=2.5, label='Trapped Wave Circulation (3D Knot / Vortex)')
    
    ax1.set_title("1. What a Particle Looks Like in 3D:\nA Toroidal Vortex (Smoke Ring / Hopfion)",
                  fontsize=11.5, fontweight='bold')
    ax1.set_xlabel("X", fontsize=10)
    ax1.set_ylabel("Y", fontsize=10)
    ax1.set_zlabel("Z", fontsize=10)
    ax1.view_init(elev=28, azim=45)
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    # -------------------------------------------------------------
    # Panel 2: 3D Spherical Cavity Well (The 3D Gravity Bubble)
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2)
    # Plot radial density gradient
    ax2.plot(data["r_slice"], data["rho_profile_3d"], 'darkblue', lw=2.8, label=r'Substrate Density $\rho(r)/\rho_0$')
    ax2.axhline(1.0, color='gray', linestyle='--', label=r'Normal Vacuum Density ($\rho_0$)')
    ax2.fill_between(data["r_slice"], data["rho_profile_3d"], 1.0, color='blue', alpha=0.15, label='Substrate Depletion (Cavity Well)')
    
    # Add inward radial arrows from all 3D directions
    ax2.annotate('Substrate Rarefaction\n(Spherical Bubble in 3D Mesh)', xy=(1.0, 0.2), xytext=(2.2, 0.35),
                 arrowprops=dict(arrowstyle="->", color='red', lw=2),
                 fontsize=9.5, fontweight='bold', color='red')
    
    ax2.set_xlabel('Radial Distance from Center $r$ [3D Sphere]', fontsize=11, fontweight='bold')
    ax2.set_ylabel(r'Substrate Density $\rho(r)/\rho_0$', fontsize=11, fontweight='bold')
    ax2.set_title("2. What a Cavity Looks Like in 3D:\nA Spherical Rarefaction Bubble (Lower Density in Center)",
                  fontsize=11.5, fontweight='bold')
    ax2.set_ylim(-0.2, 1.2)
    ax2.legend(loc='lower right', frameon=True, fontsize=8.5)
    
    # -------------------------------------------------------------
    # Panel 3: Classical Continuous Wave vs. Localized Photon Wavepacket
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(data["x_line"], data["wave_continuous"] + 1.6, 'gray', linestyle='--', lw=1.8,
             label='Classical Continuous Wave (Infinite, Non-Localized)')
    ax3.plot(data["x_line"], data["photon_wavepacket"] - 0.8, 'darkorange', lw=2.2,
             label=r'The Photon: Localized Wavepacket ($\Delta x \cdot \Delta p \sim \hbar$)')
    ax3.plot(data["x_line"], data["energy_density"] - 0.8, 'crimson', lw=1.5, linestyle=':',
             label=r'Packet Energy Density Envelope ($E = h\nu$)')
    
    ax3.annotate('Travels at c as a single lump', xy=(2.0, -0.8), xytext=(4.0, 0.2),
                 arrowprops=dict(arrowstyle="->", color='darkorange', lw=2),
                 fontsize=9.2, fontweight='bold', color='darkorange')
    
    ax3.set_xlabel('Spatial Coordinate $x$', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Amplitude', fontsize=11, fontweight='bold')
    ax3.set_title("3. Wave vs. Photon: A Photon IS a Localized Wavepacket of the Medium",
                  fontsize=11.5, fontweight='bold')
    ax3.set_ylim(-2.2, 2.6)
    ax3.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    # -------------------------------------------------------------
    # Panel 4: Synthesis Architectural Ledger
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    ledger_text = (
        "=========================================================================\n"
        "1. HOW TO VISUALIZE IN 3D (BEYOND THE 2D TRAMPOLINE):\n"
        "=========================================================================\n"
        "• 3D LATTICE: Imagine an infinite 3D sponge, foam, or crystal of springs\n"
        "  filling all of space. You are swimming inside this 3D sponge!\n"
        "• 3D CAVITY: In 2D, a cavity is a pit. In 3D, it is a SPHERICAL BUBBLE OF\n"
        "  RAREFACTION! The sponge is stretched thinner in the center. Objects are\n"
        "  drawn toward the center from ANY direction (Up, Down, Left, Right).\n"
        "• 3D PARTICLE: In 2D, a particle is a flat whirlpool. In 3D, it is a\n"
        "  SMOKE RING (TOROIDAL VORTEX / HOPFION)! A self-contained donut of\n"
        "  circulating shear waves spinning inside the 3D sponge.\n\n"
        "=========================================================================\n"
        "2. IF WAVE AND PHOTON ARE THE SAME, HOW ARE THEY DESCRIBED?\n"
        "=========================================================================\n"
        "• In our substrate theory, a PHOTON IS A 'SHEAR PHONON':\n"
        "  Just like sound in a crystal is quantized into discrete 'phonons' (quanta\n"
        "  of vibration), light is a quantized wavepacket of the cosmic substrate!\n"
        "• WAVE NATURE: It is an oscillating transverse strain wave of frequency nu.\n"
        "  When it passes through two slits, the medium's wave ripples interfere!\n"
        "• PARTICLE / PHOTON NATURE: The wave is NOT an infinite plane; it is a\n"
        "  compact, localized solitary wavepacket (soliton).\n"
        "• QUANTUM DETECTION: An electron cavity can only absorb energy in whole\n"
        "  resonant cycles: E = h * nu. The entire localized wavepacket is swallowed\n"
        "  at a single point on the detector, creating the 'particle' click!"
    )
    ax4.text(0.01, 0.98, ledger_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#7f8c8d", lw=1.5))
    
    plt.tight_layout()
    output_path = r'f:\Reality_theory\visualize_3d_cavities_and_photons.png'
    plt.savefig(output_path, dpi=300)
    print(f"Plot successfully saved to: {output_path}")
    
    # Copy to artifact directory
    artifact_dir = r'C:\Users\Asta\.gemini\antigravity\brain\cfcab9e6-1707-463d-a5cf-0f6b32f4acb8'
    if os.path.exists(artifact_dir):
        shutil.copy(output_path, os.path.join(artifact_dir, 'visualize_3d_cavities_and_photons.png'))
        print("Copied to artifact directory.")

if __name__ == "__main__":
    data = run_3d_visualization_simulation()
    plot_3d_and_photon_visualizations(data)
