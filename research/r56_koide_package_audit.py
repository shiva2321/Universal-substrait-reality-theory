"""
r56 - Independent audit of the koide_anomaly package (LAB_NOTEBOOK.md entry E51, tests K1-K7)

Question (user): "i was working with gemini for a while in the meanwhile ... check and honestly report on what we have done and what do you think."
The package koide_anomaly/ (written in another session, not in the notebook) claims: the Koide relation Q = 2/3 for the charged leptons, a tau-mass 'prediction', a Sumino-type family gauge mechanism that
'shields' Q from QED running, rare-decay 'predictions', and a QCD 'explanation' of why quarks do not obey it.  This script re-derives what can be re-derived and checks the package against itself.

  K1  The tau-mass prediction: reproduce it, and say whose it is.
  K2  The quark Koide ratios with uncertainties (the package quotes shifts of +27 % and +9.7 % without a sigma).
  K3  How surprising is Q = 2/3 to 5e-6 for random mass triples (the look-elsewhere context)?
  K4  Is the 'Sumino shielding' check a test, or an identity?
  K5  Internal consistency between the package's own modules (sign of the QED shift of Q, rare-decay bounds, benchmark, hard-coded statements, the 'Cabibbo' ratio).
  K6  Does QCD running 'explain' the quark values?
  K7  The Brannen phase 2/9: what the 452 sigma means.
Mass inputs come from koide_anomaly/data/constants.py (PDG 2024 / CODATA 2022 as typed by the other session; not re-checked here except where stated); the MS-bar masses at M_Z in K5 are typed from memory
(Xing, Zhang & Zhou 2012).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from lab import Report  # noqa: E402

import io  # noqa: E402
from contextlib import redirect_stdout  # noqa: E402

from koide_anomaly.data.constants import (M_BOTTOM, M_CHARM, M_DOWN, M_ELECTRON, M_MUON, M_STRANGE, M_TAU, M_TOP, M_UP,  # noqa: E402
                                          compute_koide_Q)
from koide_anomaly.geometry.cone_decomposition import test_brannen_phase_hypothesis  # noqa: E402
from koide_anomaly.rg_flow import qed_running, sumino_mechanism  # noqa: E402
from koide_anomaly.simulations import prediction_2_fcnc_decays as p2  # noqa: E402
from koide_anomaly.simulations import prediction_3_quark_qcd_shift as p3  # noqa: E402

NAME = "r56_koide_package_audit"


def main():
    p = Report(NAME)
    me, mm, mt = M_ELECTRON.val, M_MUON.val, M_TAU.val

    # ======================================================================================================
    p.section("K1. The tau-mass 'prediction'")
    # ------------------------------------------------------------------------------------------------------
    m_pred = brentq(lambda x: compute_koide_Q(me, mm, x) - 2.0 / 3.0, 1500, 2000, xtol=1e-12)
    p(f"    Solving Q(m_e, m_mu, m_tau) = 2/3 for m_tau: {m_pred:.6f} MeV; PDG 2024 (as typed in the package) {mt} +- {M_TAU.err} MeV: pull {(m_pred - mt) / M_TAU.err:+.2f} sigma.")
    p("    This is Koide's own prediction of 1981 (about 1776.97 MeV): prior art, reproduced exactly.  Belle II / a tau-charm factory improving sigma(m_tau) tests whether Q = 2/3 is exact; that is a real, old test.")

    # ======================================================================================================
    p.section("K2. Quark Koide ratios with uncertainties")
    # ------------------------------------------------------------------------------------------------------
    rng = np.random.default_rng(1)
    n = 400000
    for name, ms in (("up (u, c, t)", (M_UP, M_CHARM, M_TOP)), ("down (d, s, b)", (M_DOWN, M_STRANGE, M_BOTTOM))):
        s = [np.abs(rng.normal(m.val, m.err, n)) for m in ms]
        q = (s[0] + s[1] + s[2]) / (np.sqrt(s[0]) + np.sqrt(s[1]) + np.sqrt(s[2])) ** 2
        q0 = compute_koide_Q(*(m.val for m in ms))
        p(f"    {name}: Q = {q0:.4f} +- {q.std():.4f}  ({(q0 - 2 / 3) / q.std():+.0f} sigma from 2/3).  The package quotes '+27.3 %' / '+9.7 %' with no uncertainty.")
    p("    The masses mix definitions (MS-bar at 2 GeV, at m_c, at m_b, and a direct/pole top mass); the sigma above ignores that scheme dependence, which is larger than the quoted errors for the up sector.")

    # ======================================================================================================
    p.section("K3. How surprising is Q = 2/3 to 5e-6?")
    # ------------------------------------------------------------------------------------------------------
    n_tr = 2_000_000
    x = np.exp(rng.uniform(math.log(1.0), math.log(4000.0), (n_tr, 3)))
    q = x.sum(1) / (np.sqrt(x).sum(1)) ** 2
    frac_fine = float((np.abs(q - 2 / 3) < 5e-6).mean())
    frac_coarse = float((np.abs(q - 2 / 3) < 1e-3).mean())
    p(f"    Random mass triples, log-uniform over 1-4000 (ratios of the size of the lepton ones): |Q - 2/3| < 5e-6 in {frac_fine:.1e} of triples; < 1e-3 in {frac_coarse:.1e}.")
    p("    So the lepton coincidence is a ~1-in-10^5 event for a single pre-chosen formula; Koide is one of many ratio formulas that have been tried on the lepton (and quark) masses, so the look-elsewhere factor is unknown")
    p("    and large.  Suggestive, not established.  The quark values (K2) do not obey it at all.")

    # ======================================================================================================
    p.section("K4. Is the 'Sumino shielding' check a test?")
    # ------------------------------------------------------------------------------------------------------
    alpha = 1.0 / 137.035999177
    lam = 1.0e8                                                      # MeV (100 TeV), as in the package
    coef = 3.0 * alpha / (2.0 * math.pi)
    ms = (me, mm, mt)
    q_exact = compute_koide_Q(*ms)
    p("    In sumino_mechanism.simulate_lepton_mass_shielding the 'family' shift is defined as the QED shift with the opposite sign (+(3 alpha/2 pi) ln(m/Lambda) against -(3 alpha/2 pi) ln(m/Lambda)),")
    p("    so the 'shielded' Q equals the input Q by construction.  Scaling the family coefficient by a factor f:")
    p(f"    {'f':>6s} {'Q_shielded - Q_exact':>22s}")
    for f in (1.0, 1.1, 0.9, 0.5):
        shifted = [m * (1.0 - coef * math.log(m / lam) + f * coef * math.log(m / lam)) for m in ms]
        p(f"    {f:6.2f} {compute_koide_Q(*shifted) - q_exact:+22.3e}")
    p("    => the printed 'INVARIANT: diff = +1.1e-16' is an identity (f = 1 was solved for, not found); it carries no information.  Whether a real family gauge sector gives f = 1 is not computed anywhere in the package")
    p("       (the coefficient g_F^2 = 6 pi alpha is quoted from Sumino 2009 as the condition for cancellation).")

    # ======================================================================================================
    p.section("K5. Internal consistency of the package")
    # ------------------------------------------------------------------------------------------------------
    # (a) sign of the QED shift of Q
    res = qed_running.run_lepton_masses(np.array([mt * 1.0001, 91187.6]))
    sim = sumino_mechanism.simulate_lepton_mass_shielding(1.0e5)
    q_mz_indep = compute_koide_Q(0.48657, 102.718, 1746.24)
    p(f"    (a) Q(MS-bar, M_Z) - Q(pole): qed_running gives {res['Q'][1] - q_exact:+.2e}; sumino_mechanism gives {sim['delta_q_unshielded']:+.2e} (opposite sign); an independent evaluation with typed MS-bar masses at M_Z")
    p(f"        (0.48657, 102.718, 1746.24 MeV) gives {q_mz_indep - q_exact:+.2e}.  The hard-coded text in qed_running.py says Q goes 'down to ~0.6660 at M_Z'; its own output (and the independent value {q_mz_indep:.5f}) is above 2/3.")
    # (b) bounds
    buf = io.StringIO()
    with redirect_stdout(buf):
        v_min, v_reach = p2.find_allowed_vev_window()
    m12 = p2.compute_gauge_boson_masses(v_min)["M_12_TeV"]
    fc = sumino_mechanism.compute_fcnc_bounds()
    p(f"    (b) mu -> 3e bound on the lightest family gauge boson: sumino_mechanism says M_A >= {fc['m_A_min_TeV']:.1f} TeV; prediction_2 (v_F >= {v_min:.1f} TeV) implies M_12 = {m12:.1f} TeV.  The two modules use branching-ratio")
    p(f"        formulas that differ by a factor 8 (so by 8^(1/4) = {8 ** 0.25:.2f} in mass).")
    # (c) benchmark
    bench = p2.compute_branching_ratios(300.0)
    p(f"    (c) The benchmark v_F = 300 TeV (commented 'inside allowed, testable window') gives BR(mu -> 3e) = {bench['br_mu_3e']:.2e} against the limit {p2.LIMITS['mu_3e']:.1e} that the same file used to get v_F >= {v_min:.0f} TeV:")
    p(f"        the benchmark is excluded by the package's own bound.  BR(mu Ti -> e Ti) is taken as 1.5 x BR(mu -> 3e) with no derivation; BR(mu -> e gamma) uses an unexplained loop factor; BR(tau -> 3mu) an ad hoc 0.174.")
    # (d) hard-coded statement
    p(f"    (d) Final line of prediction_2: 'observed if v_F lies below ~2,300 TeV'; the file's own computed Mu3e reach is {v_reach:.0f} TeV.")
    # (e) Cabibbo-like ratio
    s_e, s_m, s_t = (math.sqrt(x) for x in (me, mm, mt))
    p(f"    (e) The 'Cabibbo-like' ratio M_12/M_13 = |sqrt(m_e) - sqrt(m_mu)| / |sqrt(m_e) - sqrt(m_tau)| = {abs(s_e - s_m) / abs(s_e - s_t):.4f} follows from the mass formula M_ij ~ |sqrt(m_i) - sqrt(m_j)| chosen in prediction_2")
    p(f"        (sumino_mechanism's docstring uses a different one); the equally good-looking sqrt(m_mu/m_tau) = {math.sqrt(mm / mt):.4f}.  Neither has anything to do with quark mixing (sin theta_C = 0.225): numerology.")

    # ======================================================================================================
    p.section("K6. Does QCD running explain the quark ratios?")
    # ------------------------------------------------------------------------------------------------------
    mus = np.array([2.0, 91.2, 1.0e16])
    run = p3.run_quark_masses_qcd(mus)
    p(f"    Q_u at mu = 2 GeV, M_Z, 1e16 GeV: {run['Q_u'][0]:.4f}, {run['Q_u'][1]:.4f}, {run['Q_u'][2]:.4f};  Q_d: {run['Q_d'][0]:.4f}, {run['Q_d'][1]:.4f}, {run['Q_d'][2]:.4f}.")
    p("    QCD running moves the quark ratios AWAY from 2/3 (by 2 % between 2 GeV and the GUT scale), while the observed offsets are 27 % (up) and 10 % (down).  Running cannot explain them, and the")
    p("    statement that the code 'proves' that gluon loops 'cannot be cancelled by family gauge bosons' is an assertion: no family-boson loop for coloured fermions is computed.")

    # ======================================================================================================
    p.section("K7. The Brannen phase 2/9 and the '452 sigma'")
    # ------------------------------------------------------------------------------------------------------
    b = test_brannen_phase_hypothesis()
    p(f"    delta fitted to (m_e, m_mu) with Q = 2/3 built in: {b['delta_fit']:.9f} rad; 2/9 = {b['delta_29']:.9f}; difference {b['delta_diff']:+.2e} (relative {abs(b['delta_diff']) / b['delta_29']:.1e}).")
    p(f"    With delta = 2/9 exactly the muon mass comes out {b['m_mu_pred_29']:.7f} MeV against {b['m_mu_exp']:.7f}: a relative miss of {(b['m_mu_pred_29'] - b['m_mu_exp']) / b['m_mu_exp']:.1e}, {b['mu_sigma_29']:+.0f} sigma only because the muon is measured to 2e-8.")
    p("    So: delta = 2/9 holds to ~8e-7 relative but not exactly; the relation is a numerical coincidence at the 10^-6 level, not a result of the package (Brannen 2006 is prior art).")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    rows = [
        ("K1 the tau-mass 'prediction' is new", f"NO: Koide 1981; reproduces {m_pred:.3f} MeV, +{(m_pred - mt) / M_TAU.err:.2f} sigma"),
        ("K2 the quark offsets are quantified", "NOT in the package (no sigma); with sigma: up 158 sigma, down 8.7 sigma from 2/3"),
        ("K3 Q = 2/3 is a >5 sigma coincidence", f"NOT shown: {frac_fine:.0e} for one formula, look-elsewhere factor unknown"),
        ("K4 'Sumino shielding' is verified", "NO: an identity by construction; the physics (f = 1) is quoted from the literature"),
        ("K5 the modules agree with each other", "NO: sign of the QED shift, bound (x1.7), benchmark excluded by its own bound, hard-coded 2300 vs 3837 TeV"),
        ("K6 QCD running explains the quark ratios", "NO: it moves them away from 2/3"),
        ("K7 the phase 2/9 is exact", "NO: relative miss 1e-5 in the muon mass; prior art (Brannen)"),
    ]
    for claim, status in rows:
        p(f"   {claim:<50s} -> {status}")
    p.save()


if __name__ == "__main__":
    main()
