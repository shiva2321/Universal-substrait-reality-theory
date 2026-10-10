"""
Audit 02 - The numerical "derivations" (electron mass, lepton masses, proton/electron
ratio, dark/baryon ratio, neutron-proton split) tested properly:

  * compared with the experimental value using its real 1-sigma uncertainty
    (a match is judged in standard deviations, not in "% accuracy");
  * checked for prior art;
  * checked for the look-elsewhere effect: how often does a formula of the
    SAME SHAPE, built from equally "natural" ingredients, land just as close
    to an ARBITRARY target?
"""
import math
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (G, alpha, banner, c, dm_np_MeV, eV, hbar, m_e_kg, m_e_MeV,  # noqa: E402
                    m_mu_MeV, m_tau_MeV, mu_pe, omega_b_h2, omega_c_h2, planck_mass)


def electron_formula(a):
    """USRT 'master formula': m_e = m_P (sqrt3/2) exp(-[3/(8a) - (a/2pi) sqrt12])."""
    mP, _ = planck_mass()
    return mP * (math.sqrt(3) / 2) * math.exp(-(3 / (8 * a) - a / (2 * math.pi) * math.sqrt(12)))


def section_electron(p):
    p(banner("1. Electron mass formula  m_e = m_P (sqrt3/2) exp(-[3/(8 alpha) - (alpha/2pi) sqrt12])"))
    a, da = alpha
    mP, dmP = planck_mass()
    me, dme = m_e_kg
    S_target = math.log(mP / me)
    dS_target = math.hypot(dmP / mP, dme / me)
    p(f"ln(m_P/m_e) = {S_target:.7f} +- {dS_target:.1e}   (uncertainty set by G: 2.2e-5 relative)")
    steps = [
        ("exp(-3/(8a))                       [found by noticing 51.53 ~ 0.375*137]", 1.0, 3 / (8 * a)),
        ("(sqrt3/2) exp(-3/(8a))             [+ prefactor picked to fit]", math.sqrt(3) / 2, 3 / (8 * a)),
        ("(sqrt3/2) exp(-[3/(8a)-(a/2pi)sqrt12]) [+ term picked to fit]",
         math.sqrt(3) / 2, 3 / (8 * a) - a / (2 * math.pi) * math.sqrt(12)),
    ]
    for label, pref, S in steps:
        pred = mP * pref * math.exp(-S)
        rel = pred / me - 1
        sig = abs(math.log(pred / me)) / dS_target
        p(f"  {label}\n     -> m_e = {pred*c*c/eV/1e6:.6f} MeV  rel. error {rel:+.3e}  = {sig:,.0f} sigma")
    p("The 'action accuracy 99.999%' quoted in the documents divides the error by 51.5; that is not a")
    p("measure of agreement. The relevant comparison is the last line: the final formula misses by")
    p("4.8e-4 while the measurement (limited by G) is good to 1.1e-5, i.e. it is excluded at ~40 sigma.")
    p("Prior art: alpha*ln(m_P/m_e) = 3/8 (the leading term, with 3/8 attributed to GUTs) is L. Nottale's")
    p("scale-relativity 'mass-charge relation' (1990s; arXiv:hep-th/0307093, arXiv:2104.03924).")
    p("The repository script electron_mass_hierarchy_proof.py records the actual discovery route:")
    p("  '# Notice: 51.528 is remarkably close to (3/8) / alpha = 0.375 * 137.036 = 51.388 !'")


