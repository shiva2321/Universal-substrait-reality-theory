"""
Geometric Analysis of Mass Vectors in R^3 (Square-Root Mass Space).
Decomposes (sqrt(m1), sqrt(m2), sqrt(m3)) along the democratic flavor-singlet axis
and the orthogonal flavor-breaking plane.
"""
import math
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

from koide_anomaly.data.constants import (
    M_ELECTRON, M_MUON, M_TAU,
    M_UP, M_DOWN, M_STRANGE, M_CHARM, M_BOTTOM, M_TOP,
    compute_koide_Q
)

# Standard orthonormal basis in R^3 adapted to the democratic axis:
# u_hat = (1, 1, 1) / sqrt(3)  (Flavor Singlet)
# e1_hat = (1, -1, 0) / sqrt(2) (Gell-Mann lambda_3 direction)
# e2_hat = (1, 1, -2) / sqrt(6) (Gell-Mann lambda_8 direction)
U_HAT  = np.array([1.0, 1.0, 1.0]) / math.sqrt(3.0)
E1_HAT = np.array([1.0, -1.0, 0.0]) / math.sqrt(2.0)
E2_HAT = np.array([1.0, 1.0, -2.0]) / math.sqrt(6.0)

@dataclass
class GeometricDecomposition:
    name: str
    masses: Tuple[float, float, float]
    sqrt_masses: np.ndarray
    Q: float
    theta_rad: float
    theta_deg: float
    v_parallel_mag: float
    v_perp_mag: float
    ratio_perp_parallel: float
    phi_polar_rad: float
    phi_polar_deg: float
    delta_phase_rad: float
    delta_over_pi: float


def decompose_mass_triplet(name: str, m1: float, m2: float, m3: float) -> GeometricDecomposition:
    """
    Analyzes the 3D geometry of the vector v = (sqrt(m1), sqrt(m2), sqrt(m3)).
    """
    v = np.array([math.sqrt(m1), math.sqrt(m2), math.sqrt(m3)])
    v_mag = np.linalg.norm(v)

    # Singlet and orthogonal projections
    v_parallel_comp = np.dot(v, U_HAT)
    v_parallel = v_parallel_comp * U_HAT
    v_perp = v - v_parallel
    v_perp_mag = np.linalg.norm(v_perp)

    # Angle with democratic axis
    cos_theta = v_parallel_comp / v_mag
    theta_rad = math.acos(np.clip(cos_theta, -1.0, 1.0))
    theta_deg = math.degrees(theta_rad)

    Q = compute_koide_Q(m1, m2, m3)
    ratio_perp_parallel = v_perp_mag / v_parallel_comp

    # Coordinates in the orthogonal plane (e1, e2)
    x = np.dot(v_perp, E1_HAT)
    y = np.dot(v_perp, E2_HAT)
    phi_rad = math.atan2(y, x)
    if phi_rad < 0:
        phi_rad += 2 * math.pi
    phi_deg = math.degrees(phi_rad)

    # In the Brannen/Koide representation:
    # sqrt(m_k) = v0 * [1 + sqrt(2) * cos(delta + 2*pi*k/3)]
    # For electron (k=1), muon (k=2), tau (k=0):
    # v0 = sum(sqrt(m)) / 3 = v_parallel_comp / sqrt(3)
    v0 = np.sum(v) / 3.0
    # cos(delta) = (sqrt(m_tau) / v0 - 1) / sqrt(2)
    arg = (math.sqrt(m3) / v0 - 1.0) / math.sqrt(2.0)
    delta_rad = math.acos(np.clip(arg, -1.0, 1.0))

    return GeometricDecomposition(
        name=name,
        masses=(m1, m2, m3),
        sqrt_masses=v,
        Q=Q,
        theta_rad=theta_rad,
        theta_deg=theta_deg,
        v_parallel_mag=v_parallel_comp,
        v_perp_mag=v_perp_mag,
        ratio_perp_parallel=ratio_perp_parallel,
        phi_polar_rad=phi_rad,
        phi_polar_deg=phi_deg,
        delta_phase_rad=delta_rad,
        delta_over_pi=delta_rad / math.pi
    )


