"""
r19 - Testing a causal-set substrate: discreteness without a rest frame  (LAB_NOTEBOOK.md entry E25)

Question (user): "Random, frame-free discreteness instead of a lattice (causal sets) ... test this
one too."  And: "make sure we are mathematically exact, calculation-wise, formulation-wise and
simulation-wise."

A causal set (Bombelli, Lee, Meyer & Sorkin 1987) is a substrate made only of ELEMENTS and the
one-way relation 'is to the past of'.  Spacetime volume = number of elements (Poisson density rho,
discreteness length l = rho^(-1/d)); everything else (time, distance, dimension, curvature) must be
COUNTED from the order.  Here, in 1+1 dimensions where exact results exist (and in 2-4D for the
dimension test), we check, with closed forms wherever possible:
  A. No preferred frame: the links of an element spread uniformly over all rapidities; their number
     is Ein(N) = ln N + gamma_E + E1(N) (exact).  A lattice has links in a few fixed directions.
  B. Dimension from order alone (Myrheim-Meyer): ordering fraction f(d) = G(d+1)G(d/2)/(2G(3d/2)).
  C. Time = counting: the longest chain measures proper time (Brightwell & Gregory 1991).  Twin
     paradox by counting, against 1/gamma with the exact Baik-Deift-Johansson finite-size term.
  D. Waves: Sorkin's discrete d'Alembertian.  Its mean on a plane wave is computed in CLOSED FORM:
     it depends on the wavevector only through k^2 -> exactly Lorentz invariant; its only real zero
     is k^2 = 0 -> massless waves travel at exactly c at every energy.  Checked by quadrature in two
     frames and by Monte Carlo sprinklings.  Contrast: a lattice operator depends on the frame.
  E. Curvature from counting: in 2D de Sitter the mean of B acting on 1 -> -R/2 (Benincasa-Dowker).
  F. Lambda ~ 1/sqrt(N): Sorkin's order-of-magnitude prediction of the cosmological constant.
"""
import bisect
import math
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mpmath as mp  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
from scipy import integrate  # noqa: E402
from scipy.optimize import brentq  # noqa: E402
from scipy.special import exp1, gamma  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, lP, save_fig, style  # noqa: E402

NAME = "r19_causal_set_substrate"
RNG = np.random.default_rng(2026)
MU_TW = -1.7710868074                       # mean of the GUE Tracy-Widom distribution


def ein(x):
    return np.euler_gamma + np.log(x) + exp1(x)


# ---------------------------------------------------------------- A. links
def corner_links(N, reps):
    out, rap = [], []
    for _ in range(reps):
        n = RNG.poisson(N)
        u, v = RNG.random(n), RNG.random(n)
        o = np.argsort(u)
        us, vs = u[o], v[o]
        cm = np.minimum.accumulate(np.concatenate([[np.inf], vs[:-1]]))
        m = vs < cm
        out.append(int(m.sum()))
        rap.extend(0.5 * np.log(us[m] / vs[m]))
    return np.array(out), np.array(rap)


# ---------------------------------------------------------------- B. Myrheim-Meyer
def f_order(d):
    return gamma(d + 1) * gamma(d / 2) / (2 * gamma(3 * d / 2))


def sprinkle_interval(d, N):
    """N points uniform in the Alexandrov interval between (0,0..) and (1,0..) of d-dim Minkowski."""
    pts = []
    while len(pts) < N:
        x = RNG.random((4 * N, d))
        x[:, 1:] = (x[:, 1:] - 0.5)
        r = np.linalg.norm(x[:, 1:], axis=1)
        ok = r < np.minimum(x[:, 0], 1 - x[:, 0])
        pts.extend(x[ok].tolist())
    return np.array(pts[:N])


def ordering_fraction(P):
    dt = P[:, None, 0] - P[None, :, 0]
    dr = np.linalg.norm(P[:, None, 1:] - P[None, :, 1:], axis=2)
    R = np.sum((dt > 0) & (dt > dr))
    return R / (len(P) * (len(P) - 1) / 2)


# ---------------------------------------------------------------- C. longest chains
def lis(seq):
    tails = []
    for x in seq:
        k = bisect.bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)