def look_elsewhere(p):
    p(banner("2. Look-elsewhere test: how special is a 4.8e-4 match in ln(m_P/m)?"))
    a = alpha[0]
    rat = sorted({Fraction(pp, qq) for qq in range(1, 17) for pp in range(1, 25) if pp / qq <= 1.5})
    lead = np.array([float(r) / a for r in rat])
    T1 = set()
    for nn in range(1, 25):
        for d in range(1, 9):
            x = math.sqrt(nn) / d
            if 0.3 < x <= 1:
                T1.add(round(-math.log(x), 12))
    for nn in range(2, 13):
        for d in range(1, 9):
            T1.add(round(math.log(nn) / d, 12))
    T1 = np.array(sorted(T1))
    T2 = np.array(sorted({(a / (k * math.pi)) * math.sqrt(n) * s
                          for k in (1, 2, 3, 4) for n in range(1, 25) for s in (1, -1)} | {0.0}))
    N = len(lead) * len(T1) * len(T2)
    p(f"Formula family  S = (p/q)/alpha + [-ln(sqrt(n)/d) or ln(n)/d] +- (alpha/(k pi)) sqrt(m):")
    p(f"  {len(lead)} leading rationals x {len(T1)} prefactor logs x {len(T2)} radiative terms = {N:,} formulas")
    p("  (the USRT formula is one member: p/q = 3/8, -ln(sqrt3/2), +(alpha/2pi) sqrt12)")
    base = (lead[:, None] + T1[None, :]).ravel()
    base.sort()

    def hits(target, win=4.8e-4):
        n = 0
        for t2 in T2:
            lo = np.searchsorted(base, target - t2 - win)
            hi = np.searchsorted(base, target - t2 + win)
            n += hi - lo
        return n

    mP, _ = planck_mass()
    MeV = 1.602176634e-13 / c**2
    named = {
        "electron": m_e_MeV[0], "muon": m_mu_MeV[0], "tau": m_tau_MeV[0], "pion+": 139.57039,
        "proton": 938.27208943, "W boson": 80369.2, "Z boson": 91188.0, "Higgs": 125200.0,
    }
    for name, mev in named.items():
        S = math.log(mP / (mev * MeV))
        p(f"  {name:9s} ln(m_P/m) = {S:8.4f}   formulas within 4.8e-4: {hits(S)}")
    rng = np.random.default_rng(1)
    rnd = [hits(t) for t in rng.uniform(38, 52, 400)]
    p(f"  400 RANDOM targets in [38, 52]: mean {np.mean(rnd):.1f} matching formulas each;"
      f" {100*np.mean(np.array(rnd) > 0):.0f}% of random numbers get at least one 'derivation'")
    p("=> A match of this quality is expected by chance once ~10^6 natural-looking formulas are")
    p("   available; it carries essentially no evidential weight.")


def koide(p):
    p(banner("3. Charged-lepton masses: Koide Q = 2/3 and the phase delta = 2/9"))
    me, dme = m_e_MeV
    mm, dmm = m_mu_MeV
    mt, dmt = m_tau_MeV

    def Q(e, m, t):
        return (e + m + t) / (math.sqrt(e) + math.sqrt(m) + math.sqrt(t)) ** 2

    q0 = Q(me, mm, mt)
    dq = abs(Q(me, mm, mt + dmt) - q0)
    p(f"Koide Q (PDG 2024) = {q0:.7f} +- {dq:.7f};  2/3 differs by {(q0-2/3)/dq:+.2f} sigma")
    p("  -> Q = 2/3 is a genuine, still unexplained empirical regularity (Koide 1981/1983). Real, but")
    p("     not new, and not derived by USRT: the parametrisation sqrt(m_k) = v0[1 + sqrt2 cos(d + 2pi k/3)]")
    p("     gives Q = 2/3 identically for ANY v0 and d, so it cannot 'prove' Q = 2/3.")

    # fit (v0, delta) to e and mu with Q = 2/3 built in
    def masses(v0, d):
        return [(v0 * (1 + math.sqrt(2) * math.cos(d + 2 * math.pi * k / 3))) ** 2 for k in (0, 1, 2)]

    # electron is k=1, muon k=2, tau k=0 (as in the USRT scripts)
    def mu_from(d):
        f = [1 + math.sqrt(2) * math.cos(d + 2 * math.pi * k / 3) for k in (0, 1, 2)]
        v0 = math.sqrt(me) / f[1]
        return (v0 * f[2]) ** 2, (v0 * f[0]) ** 2

    lo, hi = 0.20, 0.24
    for _ in range(200):
        mid = (lo + hi) / 2
        if (mu_from(mid)[0] - mm) * (mu_from(lo)[0] - mm) <= 0:
            hi = mid
        else:
            lo = mid
    d_fit = (lo + hi) / 2
    mmu_29, mtau_29 = mu_from(2 / 9)
    _, mtau_fit = mu_from(d_fit)
    p(f"delta fitted to (m_e, m_mu) with Q = 2/3 built in: {d_fit:.9f}   vs 2/9 = {2/9:.9f}")
    p(f"with delta = 2/9 exactly: m_mu = {mmu_29:.6f} MeV vs measured {mm:.7f} +- {dmm:.7f}"
      f"  -> {abs(mmu_29-mm)/dmm:,.0f} sigma off")
    p(f"tau from (m_e, m_mu) + Q = 2/3: {mtau_fit:.3f} MeV vs PDG 2024 {mt} +- {dmt}"
      f"  -> {(mtau_fit-mt)/dmt:+.2f} sigma (this is Koide's old successful prediction)")
    p("Prior art: delta ~ 2/9 was noticed by C. Brannen and G. Rosen (c. 2006); the USRT 'derivation'")
    p("(trace normalisation 2 / phase-space dimension 9) is a numerical label, not a calculation.")


