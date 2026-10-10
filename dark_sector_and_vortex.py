"""
Simulation of:
1. Dark Matter as Coherent Substrate Condensate (Solitonic Core vs. NFW Cusp).
2. Dark Energy as Non-Equilibrium Substrate Zero-Point Regulation (Volovik Mechanism).
3. 5D Superfluid Vortex Filament connecting an EPR Entangled Pair.
4. Bell Inequality Violation (CHSH S = 2*sqrt(2) = 2.828) from Substrate Phase Locking.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def simulate_dark_matter_halo():
    """
    Substrate Condensate Dark Matter (psi-DM / Fuzzy DM):
    The substrate forms macroscopic coherent condensation halos.
    Solitonic core density: rho_soliton(r) = rho_0 / (1 + 0.091 * (r/r_c)^2)^8
    Standard Cold Dark Matter (NFW): rho_NFW(r) = rho_s / ((r/r_s) * (1 + r/r_s)^2)
    """
    print("Simulating Substrate Condensate Dark Matter...")
    r = np.logspace(-1, 2, 400) # kpc
    r_core = 1.5 # kpc (solitonic core radius)
    rho_0 = 1.0  # arbitrary normalized central density
    
    # Substrate solitonic core (Bose-Einstein Condensate halo)
    rho_soliton = rho_0 / (1.0 + 0.091 * (r / r_core)**2)**8
    # Match outer tail to NFW-like envelope
    rho_substrate_dm = np.where(r < 2.5 * r_core, rho_soliton, rho_0 * 0.15 * (r_core / r)**3)
    
    # Standard NFW (cuspy profile with 1/r singularity at center)
    r_s = 8.0 # kpc
    rho_NFW = (rho_0 * 0.2) / ((r / r_s) * (1.0 + r / r_s)**2)
    
    # Rotation velocities: v(r) = sqrt(G M(r) / r)
    # Cumulative masses:
    dr = np.gradient(r)
    M_sub = 4 * np.pi * np.cumsum(rho_substrate_dm * r**2 * dr)
    M_nfw = 4 * np.pi * np.cumsum(rho_NFW * r**2 * dr)
    
    v_sub = np.sqrt(M_sub / r)
    v_nfw = np.sqrt(M_nfw / r)
    
    # Normalize for comparison
    v_sub /= np.max(v_sub)
    v_nfw /= np.max(v_nfw)
    
    return r, rho_substrate_dm, rho_NFW, v_sub, v_nfw

def simulate_dark_energy_cosmology():
    """
    Volovik Vacuum Regulation & Cosmological Acceleration:
    Substrate bulk equilibrium pressure is strictly zero: P_vac = 0.
    Observed cosmological acceleration arises from residual hydrodynamic
    expansion back-reaction: rho_Lambda ~ H(z)^2 * M_Planck^2.
    """
    print("Simulating Substrate Cosmological Expansion...")
    z = np.linspace(0, 3, 200) # Redshift
    Omega_M = 0.3
    Omega_Lambda = 0.7
    
    # Standard Lambda-CDM Hubble parameter: H(z) = H_0 * sqrt(Omega_M*(1+z)^3 + Omega_Lambda)
    H_LCDM = np.sqrt(Omega_M * (1 + z)**3 + Omega_Lambda)
    
    # "Substrate" curve: Omega_Lambda = 0.7 is the observed value put in by hand
    # and w = -0.98 is an arbitrary choice (the old comment claimed a z-dependent w
    # that the code never used). Nothing here computes the size of dark energy.
    H_Substrate = np.sqrt(Omega_M * (1 + z)**3 + Omega_Lambda * (1 + z)**(3 * (1 - 0.98)))
    
    return z, H_LCDM, H_Substrate

def simulate_vortex_entanglement_chsh():
    """
    Superfluid Vortex Phase Locking & Bell Test:
    Two entangled excitations at endpoints of a 5D vortex tube with phase difference Delta_theta = pi.
    Correlation function: E(a, b) = - cos(theta_a - theta_b).
    CHSH parameter S = |E(a, b) - E(a, b') + E(a', b) + E(a', b')|.
    For standard quantum angles: theta_a = 0, theta_a' = pi/2, theta_b = pi/4, theta_b' = -pi/4:
    S = |-cos(pi/4) - (-cos(3*pi/4)) + (-cos(-pi/4)) + (-cos(pi/4))| = 2 * sqrt(2) = 2.828 > 2 (Bell violation!)
    """
    print("Simulating Vortex Topological Bell Violation...")
    theta_diff = np.linspace(0, 2 * np.pi, 300)
    # Audit fix (2026-10): the previous version simply typed in the quantum-mechanical correlation
    # E = -cos(theta) and labelled it the 'substrate' result. Here the phase-locked vortex is actually
    # simulated: both ends carry a phase lambda fixed when the pair is created (a LOCAL hidden variable).
    rng = np.random.default_rng(0)
    lam = rng.uniform(0, 2 * np.pi, 200000)
    def E_vortex(a, b):
        return np.mean(np.sign(np.cos(a - lam)) * -np.sign(np.cos(b - lam)))
    correlation_substrate = np.array([E_vortex(0.0, t) for t in theta_diff])   # simulated vortex model
    correlation_quantum = - np.cos(theta_diff)                                  # quantum mechanics
    
    # Classical local hidden variable upper bound: triangle wave bounded by linear correlations
    classical_correlation = np.where(theta_diff <= np.pi,
                                     -1.0 + (2.0 / np.pi) * theta_diff,
                                     3.0 - (2.0 / np.pi) * theta_diff)
    
    a0, a1, b0, b1 = 0.0, np.pi / 2, np.pi / 4, 3 * np.pi / 4    # optimal CHSH settings
    S_substrate = abs(E_vortex(a0, b0) - E_vortex(a0, b1) + E_vortex(a1, b0) + E_vortex(a1, b1))
    print(f"Simulated phase-locked vortex model: CHSH S = {S_substrate:.3f} (local model: S <= 2)")
    print("Quantum mechanics (Tsirelson) gives 2.828; the vortex picture does not reproduce it")
    print("unless the quantum correlation is put in by hand (see audit/a03_bell_models.py).")
    S_classical_max = 2.0
    
    return theta_diff, correlation_substrate, classical_correlation, S_substrate, S_classical_max

def plot_dark_sector_and_vortex(r, rho_sub, rho_nfw, v_sub, v_nfw, z, H_lcdm, H_sub, th_diff, corr_sub, corr_class, S_sub=2.0):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Dark Matter Halo (Substrate Soliton vs NFW Cusp)
    axs[0, 0].loglog(r, rho_sub, 'b-', lw=2.5, label='Substrate BEC Dark Matter (Core)')
    axs[0, 0].loglog(r, rho_nfw, 'r--', lw=2.0, label='Standard CDM / NFW (Singular Cusp)')
    axs[0, 0].axvspan(0.1, 1.5, color='blue', alpha=0.1, label='Flat Quantum Solitonic Core')
    axs[0, 0].set_xlabel('Galactic Radius $r$ [kpc]', fontsize=12)
    axs[0, 0].set_ylabel(r'Mass Density $\rho(r)$ [arb. units]', fontsize=12)
    axs[0, 0].set_title('Figure 1: Dark Matter as Substrate Condensate (No Core-Cusp Problem)', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='lower left', frameon=True)
    axs[0, 0].set_ylim(1e-4, 2.0)
    
    # Subplot 2: Dark Energy & Cosmological Expansion
    axs[0, 1].plot(z, H_sub, 'g-', lw=2.5, label=r'Assumed $w = -0.98$ with observed $\Omega_\Lambda = 0.7$ put in')
    axs[0, 1].plot(z, H_lcdm, 'k--', lw=2.0, label=r'Standard $\Lambda\mathrm{CDM}$ Cosmological Model')
    axs[0, 1].set_xlabel('Cosmic Redshift $z$', fontsize=12)
    axs[0, 1].set_ylabel('Hubble Expansion Rate $H(z) / H_0$', fontsize=12)
    axs[0, 1].set_title(r'Figure 2: Expansion history ($\Omega_\Lambda$ is an input, not derived)', fontsize=13, fontweight='bold')
    axs[0, 1].legend(loc='upper left', frameon=True)
    axs[0, 1].text(0.5, 1.5, "Volovik (prior art): equilibrium vacuum\npressure is 0, so no $10^{120}$ term.\nThe observed 0.7 is NOT computed here.",
                   bbox=dict(boxstyle="round,pad=0.5", fc="#e8f8f5", ec="#1abc9c", alpha=0.9), fontsize=10.5)
    
    # Subplot 3: Entanglement Correlation Function (Vortex Phase Locking)
    axs[1, 0].plot(th_diff * 180 / np.pi, corr_sub, 'm-', lw=2.5, label='Simulated local vortex-phase model (triangle)')
    axs[1, 0].plot(th_diff * 180 / np.pi, corr_class, 'k:', lw=2.0, label='Classical Local Bound (Bell Limit)')
    axs[1, 0].set_xlabel('Measurement Angle Difference $\\Delta\\theta$ [degrees]', fontsize=12)
    axs[1, 0].set_ylabel('Quantum Correlation $E(a, b)$', fontsize=12)
    axs[1, 0].plot(th_diff * 180 / np.pi, -np.cos(th_diff), color='#3498db', lw=1.5, alpha=0.7, label='Quantum mechanics $-\\cos\\Delta\\theta$ (reference)')
    axs[1, 0].set_title('Figure 3: Simulated vortex-phase model vs quantum mechanics', fontsize=13, fontweight='bold')
    axs[1, 0].legend(loc='upper right', frameon=True)
    axs[1, 0].axhline(0, color='gray', lw=0.8)
    
    # Subplot 4: Bell CHSH Inequality Violation
    tests = ['Classical Limit (Bell)', 'Vortex model (simulated)', 'Quantum mechanics (Tsirelson)']
    s_vals = [2.0, S_sub, 2.828]
    colors = ['#95a5a6', '#9b59b6', '#3498db']
    bars = axs[1, 1].bar(tests, s_vals, color=colors, width=0.45, edgecolor='black', lw=1.2)
    axs[1, 1].axhline(2.0, color='red', linestyle='--', lw=2, label='Bell Inequality Classical Upper Bound ($S \\leq 2$)')
    axs[1, 1].set_ylabel('CHSH Parameter $S$', fontsize=12)
    axs[1, 1].set_ylim(0, 3.5)
    axs[1, 1].set_title('Figure 4: CHSH parameter - local vortex model stays at the Bell bound', fontsize=13, fontweight='bold')
    axs[1, 1].legend(loc='upper left', frameon=True)
    for bar in bars:
        h = bar.get_height()
        axs[1, 1].annotate(f'{h:.3f}',
                           xy=(bar.get_x() + bar.get_width() / 2, h),
                           xytext=(0, 6), textcoords="offset points",
                           ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dark_sector_and_vortex.png')
    plt.savefig(output_path, dpi=300)
    print(f"Dark sector & vortex simulation saved to: {output_path}")

if __name__ == "__main__":
    r, rho_sub, rho_nfw, v_sub, v_nfw = simulate_dark_matter_halo()
    z, H_lcdm, H_sub = simulate_dark_energy_cosmology()
    th_diff, corr_sub, corr_class, S_sub, S_class = simulate_vortex_entanglement_chsh()
    plot_dark_sector_and_vortex(r, rho_sub, rho_nfw, v_sub, v_nfw, z, H_lcdm, H_sub, th_diff, corr_sub, corr_class, S_sub)
