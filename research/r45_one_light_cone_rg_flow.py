"""
r45 - The single light cone: does renormalisation wash out different species speeds?  (LAB_NOTEBOOK.md entry E48, tests Q1-Q4)

Question (queue item from E47, "the single light cone: the main obstacle for matter as quasi-particles"): in a medium that is not Lorentz invariant at the cell
scale, the fermion, the scalar (sound-like) mode and the gauge field generically have different speeds c_f, c_b, c_gamma.  Observation needs them equal to ~1e-15.
Chadha & Nielsen (1983) argued that interactions drive the speeds to a common value in the infrared (emergent Lorentz invariance); Collins et al. (2004) argued that
for realistic couplings the flow is far too slow.  Here the flow is COMPUTED, not estimated, in the simplest interacting model with two speeds:

    S = int dtau d^3x [ psibar (gamma_0 d_tau + c_f gamma_i d_i) psi + (1/2)(d_tau phi)^2 + (1/2) c_b^2 (grad phi)^2 + g phi psibar psi ]
    (one Dirac fermion of speed c_f, one real scalar of speed c_b, Yukawa coupling g; Euclidean, hbar = 1).

One-loop logarithmic parts of the self-energies (shell integration, ln(Lambda/mu) = l):
    fermion:  Sigma(p) = -g^2 int_q G(p+q) D(q)  ->  i g^2 l [ gamma_0 p_0 J_0(r) + c_f gamma.p J_s(r) ],   r = c_b/c_f
        J_0 = (1/4pi^3) int dw 1/(w^2 + r^2) [ 1/(w^2+1) - 2 w^2/(w^2+1)^2 ],  J_s = (1/4pi^3) int dw 1/(w^2 + r^2) [ 1/(w^2+1) - (2/3)/(w^2+1)^2 ]   (c_f = 1)
    scalar:   Pi(p) = g^2 int_q Tr[G(q) G(q+p)]  ->  l (a_0 p_0^2 + a_s p^2),   a_s = a_0 c_f^2 (the fermion loop is Lorentz invariant with its own speed c_f)
Speeds then flow as  d ln c_f / dl = g^2 (J_s - J_0),   d c_b^2 / dl = g^2 a_0 (c_f^2 - c_b^2)   (c_f = 1 units; g^2 means g^2 / c_f^3).

  Q1. Check the machinery: Lorentz-invariant limit r = 1 must give J_0 = J_s = 1/(16 pi^2) and a_0 = a_s = 1/(4 pi^2) (the known one-loop Yukawa anomalous dimensions,
      gamma_psi = g^2/32pi^2, gamma_phi = 2 g^2/16pi^2) and no flow.
  Q2. The flow function of r = c_b / c_f and its linearisation at r = 1: the rate at which a speed difference decays.
  Q3. Integrate the flow from the Planck scale to 1 TeV (ln = 37) for fixed and for running coupling: how small does the speed difference get?
  Q4. What coupling would be needed to reach 1e-15, and what the same calculation says for QED-like couplings.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r45_one_light_cone_rg_flow"
PREF = 1.0 / (4.0 * math.pi ** 3)               # 4 pi / (2 pi)^4
LN_PLANCK_TEV = math.log(1.221e19 / 1.0e3)      # ln(E_P / 1 TeV) = 37.0
BETA_YUKAWA = 5.0                               # one-loop d g / d ln mu = 5 g^3 / (16 pi^2) for a real scalar and one Dirac fermion (standard result, checked by Q1)
TARGET = 1.0e-15


def j_integrals(r):
    f0 = lambda w: 1.0 / (w * w + r * r) * (1.0 / (w * w + 1.0) - 2.0 * w * w / (w * w + 1.0) ** 2)
    fs = lambda w: 1.0 / (w * w + r * r) * (1.0 / (w * w + 1.0) - (2.0 / 3.0) / (w * w + 1.0) ** 2)
    j0 = 2.0 * quad(f0, 0.0, np.inf, epsabs=1e-13, epsrel=1e-12)[0] * PREF
    js = 2.0 * quad(fs, 0.0, np.inf, epsabs=1e-13, epsrel=1e-12)[0] * PREF
    return j0, js


def scalar_loop_coefficients():
    """a_0 and a_s from the second derivatives of the fermion loop integrand at |q| = 1 (c_f = 1)."""
    w, c, p0, pz = sp.symbols("w c p0 pz", real=True)
    k0, kz = w + p0, c + pz
    qperp2 = 1 - c ** 2
    f = (w * k0 + qperp2 + c * kz) / ((w ** 2 + 1) * (k0 ** 2 + qperp2 + kz ** 2))
    d2_t = sp.simplify(sp.diff(f, p0, 2).subs({p0: 0, pz: 0}) / 2)
    d2_z = sp.simplify(sp.diff(f, pz, 2).subs({p0: 0, pz: 0}) / 2)
    ft = sp.lambdify((w, c), d2_t, "numpy")
    fz = sp.lambdify((w, c), d2_z, "numpy")
    pref = -4.0 / (2.0 * math.pi) ** 4 * 2.0 * math.pi          # Tr = -4 N.N ... (see header), angular integral 2 pi int dc
    a0 = pref * 2.0 * quad(lambda cc: quad(lambda ww: ft(ww, cc), 0.0, np.inf, epsabs=1e-12, epsrel=1e-11)[0], -1.0, 1.0, epsabs=1e-12, epsrel=1e-11)[0]
    a_s = pref * 2.0 * quad(lambda cc: quad(lambda ww: fz(ww, cc), 0.0, np.inf, epsabs=1e-12, epsrel=1e-11)[0], -1.0, 1.0, epsabs=1e-12, epsrel=1e-11)[0]
    return a0, a_s


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("Q1. The machinery against the known Lorentz-invariant Yukawa results")
    # ------------------------------------------------------------------------------------------------------
    j0_1, js_1 = j_integrals(1.0)
    a0, a_s = scalar_loop_coefficients()
    one_16 = 1.0 / (16.0 * math.pi ** 2)
    one_4 = 1.0 / (4.0 * math.pi ** 2)
    p(f"    fermion, r = 1:  J_0 = {j0_1:.6e}, J_s = {js_1:.6e};  1/(16 pi^2) = {one_16:.6e}  (difference J_s - J_0 = {js_1 - j0_1:.1e}: no flow in the Lorentz-invariant case)")
    p(f"    scalar loop:     a_0 = {a0:.6e}, a_s = {a_s:.6e};  1/(4 pi^2) = {one_4:.6e}  (a_s = a_0 c_f^2 holds to {abs(a_s / a0 - 1):.1e})")
    gam_psi = j0_1 / 2.0       # Z_psi - 1 = 2 gamma_psi * l  ->  gamma_psi = g^2 J_0 / 2 = g^2 / (32 pi^2)
    gam_phi = a0 / 2.0         # gamma_phi = g^2 a_0 / 2 = 2 g^2 / (16 pi^2)
    p(f"    anomalous dimensions: gamma_psi = {gam_psi * 32 * math.pi ** 2:.4f} g^2/(32 pi^2) (known: 1), gamma_phi = {gam_phi * 16 * math.pi ** 2:.4f} g^2/(16 pi^2) (known: 2).")
    p("    With the vertex correction (-2 g^3/16pi^2) the beta function is (2 + 1 + 2) g^3/(16 pi^2) = 5 g^3/(16 pi^2), the standard value used below for the running coupling.")
    ok_q1 = (abs(js_1 - j0_1) < 1e-12 and abs(j0_1 / one_16 - 1) < 1e-8 and abs(a0 / one_4 - 1) < 1e-6 and abs(a_s / a0 - 1) < 1e-6)
    p(f"    Q1 {'PASSED' if ok_q1 else 'FAILED'}: all four numbers agree with the textbook values.")

    # ======================================================================================================
    p.section("Q2. The flow of the speed ratio r = c_b / c_f and its linearisation")
    # ------------------------------------------------------------------------------------------------------
    def kappa(r):
        j0, js = j_integrals(r)
        # d ln r / dl = g^2 [ a_0 (1 - r^2) / (2 r^2) - (J_s - J_0) ]   (c_f = 1 units)
        return -(a0 * (1.0 - r * r) / (2.0 * r * r) - (js - j0))

    p(f"    {'r = c_b/c_f':>12s} {'J_s - J_0':>12s} {'scalar term':>12s} {'d ln r / dl per g^2':>20s}")
    rs = [0.05, 0.1, 0.3, 0.5, 0.8, 0.95, 1.0, 1.05, 1.25, 2.0, 5.0, 20.0]
    for r in rs:
        j0, js = j_integrals(r)
        sc = a0 * (1.0 - r * r) / (2.0 * r * r)
        p(f"    {r:12.2f} {js - j0:12.4e} {sc:12.4e} {sc - (js - j0):20.4e}")
    h = 1e-4
    slope = (kappa(1.0 + h) - kappa(1.0 - h)) / (2 * h)       # d(-d ln r/dl / g^2)/dr at r = 1 = rate of decay per g^2
    p(f"    Linearisation at r = 1: d ln r / dl = -rate * (r - 1) with rate = {slope:.5e} g^2 = {slope * 16 * math.pi ** 2:.4f} g^2/(16 pi^2).")
    p(f"    => every species-speed difference decays as exp(-{slope * 16 * math.pi ** 2:.2f} (g^2/16pi^2) l): the Lorentz-invariant point is attractive in the infrared for both signs of the difference (see table).")
    attractive = all((kappa(r) < 0) == (r < 1) for r in rs if abs(r - 1) > 1e-9)
    p(f"    Sign check over r = {rs[0]}..{rs[-1]}: the flow always points toward r = 1: {attractive}.")

    # ======================================================================================================
    p.section("Q3. Planck scale to 1 TeV: fixed and running coupling")
    # ------------------------------------------------------------------------------------------------------
    p(f"ln(E_P / 1 TeV) = {LN_PLANCK_TEV:.1f}.  Initial speed ratio r_0 = 0.3 (an O(1) mismatch).  lambda = g^2/(16 pi^2) at the Planck scale; 'fixed' keeps g constant, 'running' uses")
    p("d g^2/dl = -10 g^4 / (16 pi^2) (the Yukawa coupling falls toward the infrared, asymptotic freedom is absent: the theory is infrared free).")

    # kappa(r) = (r - 1) h(r) with h smooth: tabulate h on a grid of ln r (excluding the immediate neighbourhood of r = 1, where quadrature noise would dominate)
    # and use the finite-difference slope there, so that the flow is exactly linear near the fixed point.
    lnr_grid = np.linspace(math.log(0.02), math.log(50.0), 600)
    lnr_grid = lnr_grid[np.abs(lnr_grid) > 2e-3]
    h_tab = np.array([kappa(math.exp(x)) / (math.exp(x) - 1.0) for x in lnr_grid])

    def kappa_fast(r):
        x = math.log(r)
        if abs(x) <= 2e-3:
            h_val = slope + (np.interp(2e-3, lnr_grid[lnr_grid > 0], h_tab[lnr_grid > 0]) - slope) * 0.0
            return (r - 1.0) * slope
        return (r - 1.0) * float(np.interp(x, lnr_grid, h_tab))

    def evolve_fast(lam0, r0, running, l_max=LN_PLANCK_TEV):
        def rhs(l, y):
            lnr, lam = y
            r = math.exp(lnr)
            return [-16.0 * math.pi ** 2 * lam * kappa_fast(r), (-2.0 * BETA_YUKAWA * lam * lam) if running else 0.0]
        return solve_ivp(rhs, (0.0, l_max), [math.log(r0), lam0], rtol=1e-10, atol=1e-30)

    p(f"    {'lambda':>8s} | {'|ln r| fixed g':>14s} {'suppression':>12s} | {'|ln r| running g':>16s} {'suppression':>12s} | {'lambda at 1 TeV (running)':>26s}")
    r0 = 0.3
    rows = []
    for lam0 in (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0):
        sf = evolve_fast(lam0, r0, False)
        sr = evolve_fast(lam0, r0, True)
        df, dr = abs(sf.y[0, -1]), abs(sr.y[0, -1])
        d0 = abs(math.log(r0))
        rows.append((lam0, df, dr, sr.y[1, -1]))
        fmt = lambda v: "< 1e-15" if v < 1e-15 else f"{v:.3e}"
        p(f"    {lam0:8.3f} | {fmt(df):>14s} {fmt(df / d0):>12s} | {fmt(dr):>16s} {fmt(dr / d0):>12s} | {sr.y[1, -1]:26.4f}")
    p("    (lambda >= 0.3 is not a weak coupling: g^2 = 16 pi^2 lambda; the one-loop flow is then a guide only.)")

    # ======================================================================================================
    p.section("Q4. What would reach 1e-15, and the QED-like case")
    # ------------------------------------------------------------------------------------------------------
    d0 = abs(math.log(r0))
    # fixed coupling: find lambda such that the final difference is TARGET
    lam_fixed = brentq(lambda lam: math.log(abs(evolve_fast(lam, r0, False).y[0, -1])) - math.log(TARGET), 0.05, 20.0)
    rate_pert = slope * 16 * math.pi ** 2
    p(f"    Fixed coupling: the speeds agree to {TARGET:.0e} at 1 TeV only if lambda = g^2/(16 pi^2) = {lam_fixed:.2f} (g^2 = {16 * math.pi ** 2 * lam_fixed:.0f}) all the way from the Planck scale.")
    p(f"    (linear estimate: lambda = ln(d_0 / {TARGET:.0e}) / ({rate_pert:.2f} x {LN_PLANCK_TEV:.1f}) = {math.log(d0 / TARGET) / (rate_pert * LN_PLANCK_TEV):.2f}.)")
    # running: exponent integral  int lambda dl = (1/(10)) ln(1 + 10 lambda_0 l)
    need = math.log(d0 / TARGET) / rate_pert
    lam0_run = (math.exp(2.0 * BETA_YUKAWA * need) - 1.0) / (2.0 * BETA_YUKAWA * LN_PLANCK_TEV)
    p(f"    Running coupling: the speed difference falls by exp(-{rate_pert:.2f} * (1/10) ln(1 + 10 lambda_0 l)); reaching {TARGET:.0e} needs int lambda dl = {need:.1f}, i.e. lambda_0 = {lam0_run:.1e}:")
    p(f"    impossible: for lambda_0 = 1 (strong already) the integral is {math.log(1 + 10 * 1.0 * LN_PLANCK_TEV) / 10:.2f}.")
    alpha_em = 1.0 / 137.036
    # photon side only: standard vacuum-polarisation coefficient e^2/(12 pi^2) per Dirac fermion (literature); the fermion side is of the same order
    rate_qed = alpha_em * 4.0 * math.pi / (12.0 * math.pi ** 2)
    supp_qed = math.exp(-2.0 * rate_qed * LN_PLANCK_TEV)
    p(f"    QED-like case (alpha = 1/137): photon-side rate e^2/(12 pi^2) = {rate_qed:.2e} per e-fold; counting the fermion side as equal, an O(1) mismatch at the Planck scale is reduced only by exp(-{2 * rate_qed * LN_PLANCK_TEV:.3f}) = {supp_qed:.3f}")
    p("    by 1 TeV: the standard-model-size flow does essentially nothing (Collins et al. 2004: induced violations 1e-3-1e-2 survive).")
    p("    Conclusion: in the infrared-free, weakly coupled regime the Lorentz-invariant point is attractive but the approach is a power of the energy with exponent ~ 1e-2 (g^2/16pi^2 ~ 1e-3-1e-2) or only a logarithm")
    p("    when the coupling itself runs to zero: 15 digits of agreement cannot come from the flow; they need either a symmetry that forbids the difference or a strongly coupled UV fixed point (Bednik, Pujolas & Sibiryakov 2013).")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("Q1: the integrals reproduce the known Yukawa anomalous dimensions and give no flow at r = 1",
         "PASSED" if ok_q1 else "FAILED"),
        ("Q2: the Lorentz-invariant point is attractive (c_b and c_f flow together)",
         f"YES for every r tried ({rs[0]}-{rs[-1]}); linear rate {rate_pert:.2f} g^2/(16 pi^2) per e-fold"),
        ("Q3: 37 e-folds from the Planck scale to 1 TeV remove an O(1) speed mismatch",
         f"NO at weak coupling: lambda = 0.01 leaves {rows[2][1] / d0:.2f} of it, lambda = 0.1 leaves {rows[4][1] / d0:.1e} and lambda = 0.3 less than 1e-15; with the coupling running to zero lambda = 1 leaves {rows[6][2] / d0:.1e}"),
        ("Q4: 1e-15 agreement from the flow alone",
         f"only with a constant strong coupling lambda = {lam_fixed:.2f} (g^2 = {16 * math.pi ** 2 * lam_fixed:.0f}); with running coupling lambda_0 = {lam0_run:.0e} is needed; QED-size couplings reduce the mismatch by {supp_qed:.2f}"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<80s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(16.6, 5.2))

    ax = axs[0]
    rr = np.geomspace(0.15, 20.0, 120)
    kk = np.array([kappa(r) for r in rr]) * 16 * math.pi ** 2
    ax.semilogx(rr, kk, color=S1, lw=2.2)
    ax.axhline(0, color=MUTED, lw=1.0)
    ax.axvline(1.0, color=S3, lw=1.3, ls="--")
    ax.text(1.08, -22.0, "Lorentz-invariant point r = 1", fontsize=9, color=S3)
    ax.text(0.17, 3.0, "r < 1: r grows", fontsize=9, color=INK_2)
    ax.text(2.2, 3.0, "r > 1: r falls", fontsize=9, color=INK_2)
    ax.set(ylim=(-40, 8), xlabel="speed ratio r = c_scalar / c_fermion", ylabel="−d ln r / dℓ  per  g²/(16π²)", title="The flow always points to a common speed")

    ax = axs[1]
    ll = np.linspace(0, LN_PLANCK_TEV, 200)
    for lam0, col in ((0.01, S1), (0.1, S2), (1.0, S3)):
        sol = evolve_fast(lam0, r0, False)
        ax.semilogy(ll, [abs(np.interp(l, sol.t, sol.y[0])) for l in ll], color=col, lw=2.0, label=f"fixed g, λ = {lam0}")
    sol = evolve_fast(1.0, r0, True)
    ax.semilogy(np.linspace(0, LN_PLANCK_TEV, 200), [abs(np.interp(l, sol.t, sol.y[0])) for l in np.linspace(0, LN_PLANCK_TEV, 200)],
                color=S3, lw=2.0, ls="--", label="running g, λ₀ = 1")
    ax.axhline(TARGET, color=INK_2, ls=":", lw=1.4)
    ax.text(24.0, TARGET * 4, "needed: 10⁻¹⁵", fontsize=9, color=INK_2)
    ax.set(ylim=(1e-18, 3), xlabel="e-folds of energy below the Planck scale, ℓ", ylabel="speed difference |ln(c_scalar/c_fermion)|", title="From the Planck scale to 1 TeV")
    ax.legend(loc="center right", fontsize=9, bbox_to_anchor=(1.0, 0.45))

    ax = axs[2]
    lams = np.geomspace(1e-3, 3.0, 40)
    fin_f = [abs(evolve_fast(l_, r0, False).y[0, -1]) / d0 for l_ in lams]
    fin_r = [abs(evolve_fast(l_, r0, True).y[0, -1]) / d0 for l_ in lams]
    ax.loglog(lams, fin_f, color=S1, lw=2.0, label="fixed coupling")
    ax.loglog(lams, fin_r, color=S2, lw=2.0, label="running coupling (infrared free)")
    ax.axhline(TARGET / d0, color=INK_2, ls=":", lw=1.4)
    ax.text(1.5e-3, TARGET / d0 * 3, "10⁻¹⁵", fontsize=9, color=INK_2)
    ax.axvspan(1e-3, 1e-2, color=S3, alpha=0.18, lw=0)
    ax.text(1.2e-3, 3e-9, "standard-model-\nsize couplings", fontsize=9, color=S3)
    ax.axvspan(0.3, 3.0, color=MUTED, alpha=0.15, lw=0)
    ax.text(0.45, 1e-10, "not weak", fontsize=9, color=INK_2)
    ax.set(ylim=(1e-18, 3), xlabel="coupling λ = g²/(16π²) at the Planck scale", ylabel="fraction of the mismatch left at 1 TeV", title="A weak coupling does not wash the difference out")
    ax.legend(loc="lower left", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "rg_flow")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
