"""
Simulation and Mathematical Proof:
1. The "Smaller is Heavier" Paradox: Fundamental vs. Composite Particles.
2. The Compton-Schwarzschild V-Curve: Transition from Quantum Confinement (R ~ 1/m) to Black Holes (R ~ m).
3. Massless Particles and Free Waves: Why photons and gravitons have m = 0 (Untrapped vs Trapped excitations).
"""

import numpy as np
import matplotlib.pyplot as plt
import shutil
import os

def run_analysis():
    print("Simulating Particle Size-Mass Scaling and Massless Waves...")
    
    # Fundamental physical constants
    c = 2.99792458e8             # m/s
    hbar = 1.054571817e-34       # J s
    G = 6.67430e-11              # m^3 / (kg s^2)
    eV = 1.602176634e-19         # J
    
    # -------------------------------------------------------------
    # 1. Compton-Schwarzschild V-Curve: The Full Spectrum of Reality
    # -------------------------------------------------------------
    # Mass range from 10^-35 kg (neutrinos) to 10^35 kg (supermassive black holes)
    log_m = np.linspace(-35, 35, 500)
    m_array = 10.0**log_m
    
    # Quantum Compton radius (Localization limit of a single wave packet): R_C = hbar / (m * c)
    R_compton = hbar / (m_array * c)
    
    # Gravitational Schwarzschild radius (Cavity collapse into black hole): R_S = 2 * G * m / c^2
    R_schwarzschild = (2.0 * G * m_array) / (c**2)
    
    # Planck mass and length
    m_planck = np.sqrt(hbar * c / G) # ~ 2.176e-8 kg
    l_planck = np.sqrt(hbar * G / (c**3)) # ~ 1.616e-35 m
    
    # -------------------------------------------------------------
    # 2. Composite (Macroscopic) Scaling: R ~ (M / rho)^(1/3)
    # -------------------------------------------------------------
    # For ordinary matter (density ~ 1000 to 5000 kg/m^3, e.g. water or rock)
    rho_matter = 3000.0 # kg/m^3
    m_composite = np.logspace(-20, 25, 200) # from dust to planets
    R_composite = (3.0 * m_composite / (4.0 * np.pi * rho_matter))**(1.0/3.0)
    
    # -------------------------------------------------------------
    # 3. Real Particles and Objects Data Points
    # -------------------------------------------------------------
    landmarks = [
        {"name": "Electron", "m": 9.109e-31, "R": 3.861e-13, "type": "quantum"},
        {"name": "Proton", "m": 1.673e-27, "R": 0.841e-15, "type": "quantum_hadron"},
        {"name": "Higgs Boson", "m": 2.23e-25, "R": 1.57e-18, "type": "quantum"},
        {"name": "Planck Boundary", "m": m_planck, "R": l_planck, "type": "planck"},
        {"name": "1-gram Pebble", "m": 1e-3, "R": 4.3e-3, "type": "composite"},
        {"name": "Human (70kg)", "m": 70.0, "R": 0.25, "type": "composite"},
        {"name": "Earth", "m": 5.972e24, "R": 6.371e6, "type": "composite"},
        {"name": "Solar Mass BH", "m": 1.989e30, "R": 2953.0, "type": "bh"},
        {"name": "M87* Supermassive BH", "m": 1.3e40, "R": 1.9e13, "type": "bh"},
    ]
    
    return {
        "log_m": log_m,
        "m_array": m_array,
        "R_compton": R_compton,
        "R_schwarzschild": R_schwarzschild,
        "m_composite": m_composite,
        "R_composite": R_composite,
        "m_planck": m_planck,
        "l_planck": l_planck,
        "landmarks": landmarks,
        "c": c,
        "hbar": hbar
    }

