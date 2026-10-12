"""
r52 - Does a gauge field make the fermion and photon light cones merge?  One-loop speed flow of Lorentz-violating QED  (LAB_NOTEBOOK.md entry E49, tests L1-L4)

Question (open item from E48: 'single light cone, second pass'): r44/r47 showed that a Yukawa coupling pulls the speeds of two scalar/fermion sectors together only very slowly.  The medium has
photons (the gauge field of the 'electromagnetic' sector) and fermions (Weyl/Dirac quasi-particles of r41).  Their speeds c_gamma and v need not agree in a medium.  Does one-loop gauge dynamics
drive them together fast enough to hide the mismatch at the Lorentz-invariance bounds?

Model (hbar = 1, Euclidean): Dirac fermion of speed v coupled with charge e to a photon of speed c_g in a medium with dielectric constant eps and permeability mu, c_g^2 = 1 / (eps mu).
Coulomb gauge: <A0 A0> = 1 / (eps q^2) (instantaneous), <A_i A_j> = (delta_ij - qhat_i qhat_j) / (eps (q0^2 + c_g^2 q^2)).  x = c_g / v, alpha_v = e^2 / (4 pi eps v).

  L1. The fermion self-energy at one loop, expanded to first order in the external momentum and reduced to ONE integral over the 4D angle chi (q0 = Q cos chi, |q| = Q sin chi), checked against three
      things that are known: (a) Lorentz invariance (x = 1) gives zero speed flow (this also fixes the sign of the transverse-photon term), (b) the instantaneous-Coulomb limit x -> infinity
      gives the Weyl-semimetal result d ln v / dL = 2 alpha / (3 pi) (Hosur et al.; Isobe-Nagaosa), (c) the integral is evaluated numerically AND found to equal a closed form.
  L2. Photon side: the fermion loop renormalises eps and 1/mu with delta(1/mu) = v^2 delta eps (Lorentz invariance of the fermion sector) at the standard Uehling rate; validated by the known
      QED beta function (x = 1: d alpha / dL = -2 alpha^2 / (3 pi) per Dirac fermion).
  L3. The coupled flow of (x, alpha_v) in L = ln(Lambda / mu) and its fixed point x = 1: the approach rate, and the exact scaling delta ~ alpha^(1 + 2/n) (n = number of Dirac fermions).
  L4. What that buys: the remaining mismatch after N = ln(E_Planck / 1 eV) = 64.6 e-folds of running, and the number of e-folds that would be needed for the mismatch to fall below 1e-15 (conservative
      round number for the best bounds on photon-versus-electron speed differences; typed from memory, Kostelecky-Russell data tables; tighter bounds make the conclusion stronger).

Convention: L = ln(Lambda_UV / mu) grows towards the infrared; a positive d ln v / dL means v is larger in the infrared.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad, solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, save_fig, style  # noqa: E402

NAME = "r52_gauge_speed_flow"
HBAR = 1.054571817e-34
EV = 1.602176634e-19


def g_numeric(x, sigma=+1):
    """d ln v / dL in units of alpha_v, from the 4D-angle integral (v = 1).  sigma = relative sign of the transverse-photon term."""
    P = lambda ch: math.cos(ch) ** 2 + x * x * math.sin(ch) ** 2
    f0 = lambda ch: (math.sin(ch) ** 2 - math.cos(ch) ** 2) * (1.0 - 2.0 * sigma * math.sin(ch) ** 2 / P(ch))
    f1 = lambda ch: (-1.0 + 2.0 / 3.0 * math.sin(ch) ** 2) - 2.0 * sigma / 3.0 * math.sin(ch) ** 2 * (1.0 - 2.0 * math.sin(ch) ** 2) / P(ch)
    i0 = quad(f0, 0, math.pi, epsabs=1e-13, epsrel=1e-13, limit=200)[0]
    i1 = quad(f1, 0, math.pi, epsabs=1e-13, epsrel=1e-13, limit=200)[0]
    return -(i1 - i0) / math.pi ** 2


def g_explicit(x, sigma=+1, n_chi=64, n_th=16, h=1e-5):
    """Independent check of the reduced integrals: the same self-energy integrand with explicit 4 x 4 Euclidean gamma matrices, differentiated numerically in k0 and k_z at k = 0 and integrated
    over the 4D angle with Gauss-Legendre rules (v = 1, |q| fixed to Q = 1).  Returns d ln v / dL in units of alpha_v, normalised like g_numeric (overall sign fixed there by the Coulomb limit)."""
    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)
    i2, z2 = np.eye(2, dtype=complex), np.zeros((2, 2), dtype=complex)
    g0 = np.block([[z2, i2], [i2, z2]])
    gs = [np.block([[z2, -1j * s], [1j * s, z2]]) for s in (s1, s2, s3)]
    for a in range(4):
        for b in range(4):
            ga = g0 if a == 0 else gs[a - 1]
            gb = g0 if b == 0 else gs[b - 1]
            assert np.allclose(ga @ gb + gb @ ga, 2 * (a == b) * np.eye(4))

    def sigma_matrix(k0, kz, q0, qv):
        p0 = k0 + q0
        pv = qv + np.array([0.0, 0.0, kz])
        gt = (g0 * p0 + sum(gs[j] * pv[j] for j in range(3))) / (p0 ** 2 + pv @ pv)
        q2 = qv @ qv
        qh = qv / math.sqrt(q2)
        coul = g0 @ gt @ g0 / q2
        trans = np.zeros((4, 4), dtype=complex)
        for j in range(3):
            for i in range(3):
                trans += gs[j] @ gt @ gs[i] * ((j == i) - qh[j] * qh[i])
        return coul + sigma * trans / (q0 ** 2 + x * x * q2)

    xc, wc = np.polynomial.legendre.leggauss(n_chi)
    chi, w_chi = 0.5 * math.pi * (xc + 1.0), 0.5 * math.pi * wc
    ct, w_ct = np.polynomial.legendre.leggauss(n_th)
    tot0 = tot1 = 0.0
    for ch, wch in zip(chi, w_chi):
        q0, qm = math.cos(ch), math.sin(ch)
        for c_, wt in zip(ct, w_ct):
            qv = qm * np.array([math.sqrt(1 - c_ * c_), 0.0, c_])
            d0 = (sigma_matrix(h, 0.0, q0, qv) - sigma_matrix(-h, 0.0, q0, qv)) / (2 * h)
            dz = (sigma_matrix(0.0, h, q0, qv) - sigma_matrix(0.0, -h, q0, qv)) / (2 * h)
            tot0 += wch * wt * math.sin(ch) ** 2 * (np.trace(g0 @ d0) / 4).real
            tot1 += wch * wt * math.sin(ch) ** 2 * (np.trace(gs[2] @ dz) / 4).real
    # angular integral over the sphere of q: 2 pi dcos(theta) (azimuth trivial); I1 - I0 = (tot1 - tot0) * 2 pi / (4 pi)
    return -(tot1 - tot0) * 0.5 / math.pi ** 2


def g_closed(x):
    return 2.0 / (3.0 * math.pi) * (1.0 - 4.0 / (x * (1.0 + x) ** 2))


def photon_rate(x, n):
    """d ln c_g / dL in units of alpha_v for n Dirac fermions."""
    return -n / (3.0 * math.pi) * (1.0 - 1.0 / x ** 2)


def flow(n):
    def rhs(L, y):
        lnx, lna = y
        x, a = math.exp(lnx), math.exp(lna)
        dlnv = a * g_closed(x)
        dlnc = a * photon_rate(x, n)
        dlneps = n * 2.0 * a / (3.0 * math.pi)
        return [dlnc - dlnv, -dlneps - dlnv]
    return rhs


def evolve(x0, a0, n, big_l):
    sol = solve_ivp(flow(n), (0.0, big_l), [math.log(x0), math.log(a0)], rtol=1e-11, atol=1e-14, dense_output=True)
    return sol


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    pi = math.pi

    # ======================================================================================================
    p.section("L1. Fermion self-energy in Coulomb gauge: three checks")
    # ------------------------------------------------------------------------------------------------------
    p("Self-energy (v = 1): Sigma(k) = s e^2 Int d^4q/(2 pi)^4 [ gamma0 G(k+q) gamma0 / (eps q^2) + sigma gamma_j G(k+q) gamma_i (delta_ji - qhat_j qhat_i) / (eps (q0^2 + c_g^2 q^2)) ],")
    p("G(p) = -i (gamma0 p0 + gamma.p) / (p0^2 + p^2).  Dirac algebra: gamma0 (gamma0 p0 - ... ) gives gamma0 p0 - gamma.p for the Coulomb term and -2 gamma0 p0 - 2 (qhat.gamma)(qhat.p) for the transverse term;")
    p("after expanding to first order in k and averaging over the direction of q, the 4D angle integrals are (sin^2 chi is the measure):")
    p("    I0 = Int_0^pi [ (sin^2 - cos^2) (1 - 2 sigma sin^2 / P) ] dchi,        P = cos^2 chi + x^2 sin^2 chi          (coefficient of gamma0 k0)")
    p("    I1 = Int_0^pi [ (-1 + (2/3) sin^2) - (2 sigma / 3) sin^2 (1 - 2 sin^2) / P ] dchi                              (coefficient of gamma.k)")
    p("    d ln v / dL = - alpha_v (I1 - I0) / pi^2   (the overall sign s = -1 is fixed by the Coulomb limit below; the relative sign sigma by Lorentz invariance).")
    p("")
    p(f"    (a) Lorentz invariance, x = 1:  sigma = +1: d ln v / dL = {g_numeric(1.0, +1):+.3e} alpha_v   (zero);   sigma = -1: {g_numeric(1.0, -1):+.4f} alpha_v   (the wrong sign does not cancel: the check discriminates).")
    p(f"    (b) Coulomb limit, x -> infinity: x = 1e4: {g_numeric(1e4):.8f} alpha_v;   2/(3 pi) = {2 / (3 * pi):.8f}.  Relative difference {abs(g_numeric(1e4) / (2 / (3 * pi)) - 1):.1e} (the transverse photon decouples: the closed form below deviates from 2/(3 pi) as 4/x^3).")
    p("    (c) Independent check of the algebra: the same integrand with explicit 4 x 4 gamma matrices (Euclidean, Hermitian), differentiated numerically and integrated over the 4D angle with Gauss rules:")
    p(f"        {'x':>6s} {'explicit matrices':>20s} {'reduced integrals (a-c)':>25s} {'difference':>12s}")
    worst_ex = 0.0
    for x_ in (1.0, 1.5, 2.0, 5.0, 20.0):
        ge, gn_ = g_explicit(x_), g_numeric(x_)
        worst_ex = max(worst_ex, abs(ge - gn_))
        p(f"        {x_:6.2f} {ge:20.12f} {gn_:25.12f} {ge - gn_:12.1e}")
    p(f"        largest difference {worst_ex:.1e}: the hand reduction of the Dirac algebra is confirmed by explicit matrices (the sign of the overall factor is the one fixed by the Coulomb limit).")
    xs = (1.001, 1.01, 1.1, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0)
    p(f"    (d) Closed form  g(x) = 2/(3 pi) [1 - 4 / (x (1 + x)^2)]  (found by fitting the numerical values at x = 1.5, 2, 5, 10 and then tested at every other x):")
    p(f"        {'x':>8s} {'numerical':>16s} {'closed form':>16s} {'difference':>12s}")
    worst = 0.0
    for x in xs:
        gn, gc = g_numeric(x), g_closed(x)
        worst = max(worst, abs(gn - gc))
        p(f"        {x:8.3f} {gn:16.12f} {gc:16.12f} {gn - gc:12.1e}")
    p(f"        largest difference {worst:.1e} (the quadrature tolerance is 1e-13): the closed form agrees with the integral to machine precision; the numbers 1.5, 2, 5, 10 were used to find it, the other five points test it.")

    # ======================================================================================================
    p.section("L2. Photon side: vacuum polarisation of a fermion of speed v")
    # ------------------------------------------------------------------------------------------------------
    p("Dirac fermion loop: delta eps / eps = n (2 alpha_v / 3 pi) dL (Uehling, with the fermion speed v in alpha_v = e^2 / (4 pi eps v)); the magnetic part follows from the Lorentz invariance of the fermion sector")
    p("(speed v): delta(1/mu) = v^2 delta eps.  Hence  d ln c_g^2 / dL = [delta(1/mu)/(1/mu) - delta eps / eps] / dL = (n 2 alpha_v / 3 pi) (v^2 / c_g^2 - 1):")
    p("    d ln c_g / dL = - n (alpha_v / 3 pi) (1 - 1/x^2).")
    p("Inputs (typed in, not computed here): the Uehling coefficient 2 alpha / (3 pi) per Dirac fermion and the structure delta(1/mu) = v^2 delta eps.")
    p("Check: x = 1 gives no flow of c_g (Lorentz invariance); x >> 1 gives the rate alpha_v / (3 pi) quoted in E48; the charge: d alpha_v / dL = alpha_v (- d ln eps / dL - d ln v / dL) = -(2 n alpha_v^2 / 3 pi) at x = 1,")
    p("i.e. the standard QED beta function dalpha/dln(mu) = + 2 n alpha^2 / (3 pi) per Dirac fermion (n = 1 is the textbook value 2 alpha^2 / 3 pi).")
    a_test = 1.0 / 137.036
    p(f"    numbers for alpha = 1/137: d ln c_g / dL = {-(a_test / (3 * pi)):.3e} (x -> inf), d ln v / dL = {a_test * 2 / (3 * pi):.3e}, d ln eps / dL = {a_test * 2 / (3 * pi):.3e} per e-fold.")

    # ======================================================================================================
    p.section("L3. The coupled flow and the approach to one light cone")
    # ------------------------------------------------------------------------------------------------------
    p("    d ln x / dL = -(alpha_v / 3 pi) [ n (1 - 1/x^2) + 2 (1 - 4 / (x (1 + x)^2)) ],    d ln alpha_v / dL = -(2 n / 3 pi) alpha_v - alpha_v g(x).")
    p("    Near x = 1 (delta = x - 1):  d delta / dL = -(2 (n + 2) alpha_v / 3 pi) delta   and   d alpha_v / dL = -(2 n / 3 pi) alpha_v^2,  so  delta ~ alpha_v^(1 + 2/n) ~ (1 + 2 n alpha_0 L / 3 pi)^(-(1 + 2/n)):")
    p("    the approach to one light cone is a POWER LAW IN L = ln(scale), not exponential in L, because the coupling itself runs to zero (marginally irrelevant) at the same time.")
    p(f"    {'n (Dirac fermions)':>20s} {'rate (2(n+2)/(3 pi)) alpha / e-fold':>38s} {'exponent 1 + 2/n':>18s}")
    for n in (0.5, 1, 2, 8):
        p(f"    {n:20.1f} {2 * (n + 2) / (3 * pi):38.4f} {1 + 2 / n:18.2f}")
    p("    (n = 1/2 is one Weyl node; n = 8 is the sum of Q^2 N_colour over all charged Standard-Model fermions above their masses, if they all had the same speed v.)")
    p("")
    # numerical check of the exponent
    sol = evolve(1.05, 0.5, 1, 400.0)
    ln_d = np.log(np.exp(sol.y[0]) - 1.0)
    ln_a = sol.y[1]
    sel = (sol.t > 200)
    slope = float(np.polyfit(ln_a[sel], ln_d[sel], 1)[0])
    p(f"    Numerical check (n = 1, x0 = 1.05, alpha0 = 0.5, integrated over 400 e-folds): d ln delta / d ln alpha = {slope:.4f}   (predicted 1 + 2/n = 3).")

    # ======================================================================================================
    p.section("L4. What the running buys")
    # ------------------------------------------------------------------------------------------------------
    e_planck = math.sqrt(HBAR * c ** 5 / G0)
    n_e = math.log(e_planck / EV)
    p(f"    E_Planck = {e_planck / EV / 1e9:.3e} GeV;  running from the Planck scale to 1 eV: N = ln(E_P / eV) = {n_e:.1f} e-folds (to 1 GeV: {math.log(e_planck / EV / 1e9):.1f}).")
    bound = 1e-15
    p(f"    Remaining light-cone mismatch delta = c_g / v - 1 after N = {n_e:.1f} e-folds, and the number of e-folds needed to reach delta = {bound:.0e}:")
    p(f"    {'n':>4s} {'alpha_0':>9s} {'x_0 - 1':>8s} {'delta after 64.6':>17s} {'reduction':>10s} {'N for 1e-15':>13s} {'/ 64.6':>10s}")
    rows = []
    for n in (1, 8):
        for a0 in (1.0 / 137.036, 0.1, 1.0):
            for x0 in (2.0, 1.1):
                sol = evolve(x0, a0, n, n_e)
                x_end = math.exp(sol.sol(n_e)[0])
                d_end = x_end - 1.0
                # e-folds needed for the bound, from the near-fixed-point law (x0 - 1 -> small first): use the closed scaling with the exact start
                # find N by integrating until delta < bound or up to 1e12 using the scaling law from the point where delta < 1e-2
                sol2 = evolve(x0, a0, n, 3000.0 / a0)
                xs2 = np.exp(sol2.y[0]) - 1.0
                idx = np.argmax(xs2 < 1e-2)
                if xs2[idx] < 1e-2:
                    l1, d1, a1 = sol2.t[idx], xs2[idx], math.exp(sol2.y[1][idx])
                    # delta ~ (1 + k (L - l1))^(-(1 + 2/n)) with k = 2 n a1 / (3 pi): solve for bound
                    k = 2.0 * n * a1 / (3.0 * pi)
                    ex = 1.0 + 2.0 / n
                    n_need = l1 + ((d1 / bound) ** (1.0 / ex) - 1.0) / k
                else:
                    n_need = float("nan")
                rows.append((n, a0, x0, d_end, n_need))
                p(f"    {n:4d} {a0:9.4f} {x0 - 1:8.2f} {d_end:17.3e} {(x0 - 1) / d_end:10.1f} {n_need:13.3e} {n_need / n_e:10.1e}")
    p("    (the 'N for 1e-15' column uses the exact flow until the mismatch is below 1 % and the near-fixed-point scaling law afterwards.)")
    best = min(r[4] for r in rows if not math.isnan(r[4]))
    p(f"    Smallest number of e-folds needed in this table: {best:.2e}, i.e. {best / n_e:.1e} times the {n_e:.1f} available between the Planck scale and 1 eV.")
    p("    alpha_0 = 1 is already at the edge of perturbation theory, so the row is optimistic: it shows what the one-loop formula can give, not a controlled result.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    d_qed = [r for r in rows if r[0] == 1 and abs(r[1] - 1 / 137.036) < 1e-9 and r[2] == 2.0][0]
    d_one = [r for r in rows if r[0] == 1 and r[1] == 1.0 and r[2] == 2.0][0]
    d_sm = [r for r in rows if r[0] == 8 and abs(r[1] - 1 / 137.036) < 1e-9 and r[2] == 2.0][0]
    verdict = [
        ("L1: the self-energy integral passes Lorentz invariance, the Coulomb limit and has an exact closed form", f"YES: g(1) = {g_numeric(1.0):.0e}, g(inf) -> 2/(3 pi) to {abs(g_numeric(1e4) / (2 / (3 * pi)) - 1):.0e}, closed form to {worst:.0e}, explicit-matrix check to {worst_ex:.0e}"),
        ("L2: the photon side is consistent with the QED beta function", "YES, as a consistency check: d alpha / dL = -2 alpha^2 / (3 pi) at x = 1 (n = 1) follows from the same formulae (the photon-side rate itself is the textbook Uehling input, not derived here)"),
        ("L3: the light cones are attracted to a common value (x = 1 is an infrared fixed point)", f"YES, with a rate 2(n+2) alpha / (3 pi) = {6 / (3 * pi):.3f} alpha per e-fold at n = 1; delta ~ alpha^(1 + 2/n), a power law in the number of e-folds"),
        ("L4: the mismatch is hidden at the 1e-15 level by the running at QED strength", f"NO: from x0 = 2 and alpha = 1/137 the mismatch after {n_e:.0f} e-folds is {d_qed[3]:.2f} (a reduction by {(2 - 1) / d_qed[3]:.2f}); n = 8: {d_sm[3]:.2f}; reaching 1e-15 would take {d_qed[4]:.1e} e-folds"),
        ("L4b: and at alpha = 1 (the most favourable value for which one loop is not absurd)", f"NO: {d_one[3]:.1e} after {n_e:.0f} e-folds (reduction {(2 - 1) / d_one[3]:.0f}); 1e-15 would take {d_one[4]:.1e} e-folds"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<100s} -> {status}")
    p("   Reading: the gauge field attracts the two light cones, but only logarithmically and with an ever weaker coupling.  Equal speeds to 1e-15 cannot be produced from an unequal start by running over 65 e-folds")
    p("   at electromagnetic strength.  The single light cone must be an INPUT (a symmetry of the medium or a fine-tuned initial condition), not an output of renormalisation.")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.0, 5.3))
    ax = axs[0]
    xx = np.geomspace(1.0001, 1000.0, 400)
    ax.semilogx(xx, [g_closed(x) * 3 * pi / 2 for x in xx], color=S2, lw=2.2, label="fermion speed:  d ln v / dL")
    ax.semilogx(xx, [-photon_rate(x, 1) * 3 * pi / 2 for x in xx], color=S1, lw=2.2, label="photon speed:  - d ln c_γ / dL")
    ax.semilogx(xx, [(g_closed(x) + photon_rate(x, 1) * -1.0) * 3 * pi / 2 for x in xx], color=S3, lw=2.2, label="rate at which c_γ / v closes:  - d ln x / dL")
    ax.set(xlabel="light-cone ratio  x = c_γ / v", ylabel="flow rate ÷ (2 α_v / 3π)  per e-fold",
           title="One-loop speed flow of Lorentz-violating QED (one Dirac fermion)", ylim=(-0.05, 2.05))
    ax.legend(loc="upper left", fontsize=9)

    ax = axs[1]
    for a0, col in ((1.0 / 137.036, S1), (0.1, S2), (1.0, S3)):
        sol = evolve(2.0, a0, 1, 200.0)
        ts = np.linspace(0, 200, 400)
        xs_ = np.exp(sol.sol(ts)[0]) - 1.0
        ax.loglog(ts[1:], xs_[1:], color=col, lw=2.2, label=f"α₀ = {a0:.3g}")
    ax.axvline(n_e, color=MUTED, ls=":", lw=1.3)
    ax.text(n_e * 1.08, 3e-8, "65 e-folds\n(Planck → eV)", fontsize=9, color=INK_2)
    ax.axhline(1e-15, color=MUTED, ls="--", lw=1.0)
    ax.text(1.2, 1.6e-15, "bound ~ 1e-15 (typed from memory)", fontsize=9, color=INK_2)
    ax.set(xlabel="e-folds of running, L = ln(Λ/μ)", ylabel="light-cone mismatch  c_γ / v − 1", ylim=(1e-17, 3), xlim=(1, 200),
           title="Mismatch left after running (start: c_γ = 2v)")
    ax.legend(loc="center left", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "speed_flow")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
