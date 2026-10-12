"""
Precision Experimental Constants and Koide Parameter Benchmarks.
Sources:
- CODATA 2022 (Tiesinga et al., Rev. Mod. Phys. 97, 025002 (2025))
- PDG 2024 (Navas et al., Phys. Rev. D 110, 030001 (2024))
"""
import math
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class MeasuredValue:
    val: float
    err: float
    unit: str
    source: str

    def __str__(self):
        return f"{self.val:.8g} +/- {self.err:.2g} {self.unit} ({self.source})"

# --- Charged Leptons (Pole masses) ---
M_ELECTRON = MeasuredValue(0.51099895069, 0.00000000016, "MeV", "CODATA 2022 / PDG 2024")
M_MUON     = MeasuredValue(105.6583755,   0.0000023,       "MeV", "PDG 2024")
M_TAU      = MeasuredValue(1776.93,       0.09,            "MeV", "PDG 2024 (BESIII/Belle)")

# --- Quarks (MS-bar at 2 GeV for light quarks, pole/running for heavy) ---
M_UP       = MeasuredValue(2.16,   0.49,  "MeV", "PDG 2024 (MS-bar @ 2 GeV)")
M_DOWN     = MeasuredValue(4.67,   0.48,  "MeV", "PDG 2024 (MS-bar @ 2 GeV)")
M_STRANGE  = MeasuredValue(93.4,   8.6,   "MeV", "PDG 2024 (MS-bar @ 2 GeV)")
M_CHARM    = MeasuredValue(1270.0, 20.0,  "MeV", "PDG 2024 (MS-bar @ m_c)")
M_BOTTOM   = MeasuredValue(4180.0, 30.0,  "MeV", "PDG 2024 (MS-bar @ m_b)")
M_TOP      = MeasuredValue(172570.0, 340.0, "MeV", "PDG 2024 (Direct/Pole)")

# --- Electroweak & Couplings ---
ALPHA_EM_0 = MeasuredValue(1.0 / 137.035999177, 1.5e-10, "dimensionless", "CODATA 2022")
ALPHA_EM_MZ = MeasuredValue(1.0 / 127.952, 0.009, "dimensionless", "PDG 2024 @ M_Z")
M_Z = MeasuredValue(91187.6, 2.1, "MeV", "PDG 2024")
M_W = MeasuredValue(80369.2, 13.3, "MeV", "PDG 2024")


def compute_koide_Q(m1: float, m2: float, m3: float) -> float:
    """Exact formula for Koide Q: sum(m) / (sum(sqrt(m)))^2."""
    s_m = m1 + m2 + m3
    s_sqrt = math.sqrt(m1) + math.sqrt(m2) + math.sqrt(m3)
    return s_m / (s_sqrt ** 2)


def compute_koide_charged_leptons(n_mc: int = 1_000_000):
    """
    Computes Q for charged leptons with both linear analytical error propagation
    and high-statistics Monte Carlo sampling.
    """
    me, dme = M_ELECTRON.val, M_ELECTRON.err
    mm, dmm = M_MUON.val, M_MUON.err
    mt, dmt = M_TAU.val, M_TAU.err

    q_central = compute_koide_Q(me, mm, mt)

    # Analytical partial derivatives:
    # dQ/dm_i = 1/(sum_sqrt)^2 - 2 * sum_m / (sum_sqrt)^3 * (1 / (2 * sqrt(m_i)))
    sum_m = me + mm + mt
    sum_sqrt = math.sqrt(me) + math.sqrt(mm) + math.sqrt(mt)
    denom2 = sum_sqrt ** 2
    denom3 = sum_sqrt ** 3

    dq_dme = 1.0 / denom2 - (sum_m / denom3) / math.sqrt(me)
    dq_dmm = 1.0 / denom2 - (sum_m / denom3) / math.sqrt(mm)
    dq_dmt = 1.0 / denom2 - (sum_m / denom3) / math.sqrt(mt)

    sigma_q_analytic = math.sqrt((dq_dme * dme)**2 + (dq_dmm * dmm)**2 + (dq_dmt * dmt)**2)

    # Monte Carlo verification
    rng = np.random.default_rng(42)
    sample_me = rng.normal(me, dme, size=n_mc)
    sample_mm = rng.normal(mm, dmm, size=n_mc)
    sample_mt = rng.normal(mt, dmt, size=n_mc)

    sample_q = (sample_me + sample_mm + sample_mt) / (
        (np.sqrt(sample_me) + np.sqrt(sample_mm) + np.sqrt(sample_mt)) ** 2
    )

    q_mc_mean = float(np.mean(sample_q))
    q_mc_std = float(np.std(sample_q))

    two_thirds = 2.0 / 3.0
    delta_q = q_central - two_thirds
    pull_sigma = delta_q / sigma_q_analytic

    return {
        "Q_central": q_central,
        "Q_analytic_err": sigma_q_analytic,
        "Q_mc_mean": q_mc_mean,
        "Q_mc_std": q_mc_std,
        "target": two_thirds,
        "difference": delta_q,
        "pull_sigma": pull_sigma,
        "derivatives": {"dQ/dme": dq_dme, "dQ/dmm": dq_dmm, "dQ/dmt": dq_dmt}
    }


if __name__ == "__main__":
    res = compute_koide_charged_leptons()
    print("=" * 70)
    print("KOIDE RELATION BENCHMARK (PDG 2024 / CODATA 2022)")
    print("=" * 70)
    print(f"Q (central)         = {res['Q_central']:.10f}")
    print(f"Q uncertainty (1s)  = {res['Q_analytic_err']:.10f}")
    print(f"Q (Monte Carlo)     = {res['Q_mc_mean']:.10f} +/- {res['Q_mc_std']:.10f}")
    print(f"Exact 2/3           = {res['target']:.10f}")
    print(f"Difference (Q - 2/3)= {res['difference']:+.10f}")
    print(f"Sigma deviation     = {res['pull_sigma']:+.3f} sigma")
    print("-" * 70)
    print("Sensitivity Analysis (Uncertainty Budget):")
    dq = res['derivatives']
    dme, dmm, dmt = M_ELECTRON.err, M_MUON.err, M_TAU.err
    print(f"  Electron contribution: {abs(dq['dQ/dme'] * dme):.2e}")
    print(f"  Muon contribution:     {abs(dq['dQ/dmm'] * dmm):.2e}")
    print(f"  Tau contribution:      {abs(dq['dQ/dmt'] * dmt):.2e}  (<-- completely dominates)")
    print("=" * 70)