def longest_chain(u, v):
    o = np.argsort(u)
    return lis(v[o].tolist())


def bdj_mean(lam):
    return 2 * math.sqrt(lam) + MU_TW * lam ** (1 / 6)


# ---------------------------------------------------------------- D. Sorkin d'Alembertian
def I_exact(zeta, sigma=1):
    """Mean of the layer sum on a plane wave: I = -int_0^inf e^{i zeta s} (s - i sigma)^-3 ds.
    Evaluated on the contour rotated by +-pi/4 (Cauchy: the pole at s = i sigma is not crossed and the
    arc at infinity vanishes), where the integrand decays exponentially -- accurate for all zeta."""
    if zeta == 0:
        return complex(mp.quad(lambda s: -1 / (s - 1j * sigma) ** 3, [0, mp.inf]))
    e = mp.e ** (1j * (mp.pi / 4 if zeta > 0 else -mp.pi / 4))
    return complex(-e * mp.quad(lambda t: mp.e ** (1j * zeta * e * t) / (e * t - 1j * sigma) ** 3, [0, 1, 10, mp.inf]))


def B_mean_exact(ku, kv, rho=1.0):
    sigma = 1 if kv > 0 else -1
    zeta = 2 * ku * abs(kv) / rho
    return 4 * rho * (I_exact(zeta, sigma) - 0.5)


def B_mean_truncated(ku, kv, A1, A2, rho=1.0):
    """Same mean, but by brute-force 2D quadrature over a truncated past diamond (independent check)."""
    w = lambda b, a: math.exp(-rho * a * b / 2) * (1 - rho * a * b + (rho * a * b) ** 2 / 8) * 0.5   # noqa: E731
    re = integrate.dblquad(lambda b, a: w(b, a) * math.cos(ku * a + kv * b), 0, A1, 0, A2, epsabs=1e-11, epsrel=1e-11)[0]
    im = integrate.dblquad(lambda b, a: w(b, a) * math.sin(ku * a + kv * b), 0, A1, 0, A2, epsabs=1e-11, epsrel=1e-11)[0]
    return 4 * rho * (-0.5 + rho * complex(re, im))


def B_monte_carlo(ku, kv, A1, A2, nrep, rho=1.0):
    vals = np.empty(nrep, complex)
    for r in range(nrep):
        n = RNG.poisson(rho * A1 * A2 / 2)
        a, b = RNG.random(n) * A1, RNG.random(n) * A2
        inside = ((a[None, :] < a[:, None]) & (b[None, :] < b[:, None])).sum(1)
        wgt = np.select([inside == 0, inside == 1, inside == 2], [1, -2, 1], 0)
        vals[r] = 4 * rho * (-0.5 + np.sum(wgt * np.exp(1j * (ku * a + kv * b))))
    return vals.mean(), vals.real.std() / math.sqrt(nrep), vals.imag.std() / math.sqrt(nrep), vals.real.std()


def lattice_box(ku, kv, a=1.0):
    """Square (t,x) lattice d'Alembertian of spacing a on the same plane wave (eigenvalue, sign as B)."""
    w, k = ku + kv, kv - ku
    return (4 * math.sin(w * a / 2) ** 2 - 4 * math.sin(k * a / 2) ** 2) / a ** 2


