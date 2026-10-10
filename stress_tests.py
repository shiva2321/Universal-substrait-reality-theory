"""
Stress-Testing the Substrate-Cavity Hypothesis against Precision Experimental Physics.
Evaluates:
1. Dimensionality and Gauss Law: Inverse-Square Law deviation vs. Eöt-Wash experiment limits.
2. Speed of Substrate Ripple vs. Light Speed: GW170817 constraint |c_gw/c - 1| < 1e-15.
3. Fluid Viscosity & Drag vs. Planetary Orbital Decay (Landau Superfluid Criterion).
4. Scalar vs. Tensor Light Bending: Eddington/VLBI deflection factor (gamma - 1).
5. Weak Equivalence Principle: MICROSCOPE satellite bound eta < 1e-15.
"""

import numpy as np
import matplotlib.pyplot as plt

def compute_stress_test_metrics():
    print("Computing quantitative stress-tests...")
    
    # -------------------------------------------------------------
    # Test 1: Extra Dimensions & Short-Range Gravity (Eöt-Wash)
    # Potential: V(r) = - G M/r * (1 + alpha * exp(-r / lambda_extra))
    # Or in flat D dimensions: V(r) ~ 1/r^(D-2) for r < R_c, and 1/r for r > R_c
    # -------------------------------------------------------------
    r_microns = np.logspace(-1, 3, 300) # 0.1 micron to 1000 microns
    R_compact = 44.0 # microns (experimental bound from Eöt-Wash)
    
    # Force deviation ratio F(r) / F_Newton(r)
    # For r << R_c in 5D (d=1 extra dimension): F ~ 1/r^3 => ratio ~ (R_c / r)
    deviation_5D = 1.0 + (R_compact / np.maximum(r_microns, 0.01)) * (r_microns < R_compact)
    
    # -------------------------------------------------------------
    # Test 2: Gravitational Wave Speed vs Excitation Speed
    # GW170817: |c_gw - c| / c < 3e-15
    # If substrate sound speed c_s differs from excitation velocity c:
    # delta_c = |c_s - c| / c
    # -------------------------------------------------------------
    gw_bound = 3e-15
    
    # -------------------------------------------------------------
    # Test 3: Planetary Drag (Landau Superfluid Criterion)
    # Normal viscous medium would cause Earth orbital decay dR/dt ~ - 6*pi*eta*R / M
    # Earth orbital stability over 4.5 Gyr requires dynamic viscosity eta_substrate < 10^(-27) Pa*s
    # In a superfluid at T=0, drag is strictly 0 for v < v_Landau = c_s.
    # -------------------------------------------------------------
    eta_max_allowed = 1e-27 # Pa*s
    
    # -------------------------------------------------------------
    # Test 4: Scalar vs Tensor Light Deflection Parameter gamma
    # General Relativity (Tensor): gamma = 1, deflection theta = 4 G M / (c^2 R)
    # Pure Scalar Cavity: gamma = 0, deflection theta = 2 G M / (c^2 R)
    # Cassini spacecraft constraint: |gamma - 1| < 2.3e-5
    # -------------------------------------------------------------
    gamma_scalar = 0.0
    gamma_tensor = 1.0
    cassini_bound = 2.3e-5
    
    # -------------------------------------------------------------
    # Test 5: Weak Equivalence Principle (MICROSCOPE)
    # eta = |a_1 - a_2| / a < 1.5e-15
    # -------------------------------------------------------------
    microscope_bound = 1.5e-15
    
    return {
        "r_microns": r_microns,
        "deviation_5D": deviation_5D,
        "R_compact": R_compact,
        "gw_bound": gw_bound,
        "eta_max_allowed": eta_max_allowed,
        "cassini_bound": cassini_bound,
        "microscope_bound": microscope_bound
    }

