"""
Coleman-Weinberg 1-Loop Radiative Effective Potential for Family Gauge Symmetry.
Calculates the exact gauge boson mass matrix for SU(3)_family and tests whether
radiative corrections dynamically stabilize the Koide angle theta = 45 deg (Q = 2/3).
"""
import math
import numpy as np
import sympy as sp
from scipy.optimize import minimize_scalar

from koide_anomaly.data.constants import ALPHA_EM_0

# Gell-Mann matrices for SU(3)
LAMBDA_MATRICES = [
    np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex),
    np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex),
    np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex),
    np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex),
    np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex),
    np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex),
    np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex),
    np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex) / math.sqrt(3.0)
]
T_GENERATORS = [L / 2.0 for L in LAMBDA_MATRICES]

def compute_gauge_boson_mass_matrix(phi_diag: np.ndarray, g_F: float) -> np.ndarray:
    """
    Computes the exact 8x8 mass-squared matrix (M_A^2)_{ab} for SU(3)_family gauge bosons.
    Assuming the family Higgs Phi transforms as a Hermitian matrix (adjoint/symmetric VEV):
    (D_mu Phi) = d_mu Phi - i * g_F * [T_a, Phi]
    Trace kinetic term: Tr(D_mu Phi D^mu Phi) gives:
    (M_A^2)_{ab} = g_F^2 * Tr( [T_a, Phi] [T_b, Phi]^\dagger )
    """
    Phi = np.diag(phi_diag.astype(complex))
    M2 = np.zeros((8, 8), dtype=float)
    for a in range(8):
        comm_a = T_GENERATORS[a] @ Phi - Phi @ T_GENERATORS[a]
        for b in range(a, 8):
            comm_b = T_GENERATORS[b] @ Phi - Phi @ T_GENERATORS[b]
            # Tr( comm_a @ comm_b^\dagger )
            val = np.real(np.trace(comm_a @ comm_b.conj().T))
            M2[a, b] = g_F**2 * val
            M2[b, a] = M2[a, b]
    return M2

def coleman_weinberg_potential(theta_rad: float, alpha_rad: float, R: float = 100.0, mu_renorm: float = 100.0) -> float:
    """
    Calculates V_CW(theta, alpha) on the sphere of radius R:
    phi_k = (R / sqrt(3)) * [cos(theta) + sqrt(2)*sin(theta)*cos(alpha + 2*pi*k/3)]
    V_CW = (3 / (64 * pi^2)) * sum_{a=1}^8 M_a^4 * [ln(M_a^2 / mu^2) - 5/6]
    """
    g_F = math.sqrt(6.0 * math.pi * ALPHA_EM_0.val)
    # Eigenvalues of Phi:
    phi = np.array([
        (R / math.sqrt(3.0)) * (math.cos(theta_rad) + math.sqrt(2.0) * math.sin(theta_rad) * math.cos(alpha_rad + 2.0 * math.pi * k / 3.0))
        for k in range(3)
    ])
    
    M2 = compute_gauge_boson_mass_matrix(phi, g_F)
    eig_M2 = np.linalg.eigvalsh(M2)
    
    # Exclude zero modes (unbroken generators if any)
    v_cw = 0.0
    for m2 in eig_M2:
        if m2 > 1e-12:
            ratio = m2 / (mu_renorm**2)
            log_term = math.log(max(ratio, 1e-15)) - (5.0 / 6.0)
            v_cw += (3.0 / (64.0 * math.pi**2)) * (m2**2) * log_term
    return v_cw

def scan_coleman_weinberg_in_theta(alpha_rad: float = 0.222222, n_points: int = 200):
    """
    Scans the Coleman-Weinberg potential as a function of the Koide angle theta
    from 10 deg to 80 deg.
    """
    thetas_deg = np.linspace(10.0, 80.0, n_points)
    thetas_rad = np.radians(thetas_deg)
    pot_vals = [coleman_weinberg_potential(th, alpha_rad) for th in thetas_rad]
    
    min_idx = np.argmin(pot_vals)
    theta_min_deg = thetas_deg[min_idx]
    
    # Calculate derivative at 45 deg numerically:
    eps = 1e-4
    v_plus = coleman_weinberg_potential(math.radians(45.0 + eps), alpha_rad)
    v_minus = coleman_weinberg_potential(math.radians(45.0 - eps), alpha_rad)
    dV_dtheta_at_45 = (v_plus - v_minus) / (2.0 * math.radians(eps))
    
    return {
        "thetas_deg": thetas_deg,
        "pot_vals": pot_vals,
        "theta_min_deg": theta_min_deg,
        "v_at_45": coleman_weinberg_potential(math.radians(45.0), alpha_rad),
        "dV_dtheta_at_45": dV_dtheta_at_45
    }

if __name__ == "__main__":
    print("=" * 78)
    print("COLEMAN-WEINBERG 1-LOOP EFFECTIVE POTENTIAL FOR SU(3)_family")
    print("=" * 78)
    scan_res = scan_coleman_weinberg_in_theta()
    print(f"Angle corresponding to exact Koide Q=2/3: 45.0000 deg")
    print(f"Global minimum of Coleman-Weinberg V_CW:   {scan_res['theta_min_deg']:.2f} deg")
    print(f"dV_CW / dtheta at theta = 45 deg:         {scan_res['dV_dtheta_at_45']:+.4e}")
    print("-" * 78)
    print("HONEST THEORETICAL VERDICT:")
    if abs(scan_res['theta_min_deg'] - 45.0) < 1.0:
        print("  RESULT: The Coleman-Weinberg radiative potential dynamically stabilizes theta ~ 45 deg!")
    else:
        print(f"  RESULT: Pure SU(3)_family gauge boson loops alone minimize at theta = {scan_res['theta_min_deg']:.2f} deg,")
        print("          meaning pure gauge boson radiative corrections DO NOT automatically lock theta = 45 deg.")
        print("          An additional scalar potential or discrete symmetry in the matter sector is required.")
    print("=" * 78)