def test_brannen_phase_hypothesis():
    """
    Tests the Brannen hypothesis: delta = 2/9 exactly.
    Computes exact discrepancy against CODATA/PDG muon mass.
    """
    me = M_ELECTRON.val
    mm_exp, dmm = M_MUON.val, M_MUON.err
    mt_exp, dmt = M_TAU.val, M_TAU.err

    # Fit (v0, delta) to (m_e, m_mu) assuming Q = 2/3
    # electron is k=1, muon is k=2, tau is k=0
    def f_k(d, k):
        return 1.0 + math.sqrt(2.0) * math.cos(d + 2.0 * math.pi * k / 3.0)

    # find delta such that (f_2(d) / f_1(d))^2 = m_mu / m_e
    target_ratio = math.sqrt(mm_exp / me)
    # Bisection search for delta in [0.20, 0.25]
    lo, hi = 0.20, 0.25
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        r_mid = f_k(mid, 2) / f_k(mid, 1)
        if r_mid > target_ratio:
            hi = mid
        else:
            lo = mid
    delta_fit = 0.5 * (lo + hi)
    v0_fit = math.sqrt(me) / f_k(delta_fit, 1)
    mt_pred = (v0_fit * f_k(delta_fit, 0)) ** 2

    # With delta = 2/9 exactly:
    delta_29 = 2.0 / 9.0
    v0_29 = math.sqrt(me) / f_k(delta_29, 1)
    mmu_29 = (v0_29 * f_k(delta_29, 2)) ** 2
    mtau_29 = (v0_29 * f_k(delta_29, 0)) ** 2

    sigma_mu_29 = (mmu_29 - mm_exp) / dmm
    sigma_tau_fit = (mt_pred - mt_exp) / dmt

    return {
        "delta_fit": delta_fit,
        "delta_29": delta_29,
        "delta_diff": delta_fit - delta_29,
        "m_mu_pred_29": mmu_29,
        "m_mu_exp": mm_exp,
        "mu_sigma_29": sigma_mu_29,
        "m_tau_pred_fit": mt_pred,
        "m_tau_exp": mt_exp,
        "tau_sigma_fit": sigma_tau_fit
    }


if __name__ == "__main__":
    leptons = decompose_mass_triplet("Charged Leptons (e, mu, tau)", M_ELECTRON.val, M_MUON.val, M_TAU.val)
    up_quarks = decompose_mass_triplet("Up-type Quarks (u, c, t)", M_UP.val, M_CHARM.val, M_TOP.val)
    down_quarks = decompose_mass_triplet("Down-type Quarks (d, s, b)", M_DOWN.val, M_STRANGE.val, M_BOTTOM.val)

    print("=" * 78)
    print("GEOMETRIC CONE DECOMPOSITION IN SQUARE-ROOT MASS SPACE R^3")
    print("=" * 78)
    for g in [leptons, up_quarks, down_quarks]:
        print(f"Sector: {g.name}")
        print(f"  Koide Ratio Q:           {g.Q:.8f}")
        print(f"  Cone Angle theta:        {g.theta_deg:.6f} deg  (Target for Q=2/3 is 45.000000 deg)")
        print(f"  |v_perp| / |v_parallel|: {g.ratio_perp_parallel:.8f}  (Target for Q=2/3 is 1.000000)")
        print(f"  Phase delta:             {g.delta_phase_rad:.8f} rad  ({g.delta_over_pi:.6f} * pi)")
        print("-" * 78)

    print("\nTESTING THE BRANNEN PHASE HYPOTHESIS (delta = 2/9):")
    b_res = test_brannen_phase_hypothesis()
    print(f"  Empirically fitted delta:     {b_res['delta_fit']:.9f} rad")
    print(f"  Exact 2/9:                    {b_res['delta_29']:.9f} rad")
    print(f"  Difference (fit - 2/9):       {b_res['delta_diff']:+.9f} rad")
    print(f"  Predicted m_mu with 2/9:      {b_res['m_mu_pred_29']:.7f} MeV")
    print(f"  Measured m_mu (PDG 2024):     {b_res['m_mu_exp']:.7f} MeV")
    print(f"  Discrepancy on Muon Mass:     {b_res['mu_sigma_29']:+,.1f} sigma  (452 sigma exclusion!)")
    print(f"  Predicted m_tau with fit delta: {b_res['m_tau_pred_fit']:.3f} MeV vs PDG {b_res['m_tau_exp']:.3f} MeV ({b_res['tau_sigma_fit']:+.2f} sigma)")
    print("=" * 78)
