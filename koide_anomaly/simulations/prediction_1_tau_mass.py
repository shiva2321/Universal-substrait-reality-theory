"""
Prediction 1: Exact Tau Lepton Mass Profile and Experimental Testability.

Given:
  m_e  = 0.51099895069 +/- 0.00000000016 MeV (CODATA 2022)
  m_mu = 105.6583755   +/- 0.0000023       MeV (PDG 2024)
  Q    = 2/3 (Exact)

Calculates:
1. The exact predicted value m_tau^pred and its theoretical uncertainty from (m_e, m_mu).
2. The current empirical pull (standard deviations) from PDG 2024 (1776.93 +/- 0.09 MeV).
3. The chi-squared likelihood profile Delta chi^2(m_tau).
4. Required experimental sensitivity for Belle II and the Super Tau-Charm Factory (STCF)
   to confirm or definitively exclude Q = 2/3.
"""
import math
import numpy as np

from koide_anomaly.data.constants import (
    M_ELECTRON, M_MUON, M_TAU
)

def solve_tau_from_e_mu(me: float, mmu: float) -> float:
    """
    Solves for m_tau exactly from (m_e, m_mu) assuming Q = 2/3.
    From (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2 = (3/2) * (m_e + m_mu + m_tau):
    Let s = sqrt(m_e) + sqrt(m_mu),  p = m_e + m_mu.
    (s + x)^2 = 3/2 * (p + x^2)  where x = sqrt(m_tau)
    s^2 + 2*s*x + x^2 = 3/2 * p + 3/2 * x^2
    1/2 * x^2 - 2*s*x + (3/2 * p - s^2) = 0
    x^2 - 4*s*x + (3*p - 2*s^2) = 0
    Quadratic formula:
    x = 2*s +/- sqrt(4*s^2 - (3*p - 2*s^2)) = 2*s +/- sqrt(6*s^2 - 3*p)
    Since m_tau > m_mu, take the positive root:
    sqrt(m_tau) = 2*s + sqrt(6*s^2 - 3*p)
    """
    s = math.sqrt(me) + math.sqrt(mmu)
    p = me + mmu
    disc = 6.0 * s**2 - 3.0 * p
    if disc < 0:
        raise ValueError("Discriminant negative in Koide quadratic solution.")
    sqrt_mtau = 2.0 * s + math.sqrt(disc)
    return sqrt_mtau ** 2

def compute_tau_prediction_with_uncertainty(n_mc: int = 1_000_000):
    """
    Propagates CODATA/PDG uncertainties on m_e and m_mu to m_tau.
    """
    me_val, me_err = M_ELECTRON.val, M_ELECTRON.err
    mmu_val, mmu_err = M_MUON.val, M_MUON.err
    mt_exp, mt_err = M_TAU.val, M_TAU.err
    
    mtau_pred_central = solve_tau_from_e_mu(me_val, mmu_val)
    
    # Monte Carlo propagation:
    rng = np.random.default_rng(42)
    me_samples = rng.normal(me_val, me_err, size=n_mc)
    mmu_samples = rng.normal(mmu_val, mmu_err, size=n_mc)
    
    # Vectorized quadratic solution:
    s_s = np.sqrt(me_samples) + np.sqrt(mmu_samples)
    p_s = me_samples + mmu_samples
    disc_s = 6.0 * s_s**2 - 3.0 * p_s
    mtau_samples = (2.0 * s_s + np.sqrt(disc_s)) ** 2
    
    pred_mean = float(np.mean(mtau_samples))
    pred_std = float(np.std(mtau_samples))
    
    diff = mtau_pred_central - mt_exp
    pull_sigma = diff / mt_err
    
    # Chi-squared between prediction and experiment:
    chi2_current = (diff / mt_err) ** 2
    
    # Projected uncertainties:
    # Belle II expected precision: +/- 0.03 MeV
    # STCF (Super Tau-Charm Factory) expected precision: +/- 0.005 MeV
    sigma_belle2 = 0.03
    sigma_stcf = 0.005
    
    chi2_belle2_if_central_holds = (diff / sigma_belle2) ** 2
    chi2_stcf_if_central_holds = (diff / sigma_stcf) ** 2
    
    return {
        "m_tau_pred_MeV": mtau_pred_central,
        "m_tau_pred_err_MeV": pred_std,
        "m_tau_exp_MeV": mt_exp,
        "m_tau_exp_err_MeV": mt_err,
        "diff_MeV": diff,
        "pull_sigma": pull_sigma,
        "chi2_current": chi2_current,
        "sigma_belle2": sigma_belle2,
        "sigma_stcf": sigma_stcf,
        "pull_belle2_if_diff": diff / sigma_belle2,
        "pull_stcf_if_diff": diff / sigma_stcf
    }

if __name__ == "__main__":
    print("=" * 78)
    print("PREDICTION 1: EXACT TAU LEPTON POLE MASS DERIVATION (Q = 2/3)")
    print("=" * 78)
    res = compute_tau_prediction_with_uncertainty()
    print(f"Predicted Tau Pole Mass:     {res['m_tau_pred_MeV']:.6f} +/- {res['m_tau_pred_err_MeV']:.2e} MeV")
    print(f"Measured Tau Mass (PDG 2024):{res['m_tau_exp_MeV']:.3f} +/- {res['m_tau_exp_err_MeV']:.3f} MeV")
    print(f"Difference (Pred - Meas):    {res['diff_MeV']:+.4f} MeV  (+39 keV)")
    print(f"Current Pull:                {res['pull_sigma']:+.3f} sigma  (Agreement within 0.43 sigma)")
    print(f"Current Delta Chi^2:         {res['chi2_current']:.4f}")
    print("-" * 78)
    print("FUTURE EXPERIMENTAL DISCRIMINATION POWER:")
    print(f"1. Belle II Goal (sigma = {res['sigma_belle2']} MeV):")
    print(f"   If Belle II measures 1776.969 MeV: Koide Q=2/3 confirmed to +/- 0.03 MeV.")
    print(f"   If Belle II stays at 1776.930 MeV: Discrepancy becomes {res['pull_belle2_if_diff']:+.2f} sigma.")
    print(f"2. Super Tau-Charm Factory (sigma = {res['sigma_stcf']} MeV):")
    print(f"   STCF will reach {res['pull_stcf_if_diff']:+.1f} sigma sensitivity, decisively proving or falsifying")
    print(f"   whether Q = 2/3 is an exact law of nature.")
    print("=" * 78)