def plot_analysis(data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    
    # ---------------------------------------------------------
    # Panel 1: The Compton-Schwarzschild V-Curve (Quantum vs Gravity)
    # ---------------------------------------------------------
    ax1 = axs[0, 0]
    ax1.loglog(data["m_array"], data["R_compton"], 'b--', lw=2.2, label=r'Fundamental Quantum Limit: $R_C = \frac{\hbar}{mc} \propto \frac{1}{m}$')
    ax1.loglog(data["m_array"], data["R_schwarzschild"], 'r-', lw=2.5, label=r'Gravitational Horizon Limit: $R_S = \frac{2Gm}{c^2} \propto m$')
    ax1.loglog(data["m_composite"], data["R_composite"], 'g-.', lw=2.0, label=r'Composite Macro Matter: $R \propto M^{1/3}$ (Many particles!)')
    
    # Highlight Forbidden Quantum Gravity Zone
    ax1.fill_between(data["m_array"], np.minimum(data["R_compton"], data["R_schwarzschild"]), 1e-40, color='gray', alpha=0.18, label='Physically Unreachable Zone (Sub-Planck / Sub-Horizon)')
    
    # Mark Planck Point
    ax1.plot(data["m_planck"], data["l_planck"], 'kd', markersize=10, label='Planck Crossover (Minimum Physical Size)')
    ax1.annotate('Planck Scale\n($m_P \\approx 21\\,\\mu$g, $\\ell_P \\approx 1.6\\times 10^{-35}\\,m$)',
                 xy=(data["m_planck"], data["l_planck"]), xytext=(20, -35),
                 textcoords='offset points', fontsize=9.5, fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color='black', lw=1.5))
    
    # Mark landmarks
    for lm in data["landmarks"]:
        if lm["name"] in ["Electron", "Proton", "1-gram Pebble", "Earth", "Solar Mass BH"]:
            color = 'purple' if lm["type"].startswith("quantum") else ('green' if lm["type"] == 'composite' else 'red')
            ax1.plot(lm["m"], lm["R"], 'o', color=color, markersize=7)
            offset = (15, 10) if lm["name"] != "Proton" else (-60, -20)
            ax1.annotate(f"{lm['name']}", xy=(lm["m"], lm["R"]), xytext=offset,
                         textcoords='offset points', fontsize=8.5, fontweight='bold', color=color)
            
    ax1.set_xlim(1e-35, 1e42)
    ax1.set_ylim(1e-36, 1e20)
    ax1.set_xlabel('Mass [kg] (Log Scale)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Radius / Spatial Size [m] (Log Scale)', fontsize=11, fontweight='bold')
    ax1.set_title('1. Why "Smaller is Heavier" Only Applies to Fundamental Waves (The V-Curve)', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    # ---------------------------------------------------------
    # Panel 2: The Two Regimes of Nature: Fundamental vs Composite
    # ---------------------------------------------------------
    ax2 = axs[0, 1]
    ax2.axis('off')
    regimes_text = (
        "=========================================================================\n"
        "WHY COMMON INTUITION (BIGGER = HEAVIER) IS BOTH RIGHT AND WRONG\n"
        "=========================================================================\n\n"
        "1. COMPOSITE MACROSCOPIC REALITY (Rocks, Elephants, Baseballs):\n"
        "   - A rock is NOT a single fundamental excitation!\n"
        "   - It is composed of ~ 10^26 separate atoms bonded together.\n"
        "   - Mass is EXTENSIVE: M = N * m_atom = rho * Volume = (4/3)*pi*rho * R^3.\n"
        "   - If you want a heavier rock, you bundle more particles together: R ~ M^(1/3).\n"
        "   --> In the macroscopic world: BIGGER OBJECT = HEAVIER OBJECT!\n\n"
        "2. FUNDAMENTAL QUANTUM REALITY (Single Ripples in the Substrate):\n"
        "   - An electron or muon is a SINGLE isolated wave packet trapped in a cavity.\n"
        "   - By de Broglie relation: Momentum p = h / lambda.\n"
        "   - Squeezing a wave into a smaller cavity requires tighter wavelength:\n"
        "       lambda ~ R  ==>  p ~ h / R  ==>  Energy E = p*c ~ (h*c) / R\n"
        "   - Therefore: Rest Mass m = E / c^2 = (hbar) / (R * c)  ==>  m ~ 1 / R!\n"
        "   --> To force a single ripple into a TINY space, you must inject ENORMOUS\n"
        "       curvature and energy, creating a HEAVIER fundamental particle!\n\n"
        "3. THE GRAVITATIONAL TURNOVER (Black Holes):\n"
        "   - If you keep squeezing a particle smaller than the Planck length (10^-35 m),\n"
        "     the mass becomes so high that gravity takes over:\n"
        "     R_Schwarzschild = 2*G*m / c^2  ==>  R ~ m.\n"
        "   - Here, the arrow reverses again: A heavier black hole is a LARGER black hole!"
    )
    ax2.text(0.01, 0.98, regimes_text, va='top', ha='left', family='monospace', fontsize=9.2,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fbfcfc", ec="#7f8c8d", lw=1.5))
    
    # ---------------------------------------------------------
    # Panel 3: Trapped vs Massless Waves (Photons vs Matter)
    # ---------------------------------------------------------
    ax3 = axs[1, 0]
    x = np.linspace(-4, 4, 300)
    
    # Traveling wave (Photon): envelope moving linearly at c
    traveling_wave = np.exp(-((x - 1.5)**2) / 0.8) * np.cos(10 * (x - 1.5))
    
    # Trapped cavity standing wave (Matter): confined circular / nodal envelope
    trapped_wave = np.exp(-(x**2) / 0.5) * np.cos(12 * x)
    
    ax3.plot(x, traveling_wave + 1.8, 'darkorange', lw=2.2, label='Massless Wave (Photon): Untrapped, v = c, m_0 = 0')
    ax3.plot(x, trapped_wave - 1.2, 'purple', lw=2.2, label='Massive Particle (Matter): Confined Cavity, v_net = 0, m_0 > 0')
    
    # Draw cavity walls for trapped wave
    ax3.axvline(-1.2, ymin=0.08, ymax=0.45, color='crimson', lw=3, linestyle='--', label='Cavity Boundary (Reflection/Vortex)')
    ax3.axvline(1.2, ymin=0.08, ymax=0.45, color='crimson', lw=3, linestyle='--')
    
    # Arrows showing motion
    ax3.annotate('', xy=(3.5, 1.8), xytext=(2.2, 1.8),
                 arrowprops=dict(facecolor='darkorange', edgecolor='darkorange', width=2, headwidth=8))
    ax3.text(2.6, 2.1, 'Travels freely at c\nNo cavity wall!', color='darkorange', fontweight='bold', fontsize=9.5)
    
    # Double arrow showing trapped circulation
    ax3.annotate('', xy=(0.8, -1.2), xytext=(-0.8, -1.2),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax3.text(-0.8, -0.6, 'Circulating / Standing in Cavity\nRest frame exists! Inertia m = E/c^2', color='purple', fontweight='bold', fontsize=9.5)
    
    ax3.set_ylim(-2.8, 3.2)
    ax3.set_title('2. Massless Particles vs. Massive Matter in the Substrate', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Spatial Coordinate x', fontsize=11, fontweight='bold')
    ax3.legend(loc='upper left', frameon=True, fontsize=8.5)
    
    # ---------------------------------------------------------
    # Panel 4: Mathematical Anatomy of Massless Particles
    # ---------------------------------------------------------
    ax4 = axs[1, 1]
    ax4.axis('off')
    massless_text = (
        "=========================================================================\n"
        "WHAT ABOUT MASSLESS PARTICLES AND WAVES? (Photons, Gluons, Gravitons)\n"
        "=========================================================================\n\n"
        "1. WHY ARE THEY MASSLESS (m_0 = 0)?\n"
        "   - In our substrate theory, a MASSLESS particle is an UNTRAPPED WAVE.\n"
        "   - It has no cavity walls, no circulating vortex trap, and no boundary!\n"
        "   - Because it is not locked in a cavity, its radius is INFINITE (R -> inf).\n"
        "     m = hbar / (R * c)  ==>  As R -> inf, Rest Mass m_0 = 0!\n\n"
        "2. WHY CAN'T A MASSLESS PARTICLE SIT AT REST?\n"
        "   - A substrate wave naturally propagates at the medium's speed of sound (c).\n"
        "   - It only 'rests' if you trap it in a self-enclosed loop (a cavity).\n"
        "   - An untrapped ripple always moves at v = c in all reference frames.\n"
        "   - Relativistic dispersion: E^2 = p^2 * c^2 + m_0^2 * c^4.\n"
        "     Since m_0 = 0, E = p * c.\n\n"
        "3. DO MASSLESS WAVES HAVE GRAVITY?\n"
        "   - YES! Even though m_0 = 0, a photon carries ENERGY E = h * nu.\n"
        "   - In the substrate, energy is wave displacement energy:\n"
        "     Stress-energy tensor T_{mu nu} depends on TOTAL ENERGY DENSITY,\n"
        "     not rest mass! A laser beam still carves a tiny depletion well (gravity)\n"
        "     in the substrate as it flies by, exactly as proven in General Relativity!"
    )
    ax4.text(0.01, 0.98, massless_text, va='top', ha='left', family='monospace', fontsize=9.2,
             bbox=dict(boxstyle="round,pad=0.8", fc="#fef9e7", ec="#f39c12", lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'particle_size_mass_paradox.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot successfully saved to: {output_path}")
    
    # Copy to artifact directory
    artifact_dir = r'C:\Users\Asta\.gemini\antigravity\brain\cfcab9e6-1707-463d-a5cf-0f6b32f4acb8'
    if os.path.exists(artifact_dir):
        shutil.copy(output_path, os.path.join(artifact_dir, 'particle_size_mass_paradox.png'))
        print("Copied to artifact directory.")

if __name__ == "__main__":
    data = run_analysis()
    plot_analysis(data)