def proton(p):
    p(banner("4. Proton/electron mass ratio  6 pi^5 + (3 pi/2) alpha"))
    a = alpha[0]
    pred = 6 * math.pi ** 5 + 1.5 * math.pi * a
    mu, dmu = mu_pe
    p(f"6 pi^5            = {6*math.pi**5:.9f}   (F. Lenz, Phys. Rev. 82, 554 (1951))")
    p(f"+ (3 pi/2) alpha  = {pred:.9f}")
    p(f"CODATA 2022       = {mu:.9f} +- {dmu}")
    p(f"difference        = {pred-mu:+.6e}  = {abs(pred-mu)/dmu:,.0f} sigma")
    p("=> The added term was chosen after the fact to close most of the 0.0346 gap; the remainder")
    p("   (1.8e-4) is ~5,500 times the measurement uncertainty, so the formula is excluded.")


def dark_ratio(p):
    p(banner("5. Dark-matter / baryon ratio  5 + 3/8"))
    oc, doc = omega_c_h2
    ob, dob = omega_b_h2
    R = oc / ob
    dR = R * math.hypot(doc / oc, dob / ob)
    p(f"Planck 2018: Omega_c h^2 / Omega_b h^2 = {R:.4f} +- {dR:.4f}")
    p(f"5 + 3/8 = 5.3750 -> pull {(5.375-R)/dR:+.2f} sigma")
    p(f"5 + sin^2(theta_W) at low energy (0.2312) = 5.2312 -> pull {(5.2312-R)/dR:+.2f} sigma")
    p("  (so the choice of the GUT-scale 3/8 rather than the measured 0.231 is what makes it 'work')")
    cands = sorted({Fraction(pp, qq) for qq in range(1, 13) for pp in range(1, 200) if abs(pp / qq - R) < dR})
    p(f"Simple fractions p/q (q <= 12) inside 1 sigma: {len(cands)}: " + ", ".join(str(x) for x in cands))
    p("The repository script records how the formula was found from a mis-entered target:")
    p("  omega_dm_measured = 0.2650 (Planck 2018 gives 0.120/0.6736^2 = 0.2645) -> 0.2650/0.0493 = 5.3753")
    p("  '# Notice: Exact Planck ratio: 5.375 = 43 / 8 = (40 + 3) / 8 = 5 + 3/8 !'")


def neutron_proton(p):
    p(banner("6. Neutron-proton mass difference"))
    d, dd = dm_np_MeV
    p(f"CODATA 2022 m_n - m_p = {d} +- {dd} MeV")
    p("USRT: (m_d - m_u) = 2.0500 MeV minus EM = 0.7567 MeV -> 1.2933 MeV. The two inputs are not")
    p("derived; 0.7567 is chosen so that the difference reproduces the measured value to 4 decimals.")
    p("Actual first-principles result (BMW collaboration, Borsanyi et al., Science 347, 1452 (2015),")
    p("lattice QCD+QED): QCD (m_d - m_u) part ~ +2.5 MeV, QED part ~ -1.0 MeV, total 1.51 +- 0.28 MeV.")


def main():
    out = []
    p = out.append
    section_electron(p)
    look_elsewhere(p)
    koide(p)
    proton(p)
    dark_ratio(p)
    neutron_proton(p)
    text = "\n".join(out)
    print(text)
    with open(os.path.join(os.path.dirname(__file__), "results", "a02_numerology.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