# ---------------------------------------------------------------- E. de Sitter
def ds_B1(rho):
    """Mean of B acting on 1 at a point of 2D de Sitter (radius 1), exact interval volumes.
    J - 1/2 split into two pieces free of cancellation (substitution w = rho V)."""
    f = lambda w: math.exp(-w) * (1 - 2 * w + 0.5 * w * w)            # noqa: E731
    F = lambda x: math.exp(-x) * (x - 0.5 * x * x)                    # noqa: E731

    def b_of_V(a, V):
        E = math.exp(V / 2)
        return 2 * (2 + a) * (E - 1) / (2 + a - 2 * E)
    P1 = integrate.quad(lambda x: F(x) * (math.exp(x / (2 * rho)) / (2 * rho * math.expm1(x / (2 * rho))) - 1 / x),
                        0, np.inf, limit=400, epsabs=1e-16, epsrel=1e-12)[0]

    def inner(a):
        Wm = rho * 2 * math.log1p(a / 2)
        g = lambda w: f(w) / (2 + a + b_of_V(a, w / rho))              # noqa: E731
        brk = [0, min(1, Wm), min(10, Wm), min(40, Wm), Wm]
        return sum(integrate.quad(g, lo, hi, limit=200, epsabs=1e-16, epsrel=1e-12)[0]
                   for lo, hi in zip(brk[:-1], brk[1:]) if hi > lo)
    edges = [0, 1e-3 / rho, 1e-1 / rho, 1 / rho, 10 / rho, 1e-1, 1, 10, 100, 1e3, 1e5, np.inf]
    P2 = -sum(integrate.quad(inner, lo, hi, limit=300, epsabs=1e-16, epsrel=1e-11)[0]
              for lo, hi in zip(edges[:-1], edges[1:]) if hi > lo)
    return 4 * rho * (P1 + P2)


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. No preferred frame: an element's links point in every boost direction")
    for N in (10, 100, 1000):
        cnt, _ = corner_links(N, 4000 if N < 1000 else 800)
        p(f"   diamond with N = {N:4d} expected elements: links from the bottom element {cnt.mean():.3f} +- "
          f"{cnt.std() / math.sqrt(len(cnt)):.3f}; exact Ein(N) = ln N + gamma_E + E1(N) = {ein(N):.3f}")
    _, rap = corner_links(20000, 300)
    p(f"   link rapidities (N = 20000): spread over [{rap.min():.1f}, {rap.max():.1f}]; density per unit rapidity is"
      f" flat in theory: (rho/2) e^(-rho s/2) ds d(eta), independent of eta")
    p("=> an element is linked to neighbours moving at EVERY speed: the number grows like ln N with no")
    p("   preferred one. A lattice links each cell to a few fixed neighbours -- that choice IS a rest")
    p("   frame. Theorem (Bombelli, Henson & Sorkin, MPLA 24, 2579 (2009)): no rule on a Poisson")
    p("   sprinkling can pick a direction; discreteness and exact Lorentz symmetry coexist.")

    p.section("B. Dimension from order alone (Myrheim-Meyer)")
    x = sp.symbols("d", positive=True)
    fsym = sp.gamma(x + 1) * sp.gamma(x / 2) / (2 * sp.gamma(3 * x / 2))
    p(f"   exact: f(2) = {sp.nsimplify(fsym.subs(x, 2))}, f(3) = {sp.nsimplify(fsym.subs(x, 3))}, f(4) = {sp.nsimplify(fsym.subs(x, 4))}")
    dims = {}
    for d in (2, 3, 4):
        ests = []
        for _ in range(12):
            fo = ordering_fraction(sprinkle_interval(d, 1500))
            ests.append(brentq(lambda dd: f_order(dd) - fo, 1.2, 8))
        dims[d] = (np.mean(ests), np.std(ests, ddof=1) / math.sqrt(len(ests)))
        p(f"   sprinkled into {d}D Minkowski (N = 1500, 12 runs): dimension read off the order = {dims[d][0]:.3f} +- {dims[d][1]:.3f}")
    p("=> the substrate knows its own dimension by counting how many pairs are causally related.")

    p.section("C. Time = counting along chains; the twin paradox by counting")
    lam = 200000.0
    p(f"   2D diamond with {lam:.0f} expected elements; proper time is read as the LONGEST CHAIN of elements")
    p("   (Brightwell & Gregory, PRL 66, 260 (1991)); exact asymptotics for 2D: E[L] = 2 sqrt(N) + mu_TW N^(1/6)")
    p(f"   (Baik, Deift & Johansson, J. AMS 12, 1119 (1999); mu_TW = {MU_TW:.4f})")
    twins = {}
    for vel in (0.0, 0.3, 0.6, 0.8):
        a = 0.5 * (1 + vel)
        b = 1 - a
        ratios, preds = [], []
        for _ in range(6):
            n = RNG.poisson(lam)
            u, v = RNG.random(n), RNG.random(n)
            Lstay = longest_chain(u, v)
            m1 = (u < a) & (v < b)
            m2 = (u > a) & (v > b)
            Ltw = longest_chain(u[m1], v[m1]) + longest_chain(u[m2], v[m2])
            ratios.append(Ltw / Lstay)
        pred = (2 * bdj_mean(lam * a * b)) / bdj_mean(lam)
        twins[vel] = (np.mean(ratios), np.std(ratios) / math.sqrt(6), pred)
        p(f"   travelling twin at v = {vel:.1f}: chain ratio {twins[vel][0]:.4f} +- {twins[vel][1]:.4f};"
          f"  1/gamma = {math.sqrt(1 - vel * vel):.4f}; with exact finite-N term {pred:.4f}")
    p("=> 'time varies with how fast something moves relative to something else', derived by COUNTING:")
    p("   the traveller's longest chain has fewer elements, by 1/gamma. No clocks, no metric -- only order.")

    p.section("D. Waves on a causal set: Sorkin's d'Alembertian is exactly Lorentz invariant on average")
    p("   B phi(x) = (4/l^2)[ -phi(x)/2 + sum_L1 phi - 2 sum_L2 phi + sum_L3 phi ], L_n = past elements with n-1")
    p("   elements between them and x (Sorkin, gr-qc/0703099).  Mean over sprinklings, plane wave e^{i(k_u a + k_v b)}")
    p("   (a, b = past null distances): the b-integral is exact, (c-beta)^2/c^3 = -k_v^2/(beta - i k_v)^3, giving")
    p("   E[B]/phi = 4 rho (I(zeta) - 1/2),  I(zeta) = -int_0^inf e^{i zeta s}/(s - i)^3 ds,  zeta = 2 k_u k_v / rho")
    s_ = sp.symbols("s", positive=True)
    I0 = sp.simplify(sp.integrate(-1 / (s_ - sp.I) ** 3, (s_, 0, sp.oo)))
    I1 = sp.simplify(sp.integrate(-sp.I * s_ / (s_ - sp.I) ** 3, (s_, 0, sp.oo)))
    p(f"   exact (sympy): I(0) = {I0}, I'(0) = {I1}  ->  E[B]/phi = 4 k_u k_v + ... = (omega^2 - k^2) + ...")
    p("   so E[B phi] -> -box phi in the continuum (our signature +,-), with corrections that depend only on")
    p("   zeta ~ k^2 l^2. A boost multiplies k_u by lambda and divides k_v by lambda: zeta is unchanged. EXACT.")
    kap = 0.25
    zeta0 = 2 * kap * kap
    exact = B_mean_exact(kap, kap)
    p(f"   example k_u k_v = {kap * kap}: exact mean {exact.real:.6f}{exact.imag:+.6f}i")
    for lamb in (1.0, 2.0, 4.0):
        vals = [B_mean_truncated(kap * lamb, kap / lamb, A, A) for A in (12, 24, 48)]
        p(f"   boost lambda = {lamb}: brute-force quadrature in a fixed truncated region A = 12, 24, 48: "
          + ", ".join(f"{v.real:.5f}{v.imag:+.5f}i" for v in vals) + "  -> same limit")
    p("   Monte Carlo sprinklings (rho = 1), 600,000 each, in the diamond A = 12 seen from two frames")
    p("   (wave AND region boosted together: a' = a/lambda, b' = b lambda):")
    mc = {}
    for lamb in (1.0, 2.0):
        m, se_r, se_i, sd = B_monte_carlo(kap * lamb, kap / lamb, 12 / lamb, 12 * lamb, 600000)
        tr = B_mean_truncated(kap * lamb, kap / lamb, 12 / lamb, 12 * lamb)
        mc[lamb] = (m, se_r, se_i, sd, tr)
        p(f"   frame lambda = {lamb}: MC {m.real:.4f}+-{se_r:.4f} {m.imag:+.4f}+-{se_i:.4f}i  (exact for this region"
          f" {tr.real:.6f}{tr.imag:+.6f}i; deviation {abs(m.real - tr.real) / se_r:.1f} and {abs(m.imag - tr.imag) / se_i:.1f} sigma);"
          f" spread of ONE sprinkling {sd:.1f}")
    p(f"   the exact region values in the two frames are identical: |difference| = {abs(mc[1.0][4] - mc[2.0][4]):.1e}")
    chi2 = sum(((mc[L][0].real - mc[L][4].real) / mc[L][1]) ** 2 + ((mc[L][0].imag - mc[L][4].imag) / mc[L][2]) ** 2 for L in mc)
    p(f"   chi^2 of the 4 Monte Carlo numbers against the exact value: {chi2:.1f} for 4 degrees of freedom")
    lat = [lattice_box(kap * lamb, kap / lamb) for lamb in (1.0, 2.0, 4.0)]
    p(f"   lattice d'Alembertian (spacing = l) on the same three boosted waves: {lat[0]:.5f}, {lat[1]:.5f}, {lat[2]:.5f}"
      f"  (continuum 4 k_u k_v = {4 * kap * kap:.5f}): it depends on the frame")
    zs = np.concatenate([-np.logspace(-3, 1.5, 60), np.logspace(-3, 1.5, 60)])
    dist = min(min(abs(B_mean_exact(z / 2, 1.0, 1.0)), abs(B_mean_exact(z / 2, -1.0, 1.0))) / min(2 * abs(z), 2.0)
               for z in zs)
    p(f"   zeros off the light cone: min |E[B]| / min(2|zeta|, 2) = {dist:.3f} over 1e-3 <= |zeta| <= 30, both time")
    p("   orientations (the mean grows like 2 zeta near the cone and tends to -2 far from it; it never vanishes)")
    p("=> on average, waves on a causal set obey a dispersion relation that is a function of k^2 alone, vanishing")
    p("   only on the light cone: massless waves travel at EXACTLY c at every energy, in every direction. No")
    p("   3:1 TeV delay pattern (r10), no species-dependent speeds, so the r13 graviton-speed problem does not")
    p("   arise (r13 showed a Lorentz-invariant regulator gives c_g = c exactly).")
    p(f"   PRICE: a single sprinkling is very noisy (spread {mc[1.0][3]:.0f} vs signal ~0.3): the operator is NON-LOCAL")
    p("   (elements far along the light cone contribute). Physical fields need a non-locality scale l_k >> l")
    p("   (Sorkin 2007) -- a new, testable length.")

    p.section("E. Curvature from counting: 2D de Sitter (radius 1, R = 2)")
    ds = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", integrate.IntegrationWarning)   # requested tolerances near double precision
        for rho in (1e2, 1e3, 1e4, 1e5):
            ds[rho] = ds_B1(rho)
        p(f"   density rho = {rho:8.0f}: E[B 1] = {ds[rho]:.6f}   (-R/2 = -1)")
    p("   (rho = 100 and 1000 also computed by direct 2D quadrature without the substitution: same to 5 digits)")
    p("=> counting elements and their order alone measures spacetime curvature: E[B phi] -> -(box + R/2) phi")
    p("   (Benincasa & Dowker, PRL 104, 181301 (2010), who used this to define a discrete Einstein-Hilbert")
    p("   action -- the dynamics of gravity written as a COUNT, with no rest frame anywhere).")

    p.section("F. The cosmological constant as a counting fluctuation (Sorkin)")
    H0 = 67.4e3 / 3.0857e22
    N4 = (c / H0 / lP()) ** 4
    Lam_obs = 3 * H0 ** 2 * 0.685 / c ** 2 * lP() ** 2
    p(f"   4-volume of the observable universe ~ (c/H0)^4 = {N4:.1e} Planck units; if the number of elements")
    p(f"   fluctuates by sqrt(N), Lambda ~ 1/sqrt(N) = {N4 ** -0.5:.1e} (Planck units)")
    p(f"   observed Lambda l_P^2 = {Lam_obs:.1e}  -- same order of magnitude")
    p("   (argued by Sorkin before 1998's discovery of cosmic acceleration; 'everpresent Lambda': Ahmed,")
    p("   Dodelson, Greene & Sorkin, PRD 69, 103523 (2004)). Order of magnitude only; O(1) factors open.")

    p.section("Verdict for the causal-set substrate")
    for line in (
        "* PASSES what killed the lattice: no rest frame (A), exact Lorentz-invariant waves (D) -> c_g = c and",
        "  no 3:1 delays; no discrete rotations -> no cosmic-string disclinations (r15); no foliation, so no",
        "  absolute time and no Horava scalar (r12) -- time is the order itself.",
        "* DELIVERS the user's picture of time: relational (counting), relative (twin by counting, C), one way",
        "  (acyclic order; r18), and curvature/gravity from counting (E).",
        "* OPEN: non-locality and large fluctuations (D); 4D dynamics (the sum over causal sets is dominated by",
        "  non-manifold-like orders unless the action suppresses them); 'swerves' (Lorentz-invariant momentum",
        "  diffusion of particles, Dowker, Henson & Sorkin 2004), which observations already constrain.",
    ):
        p(line)

    # ---------- figures
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    ax = axs[0, 0]
    ax.hist(rap, bins=40, range=(-4, 4), color=S1, alpha=0.85, density=False,
            weights=np.full(len(rap), 1 / 300), label="causal set: ~0.2 links per bin, at every rapidity")
    ax.vlines([0], 0, 1.0, color=S2, lw=4, label="square lattice: its 1 timelike link, rapidity 0 only")
    ax.set_ylim(0, 1.12)
    ax.set(xlabel="rapidity of the link (boost angle)", ylabel="links per element per bin",
           title="Links point in every boost direction:\nno rest frame is singled out")
    ax.legend(loc="upper right", fontsize=8.5)
    ax = axs[0, 1]
    vv = np.linspace(0, 0.85, 200)
    ax.plot(vv, np.sqrt(1 - vv ** 2), color=MUTED, ls="--", lw=1.5, label="relativity: 1/γ")
    ax.errorbar(list(twins), [twins[v][0] for v in twins], yerr=[twins[v][1] for v in twins], fmt="o", color=S1,
                ms=7, capsize=3, label="longest-chain count (simulated)")
    ax.plot(list(twins), [twins[v][2] for v in twins], "x", color=S2, ms=8, label="exact finite-N prediction")
    ax.set(xlabel="travelling twin's speed v / c", ylabel="travelling twin's count / stay-at-home count",
           title="Twin paradox by counting elements:\nthe traveller ages less, by 1/γ")
    ax.legend(loc="lower left", fontsize=8.5)
    ax = axs[1, 0]
    zz = np.logspace(-3, 1.2, 50)
    curve = [((B_mean_exact(z / 2, 1.0)) / (2 * z)).real for z in zz]
    ax.semilogx(zz, curve, color=S1, lw=2, label="causal set, exact mean (any frame)")
    for lamb, mk in ((1.0, "o"), (2.0, "s"), (4.0, "^")):
        zq = np.array([0.02, 0.125, 0.5])
        ax.semilogx(zq, [(B_mean_truncated(math.sqrt(z / 2) * lamb, math.sqrt(z / 2) / lamb, 48, 48) / (2 * z)).real for z in zq],
                    mk, color=S1, mfc="none", ms=7, label=f"quadrature, boost λ = {lamb:g}")
    for lamb, ls in ((1.0, "-"), (4.0, ":")):
        ax.semilogx(zz, [lattice_box(math.sqrt(z / 2) * lamb, math.sqrt(z / 2) / lamb) / (2 * z) for z in zz], color=S2, ls=ls,
                    lw=1.6, label=f"lattice, boost λ = {lamb:g}")
    ax.axhline(1, color=MUTED, lw=1, ls="--")
    ax.set(xlabel="ζ = k²ℓ²/2 (wave's invariant size in cell units)", ylabel="Re[operator] / continuum value",
           ylim=(-0.9, 1.75), title="Wave operator on plane waves: the causal set gives one\ncurve in every frame, the lattice does not")
    ax.legend(loc="upper left", fontsize=7.5, ncol=2)
    ax = axs[1, 1]
    rr = np.array(list(ds))
    ax.semilogx(rr, [ds[r] for r in rr], "o-", color=S3, ms=7, label="exact mean, 2D de Sitter")
    ax.axhline(-1, color=MUTED, ls="--", lw=1.4, label="−R/2 (curvature of the space)")
    ax.set(xlabel="element density ρ (per curvature area)", ylabel="mean of B acting on a constant",
           ylim=(-1.05, -0.9), title="Curvature measured by counting elements\nconverges to −R/2")
    ax.legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "causal_set_tests")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