def plot_stress_tests(data):
    fig, axs = plt.subplots(2, 2, figsize=(14, 11))
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Subplot 1: Short-Range Gravity & Dimensional Crossover
    r = data["r_microns"]
    axs[0, 0].loglog(r, data["deviation_5D"], 'r-', lw=2.5, label='5D Substrate Cavity Model ($R_c = 44\\mu\\mathrm{m}$)')
    axs[0, 0].axhline(1.0, color='k', linestyle='--', lw=1.5, label='Standard 3D Newtonian ($1/r^2$)')
    axs[0, 0].axvline(data["R_compact"], color='blue', linestyle=':', lw=2, label=r'Eöt-Wash Constraint Limit ($R_c \leq 44\,\mu\mathrm{m}$)')
    axs[0, 0].fill_between(r, 1.0, data["deviation_5D"], where=(r < data["R_compact"]), color='red', alpha=0.15)
    axs[0, 0].set_xlabel(r'Distance $r$ [micrometers ($\mu$m)]', fontsize=12)
    axs[0, 0].set_ylabel(r'Force Ratio $F(r) / F_{\mathrm{Newton}}$', fontsize=12)
    axs[0, 0].set_title('Test 1: Extra-Dimensional Cavity Scaling vs Eöt-Wash', fontsize=13, fontweight='bold')
    axs[0, 0].legend(loc='upper right', frameon=True)
    
    # Subplot 2: Metric Component Deflection (Tensor vs Scalar)
    categories = ['Pure Scalar Cavity', 'Observed Reality (VLBI/Cassini)', 'Tensor Einstein Gravity']
    gamma_vals = [0.0, 1.0, 1.0]
    errors = [0.0, 2.3e-5, 0.0]
    colors = ['#e74c3c', '#2ecc71', '#3498db']
    bars = axs[0, 1].bar(categories, gamma_vals, yerr=errors, color=colors, width=0.5, capsize=8, edgecolor='black')
    axs[0, 1].axhline(1.0, color='gray', linestyle='--')
    axs[0, 1].set_ylabel(r'PPN Parameter $\gamma$ (Light Deflection Factor)', fontsize=12)
    axs[0, 1].set_ylim(-0.2, 1.3)
    axs[0, 1].set_title('Test 2: Light Bending Parameter $\\gamma$ (Cassini/Eddington)', fontsize=13, fontweight='bold')
    for bar in bars:
        height = bar.get_height()
        axs[0, 1].annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 6), textcoords="offset points",
                           ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Subplot 3: Wave Speeds (GW170817 Test)
    speeds = ['Light Speed $c$', 'GW Speed $c_{gw}$ (Observed)', 'Substrate Acoustic Speed $c_s$ Req.']
    ratios = [1.0, 1.0, 1.0]
    axs[1, 0].barh(speeds, ratios, color=['#9b59b6', '#3498db', '#f39c12'], height=0.4, edgecolor='black')
    axs[1, 0].set_xlim(0.99999999999999, 1.00000000000001)
    axs[1, 0].set_xlabel('Speed Ratio relative to Light ($v / c$)', fontsize=12)
    axs[1, 0].set_title(r'Test 3: Propagation Speed Alignment ($|c_{gw}/c - 1| < 10^{-15}$)', fontsize=13, fontweight='bold')
    axs[1, 0].text(1.0, 1, r' $\Delta c / c < 3 \times 10^{-15}$', va='center', ha='left', fontsize=11, color='blue', fontweight='bold')
    
    # Subplot 4: Experimental Frontier Overview
    tests = ['Weak Equiv. Principle (MICROSCOPE)', 'Light Deflection (Cassini)', 'GW Speed Matching (GW170817)', 'Vacuum Drag / Viscosity Limit']
    tolerances = [1e-15, 2.3e-5, 3e-15, 1e-27]
    log_tol = np.log10(tolerances)
    y_pos = np.arange(len(tests))
    axs[1, 1].barh(y_pos, np.abs(log_tol), color='#1abc9c', height=0.5, edgecolor='black')
    axs[1, 1].set_yticks(y_pos)
    axs[1, 1].set_yticklabels(tests, fontsize=11)
    axs[1, 1].set_xlabel(r'Precision Constraint Order of Magnitude: $-\log_{10}(\epsilon)$', fontsize=12)
    axs[1, 1].set_title('Test 4: Experimental Bounds Constraining Substrate Models', fontsize=13, fontweight='bold')
    for i, v in enumerate(np.abs(log_tol)):
        axs[1, 1].text(v + 0.5, i, f'$10^{{{int(log_tol[i])}}}$', va='center', fontsize=11, fontweight='bold')
    axs[1, 1].set_xlim(0, 32)
    
    plt.tight_layout()
    output_path = r'f:\Reality_theory\stress_tests.png'
    plt.savefig(output_path, dpi=300)
    print(f"Stress test plots successfully saved to: {output_path}")

if __name__ == "__main__":
    data = compute_stress_test_metrics()
    plot_stress_tests(data)
