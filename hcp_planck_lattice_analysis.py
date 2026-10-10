"""
Simulation and Mathematical Proof:
Is the Planck Scale Lattice of the Universe Hexagonal Close-Packed (HCP)?

Evaluates:
1. Kepler's Conjecture: Maximum packing density in 3D (eta = pi / (3*sqrt(2)) = 74.05%).
2. The 12-Coordination Sphere (Kissing Number = 12) in HCP geometry.
3. The Geometric Origin of K = sqrt(3)/2 = cos(pi/6) from the HCP basal triangle.
4. Long-wavelength sound speeds vs direction (computed from the HCP dynamical matrix).
   Audit note (2026-10): they are NOT isotropic; an earlier version drew a hard-coded circle.
   for long-wavelength waves (lambda >> ell_P).
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import shutil

def analyze_hcp_lattice():
    print("Simulating 3D Hexagonal Close-Packing (HCP) at the Planck scale...")
    
    # -------------------------------------------------------------
    # 1. 3D HCP Unit Cell Geometry & 12 Nearest Neighbors
    # -------------------------------------------------------------
    # Central sphere at (0, 0, 0)
    # Layer B (Z = 0): 6 coplanar neighbors in a regular hexagon of radius a = 1.0
    angles_6 = np.linspace(0, 2*np.pi, 7)[:-1]
    x_layer_B = np.cos(angles_6)
    y_layer_B = np.sin(angles_6)
    z_layer_B = np.zeros(6)
    
    # Layer A_top (Z = + c/2 = + sqrt(2/3)): 3 neighbors in equilateral triangle
    c_half = np.sqrt(2.0 / 3.0) # ~ 0.8165
    angles_3_top = np.array([np.pi/6, np.pi/6 + 2*np.pi/3, np.pi/6 + 4*np.pi/3])
    r_top = 1.0 / np.sqrt(3.0) # distance from center in XY projection
    x_layer_A_top = r_top * np.cos(angles_3_top)
    y_layer_A_top = r_top * np.sin(angles_3_top)
    z_layer_A_top = np.full(3, c_half)
    
    # Layer A_bottom (Z = - c/2): 3 neighbors matching top orientation
    x_layer_A_bot = x_layer_A_top.copy()
    y_layer_A_bot = y_layer_A_top.copy()
    z_layer_A_bot = - np.full(3, c_half)
    
    # Combine all 12 neighbors
    x_neighbors = np.concatenate([x_layer_B, x_layer_A_top, x_layer_A_bot])
    y_neighbors = np.concatenate([y_layer_B, y_layer_A_top, y_layer_A_bot])
    z_neighbors = np.concatenate([z_layer_B, z_layer_A_top, z_layer_A_bot])
    
    # -------------------------------------------------------------
    # 2. Packing Densities Comparison (Kepler's Theorem)
    # -------------------------------------------------------------
    lattices = ['Simple Cubic (SC)', 'Body-Centered Cubic (BCC)', 'Diamond Cubic', 'Hexagonal Close-Packed (HCP / FCC)']
    densities = [np.pi / 6.0, np.pi * np.sqrt(3.0) / 8.0, np.pi * np.sqrt(3.0) / 16.0, np.pi / (3.0 * np.sqrt(2.0))]
    
    # -------------------------------------------------------------
    # 3. Acoustic Wave (An)isotropy in the HCP Lattice - COMPUTED
    # -------------------------------------------------------------
    # Audit fix (2026-10): the previous version did not compute anything here; it set
    # v_s_low_energy = np.ones(...) ("Exactly isotropic!") and drew an invented 5% 6-fold ripple.
    # Below, the long-wavelength sound speeds are obtained from the full dynamical matrix of an
    # ideal HCP lattice (2-atom basis, nearest-neighbour central springs), as a function of the
    # polar angle theta measured from the c-axis (in the x-z plane).
    a_lat = 1.0
    c_lat = a_lat * np.sqrt(8.0 / 3.0)
    A_vecs = np.array([[a_lat, 0, 0], [a_lat / 2, a_lat * np.sqrt(3) / 2, 0], [0, 0, c_lat]])
    basis = np.array([[0, 0, 0], [a_lat / 2, a_lat / (2 * np.sqrt(3)), c_lat / 2]])
    bonds = []
    for s_i, tau_s in enumerate(basis):
        for n1 in range(-2, 3):
            for n2 in range(-2, 3):
                for n3 in range(-2, 3):
                    R = n1 * A_vecs[0] + n2 * A_vecs[1] + n3 * A_vecs[2]
                    for s_j, tau_j in enumerate(basis):
                        d = R + tau_j - tau_s
                        if abs(np.linalg.norm(d) - a_lat) < 1e-6:
                            bonds.append((s_i, s_j, d))

    def acoustic_speeds(u, qmag=1e-4):
        q = qmag * u
        D = np.zeros((6, 6), dtype=complex)
        for s_i, s_j, d in bonds:
            n = d / np.linalg.norm(d)
            nn = np.outer(n, n)
            D[3*s_i:3*s_i+3, 3*s_i:3*s_i+3] += nn
            D[3*s_i:3*s_i+3, 3*s_j:3*s_j+3] -= nn * np.exp(1j * (q @ d))
        w2 = np.sort(np.linalg.eigvalsh(D).real)[:3]
        return np.sqrt(np.clip(w2, 0, None)) / qmag

    theta_angles = np.linspace(0, 2*np.pi, 181)
    speeds = np.array([acoustic_speeds(np.array([np.sin(t), 0.0, np.cos(t)])) for t in theta_angles])
    v_ref = np.mean(speeds[:, :2])                  # average transverse speed, called "c"
    v_s_TA1 = speeds[:, 0] / v_ref
    v_s_TA2 = speeds[:, 1] / v_ref
    v_s_LA = speeds[:, 2] / v_ref
    print(f"HCP long-wavelength transverse speeds vary from {min(v_s_TA1.min(), v_s_TA2.min()):.3f} c "
          f"to {max(v_s_TA1.max(), v_s_TA2.max()):.3f} c with direction (NOT isotropic).")
    print(f"Longitudinal speed varies from {v_s_LA.min():.3f} c to {v_s_LA.max():.3f} c.")
    v_s_low_energy = v_s_TA1
    v_s_planck_cutoff = v_s_TA2

    return {
        "x_neighbors": x_neighbors, "y_neighbors": y_neighbors, "z_neighbors": z_neighbors,
        "lattices": lattices, "densities": densities,
        "theta_angles": theta_angles,
        "v_s_low_energy": v_s_low_energy, "v_s_planck_cutoff": v_s_planck_cutoff
    }

def plot_hcp_analysis(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig = plt.figure(figsize=(16, 12))
    
    # -------------------------------------------------------------
    # Panel 1: 3D Visualization of the 12-Neighbor HCP Planck Cell
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    # Plot central node
    ax1.scatter([0], [0], [0], color='crimson', s=250, edgecolor='black', label='Central Planck Node')
    
    # Plot 12 nearest neighbors
    ax1.scatter(data["x_neighbors"][:6], data["y_neighbors"][:6], data["z_neighbors"][:6],
                color='cyan', s=140, edgecolor='black', label='6 In-Plane Neighbors (Z = 0)')
    ax1.scatter(data["x_neighbors"][6:9], data["y_neighbors"][6:9], data["z_neighbors"][6:9],
                color='magenta', s=140, edgecolor='black', label=r'3 Top Neighbors ($Z = +c/2$)')
    ax1.scatter(data["x_neighbors"][9:], data["y_neighbors"][9:], data["z_neighbors"][9:],
                color='blue', s=140, edgecolor='black', label=r'3 Bottom Neighbors ($Z = -c/2$)')
    
    # Draw elastic bonds from center to all 12 neighbors
    for i in range(12):
        ax1.plot([0, data["x_neighbors"][i]], [0, data["y_neighbors"][i]], [0, data["z_neighbors"][i]],
                 color='gray', linestyle='-', lw=1.2)
        
    ax1.set_title("1. The 12-Bond HCP Coordination Shell\n(Maximum Packing Geometry of Space)",
                  fontsize=11.5, fontweight='bold')
    ax1.set_xlabel("X", fontsize=10)
    ax1.set_ylabel("Y", fontsize=10)
    ax1.set_zlabel("Z", fontsize=10)
    ax1.view_init(elev=22, azim=-45)
    ax1.legend(loc='upper right', frameon=True, fontsize=8.0)
    
    # -------------------------------------------------------------
    # Panel 2: Kepler Packing Density Comparison
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2)
    colors = ['#95a5a6', '#3498db', '#e67e22', '#2ecc71']
    bars = ax2.bar(data["lattices"], [d * 100 for d in data["densities"]], color=colors, width=0.48, edgecolor='black', lw=1.2)
    ax2.set_ylabel('Packing Efficiency [%]', fontsize=11, fontweight='bold')
    ax2.set_title("2. Kepler's Theorem: HCP is the Densest Possible Packing of Reality",
                  fontsize=11.5, fontweight='bold')
    ax2.set_ylim(0, 95)
    ax2.set_xticks(range(len(data["lattices"])))
    ax2.set_xticklabels(data["lattices"], rotation=12, ha='right', fontsize=9.5)
    
    for bar, d in zip(bars, data["densities"]):
        h = bar.get_height()
        ax2.annotate(f'{h:.2f}%', xy=(bar.get_x() + bar.get_width()/2, h),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                     fontweight='bold', fontsize=9.5)
        
    # -------------------------------------------------------------
    # Panel 3: Computed directional sound speeds (anisotropic)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3, projection='polar')
    ax3.plot(data["theta_angles"], data["v_s_low_energy"], 'blue', lw=2.5,
             label=r'Transverse mode TA1 at LOW energy ($k \to 0$), computed')
    ax3.plot(data["theta_angles"], data["v_s_planck_cutoff"], 'crimson', linestyle='--', lw=1.8,
             label=r'Transverse mode TA2 at LOW energy ($k \to 0$), computed')
    ax3.plot(data["theta_angles"], np.ones_like(data["theta_angles"]), color='gray', lw=1, linestyle=':',
             label='Perfect isotropy (what Lorentz invariance requires)')
    ax3.set_title(r"3. Computed low-energy transverse speed vs angle to c-axis:" + "\n" + r"NOT a circle - the lattice is anisotropic even at $\lambda \gg \ell_P$",
                  fontsize=11.5, fontweight='bold', va='bottom')
    ax3.set_ylim(0.8, 1.2)
    ax3.legend(loc='lower center', bbox_to_anchor=(0.5, -0.32), frameon=True, fontsize=8.5)
    
    # -------------------------------------------------------------
    # Panel 4: Architectural Synthesis
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    analysis_text = (
        "=========================================================================\n"
        "IS THE PLANCK SCALE ARRANGEMENT OF THE UNIVERSE HCP?\n"
        "=========================================================================\n\n"
        "1. YES, BY THE PRINCIPLE OF MAXIMUM PACKING (KEPLER'S THEOREM):\n"
        "   - During the primordial condensation of the substrate, the medium\n"
        "     minimized its vacuum free energy by packing its quanta as tightly\n"
        "     as possible. In 3D space, mathematics PROVES that only HCP and FCC\n"
        "     achieve maximum density (74.05%).\n\n"
        "2. THE EXACT EMERGENCE OF THE PREFACTOR K = sqrt(3)/2:\n"
        "   - In an HCP lattice, every layer is a 2D triangular grid.\n"
        "   - The altitude of an equilateral triangle is exactly:\n"
        "         h = sin(60 deg) = cos(30 deg) = sqrt(3)/2 = 0.866025!\n"
        "   - (Claimed to enter the electron mass; see the audit note below.)\n\n"
        "3. AUDIT (computed in panel 3):\n"
        "   - Long-wavelength transverse speeds in HCP depend on the angle to\n"
        "     the c-axis by ~17% (FCC: ~33%). Light speed would be direction-\n"
        "     dependent at ALL energies - excluded by experiment (~1e-17).\n"
        "   - sqrt(3)/2 is a geometric number of the triangle; no fluctuation\n"
        "     determinant was computed, so its use in m_e is a fit.\n"
        "   - Winterberg's Planck-aether model uses +/- mass 'planckions';\n"
        "     the HCP/Maxwell/Dirac claims above are not verified."
    )
    ax4.text(0.01, 0.98, analysis_text, va='top', ha='left', family='monospace', fontsize=9.0,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fdfefe", ec="#2c3e50", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hcp_planck_lattice_analysis.png')
    plt.savefig(output_path, dpi=300)
    print(f"HCP lattice analysis plot saved to: {output_path}")
    
    # Copy to artifact directory
    artifact_dir = r'C:\Users\Asta\.gemini\antigravity\brain\cfcab9e6-1707-463d-a5cf-0f6b32f4acb8'
    if os.path.exists(artifact_dir):
        shutil.copy(output_path, os.path.join(artifact_dir, 'hcp_planck_lattice_analysis.png'))
        print("Copied to artifact directory.")

if __name__ == "__main__":
    data = analyze_hcp_lattice()
    plot_hcp_analysis(data)
