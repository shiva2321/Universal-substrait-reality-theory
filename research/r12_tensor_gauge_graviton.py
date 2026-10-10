"""
r12 - Building a graviton from the substrate: the gauge route  (LAB_NOTEBOOK.md entry E17)

Question (user): "Deriving the protected spin-2 mode from the substrate is the open core
problem -- let's research it with field-established and out-of-the-box ways."

r02 showed that light comes out right (exactly 2 polarisations, massless, isotropic) when the
substrate's field is a VECTOR with a gauge redundancy A -> A + d chi ("twist-only" stiffness).
The spin-2 analogue: a SYMMETRIC TENSOR field h_ij on the lattice (a local strain/metric of the
substrate) whose stiffness is blind to h -> h + d xi + d xi (moving the cells around changes
nothing physical).  Field-established versions: linearised GR (ADM), Gu & Wen (2006, 2012),
Xu (2006), Pretko (2017), Horava (2009), Blas-Pujolas-Sibiryakov (2010).

On a cubic lattice every difference becomes i d_a(k), d_a = 2 sin(k_a/2).  For each k we build
the 6x6 kinetic and stiffness matrices of h_ij and count the propagating modes and their
helicities, for five substrates:
  M1  elastic tensor medium (no gauge symmetry)
  M2  spatial-gauge medium with curvature-squared stiffness (Xu's "soft gravitons")
  M3  spatial-gauge medium with Einstein stiffness and an ABSOLUTE TIME (projectable Horava):
      what a substrate with a preferred rest frame -- like USRT's -- naturally gives
  M4  M3 plus the Blas-Pujolas-Sibiryakov term alpha (grad lapse)^2 ("healthy" extension)
  M5  full GR: the local Hamiltonian constraint (time-reparametrisation gauge) is added
Kinetic term (DeWitt metric) (1/4)(hdot:hdot - lambda (tr hdot)^2); GR has lambda = 1.
Einstein stiffness = -(sqrt(g) R)^(2), the quadratic part of the curvature of the strain.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.linalg import eig, null_space  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r12_tensor_gauge_graviton"
EPS = np.zeros((3, 3, 3))
for a, b, cc in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
    EPS[a, b, cc], EPS[a, cc, b] = 1, -1

# orthonormal basis of symmetric 3x3 matrices (Frobenius inner product)
BASIS = []
for i in range(3):
    m = np.zeros((3, 3)); m[i, i] = 1; BASIS.append(m)
for i, j in ((0, 1), (0, 2), (1, 2)):
    m = np.zeros((3, 3)); m[i, j] = m[j, i] = 1 / np.sqrt(2); BASIS.append(m)
BASIS = np.array(BASIS)                       # (6, 3, 3)
TR = np.array([np.trace(b) for b in BASIS])   # trace as a 6-vector


def mat(v):
    return np.einsum("a,aij->ij", v, BASIS)


def quad_matrix(form):
    """6x6 symmetric matrix of a quadratic form f(h) given as a function of a 3x3 matrix."""
    Q = np.zeros((6, 6))
    for a in range(6):
        for b in range(6):
            Q[a, b] = 0.25 * (form(BASIS[a] + BASIS[b]) - form(BASIS[a] - BASIS[b]))
    return Q


def lattice_d(k):
    return 2 * np.sin(np.asarray(k, float) / 2)


def kinetic(lam):
    return 0.25 * (np.eye(6) - lam * np.outer(TR, TR))


def V_einstein(d):
    D2 = d @ d
    return quad_matrix(lambda h: 0.25 * (D2 * np.sum(h * h) - 2 * np.sum((d @ h) ** 2)
                                         + 2 * (d @ h @ d) * np.trace(h) - D2 * np.trace(h) ** 2))


def V_curv2(d):
    def inc(h):
        return np.einsum("iab,jcd,a,c,bd->ij", EPS, EPS, d, d, h)
    return quad_matrix(lambda h: 0.25 * np.sum(inc(h) ** 2))


def V_elastic(d, mix=1.0):
    D2 = d @ d
    return quad_matrix(lambda h: 0.25 * (D2 * np.sum(h * h) + mix * np.sum((d @ h) ** 2)))


def gauge_dirs(d):
    """h = d xi + xi d for xi = e_x, e_y, e_z (the 3 'moving the cells' directions)."""
    B = []
    for a in range(3):
        xi = np.zeros(3); xi[a] = 1
        h = np.outer(d, xi) + np.outer(xi, d)
        B.append([np.sum(h * b) for b in BASIS])
    return np.array(B).T                       # (6, 3)


def hamiltonian_constraint(d):
    """R^(1)(h) = D^2 tr h - d.h.d as a 6-vector (linearised scalar curvature of the strain)."""
    return np.array([(d @ d) * np.trace(b) - d @ b @ d for b in BASIS])


def J2_matrix(d):
    """Square of the rotation generator about d, acting on symmetric tensors (6x6, Euclidean basis)."""
    n = d / np.linalg.norm(d)
    S = -1j * np.einsum("abc,c->ab", EPS, n)
    J2 = np.zeros((6, 6), complex)
    for b in range(6):
        h = BASIS[b].astype(complex)
        Jh = S @ h - h @ S
        J2h = S @ Jh - Jh @ S
        J2[:, b] = [np.sum(BASIS[a] * J2h) for a in range(6)]
    return np.real(J2)


def helicity_resolved(Wq, Aq, Q, d, tol=1e-7):
    """Solve Wq x = w^2 Aq x; inside each degenerate group diagonalise J^2 (helicity^2)."""
    w2, X = eig(Wq, Aq)
    w2 = np.real(w2)
    order = np.argsort(w2)
    w2, X = w2[order], np.real(X[:, order])
    J2 = J2_matrix(d)
    out, i = [], 0
    while i < len(w2):
        j = i + 1
        while j < len(w2) and abs(w2[j] - w2[i]) < tol * max(1.0, abs(w2[i])):
            j += 1
        V = Q @ X[:, i:j]                         # physical (transverse) representatives
        U, _ = np.linalg.qr(V)
        hs, Y = np.linalg.eigh(U.T @ J2 @ U)
        for m in range(j - i):
            y = np.linalg.lstsq(Q, U @ Y[:, m], rcond=None)[0]
            out.append((float(w2[i]), float(np.sqrt(max(hs[m], 0))), float(np.sign(y @ Aq @ y))))
        i = j
    return out


def modes(model, k, lam=1.0, alpha=0.5):
    """Return list of (omega^2, |helicity|, norm sign) of the physical modes at wavevector k."""
    d = lattice_d(k)
    D2 = d @ d
    if model == "M1":
        A, W, Q = kinetic(0.0), V_elastic(d), np.eye(6)
    else:
        B = gauge_dirs(d)
        Q = null_space(B.T)                    # transverse representatives (6x3)
        if model == "M5":                      # Hamiltonian constraint: R1(h) = 0 as well
            C = hamiltonian_constraint(d) @ Q
            Q = Q @ null_space(C[None, :])
            lam = 1.0
        L = 0.0 if model == "M2" else lam
        A = kinetic(L)
        if model != "M5":                      # shift integrated out: kinetic on the quotient
            GB = A @ B
            M = B.T @ GB
            if abs(np.linalg.det(M)) > 1e-12 * D2 ** 3:
                A = A - GB @ np.linalg.solve(M, GB.T)
        W = V_curv2(d) if model == "M2" else V_einstein(d)
        if model == "M4":                      # lapse integrated out with alpha (grad n)^2
            c = hamiltonian_constraint(d)
            W = W + np.outer(c, c) / (4 * alpha * D2)
    Aq, Wq = Q.T @ A @ Q, Q.T @ W @ Q
    return sorted(helicity_resolved(Wq, Aq, Q, d), key=lambda t: (t[1], t[0]))


def scalar_mode(lam, alpha=None, k=(0.0, 0.0, 0.05)):
    d = lattice_d(k)
    ms = modes("M3" if alpha is None else "M4", k, lam=lam, alpha=alpha if alpha else 0.5)
    s = [m for m in ms if m[1] < 0.5][0]
    return s[0] / (d @ d), s[2]


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Mode count and helicities at a generic wavevector (k = (0.13, 0.31, 0.47))")
    k = np.array([0.13, 0.31, 0.47])
    D2 = lattice_d(k) @ lattice_d(k)
    labels = {"M1": "elastic tensor medium, no gauge symmetry",
              "M2": "spatial gauge, curvature^2 stiffness (Xu 2006)",
              "M3": "spatial gauge, Einstein stiffness, absolute time (lambda = 1.2)",
              "M4": "M3 + healthy extension (alpha = 0.5)",
              "M5": "full GR: + local Hamiltonian constraint"}
    for m, lab in labels.items():
        ms = modes(m, k, lam=1.2, alpha=0.5)
        desc = ", ".join(f"h={hh:.0f}: w^2/D^2={w2 / D2:+.3f}{' GHOST' if s < 0 else ''}" for w2, hh, s in ms)
        p(f"{m} {lab}")
        p(f"     {len(ms)} modes -> {desc}")
    p("Read: M1 has 6 waves (helicity 0, 0, 1, 1, 2, 2) -- like r02's elastic lattice, too many.")
    p("      The gauge redundancy removes 3 (h = 0, 1, 1). What is left is 2 helicity-2 waves")
    p("      PLUS one helicity-0 wave, except in M5, where the Hamiltonian constraint removes it.")

    p.section("B. The helicity-2 waves of M3-M5 have EXACTLY the lattice photon's dispersion")
    rng = np.random.default_rng(1)
    worst = 0.0
    for _ in range(200):
        kk = rng.uniform(-np.pi, np.pi, 3)
        d = lattice_d(kk)
        for w2, hh, _s in modes("M5", kk):
            worst = max(worst, abs(w2 - d @ d))
    p(f"200 random k in the Brillouin zone: max |omega^2 - 4 sum sin^2(k/2)| = {worst:.1e}")
    p("=> graviton and photon (r02) on the same lattice share the SAME dispersion relation, including")
    p("   the lattice corrections: one light cone at all energies, as GW170817 demands (r11), PROVIDED")
    p("   the overall stiffness/inertia ratio of both fields is the same number (one input, not two).")
    for direction, kd in (("[100]", (1, 0, 0)), ("[111]", (1, 1, 1))):
        kd = np.array(kd, float) / np.linalg.norm(kd)
        k0, dk = 0.03, 1e-4
        w = [np.sqrt(modes("M5", s * kd)[0][0]) for s in (k0 - dk, k0 + dk)]
        vg = (w[1] - w[0]) / (2 * dk)
        p(f"   group-velocity deficit along {direction} at ka = 0.03: 1 - v_g/c = {1 - vg:.3e}"
          f"  (light, r10: (1/8)(ka)^2 sum n^4 = {k0 ** 2 / 8 * np.sum(kd ** 4):.3e})")

    p.section("C. Curvature-squared stiffness (M2): gravitons with omega ~ k^2 -> a CONFINING force")
    for s in (0.02, 0.04, 0.08):
        kk = np.array([0, 0, s])
        w = np.sqrt([m[0] for m in modes("M2", kk)])
        p(f"   k = {s:.2f}: omega = {np.round(w, 6)}  (omega/k^2 = {np.round(w / s ** 2, 3)})")
    N = 128
    kg = 2 * np.pi * np.fft.fftfreq(N)
    KX, KY, KZ = np.meshgrid(kg, kg, kg, indexing="ij")
    lam_ = 4 * (np.sin(KX / 2) ** 2 + np.sin(KY / 2) ** 2 + np.sin(KZ / 2) ** 2)
    with np.errstate(divide="ignore"):
        G2 = np.real(np.fft.ifftn(np.where(lam_ > 0, 1 / lam_, 0)))
        G4 = np.real(np.fft.ifftn(np.where(lam_ > 0, 1 / lam_ ** 2, 0)))
    r = np.arange(1, 13)
    pot2 = G2[r, 0, 0] - G2[12, 0, 0]
    pot4 = G4[r, 0, 0] - G4[0, 0, 0]
    slope = np.polyfit(r[2:], pot4[2:], 2)[1]
    p(f"static potential of a point source, stiffness ~ k^4 (128^3 lattice, fit a + b r + c r^2 for the box):"
      f" b = {slope:.4f} (continuum -r/(8 pi): {-1 / (8 * np.pi):.4f})")
    p("=> a k^4 ('curvature squared') stiffness gives a potential ~ r: masses would be CONFINED, not")
    p("   attracted by 1/r. Newton's law needs the Einstein stiffness ~ k^2 (models M3-M5).")

    p.section("D. A substrate with an absolute time (M3): the extra helicity-0 'scalar graviton'")
    p("Analytic (linearised projectable Horava gravity): omega^2 = -k^2 (lambda-1)/(3 lambda-1), kinetic sign (1-3lambda)/(1-lambda)")
    lams = [-0.5, 0.0, 0.2, 0.5, 0.8, 0.95, 1.05, 1.2, 2.0, 3.0]
    healthy = []
    for L in lams:
        w2, s = scalar_mode(L)
        exact = -(L - 1) / (3 * L - 1)
        status = "UNSTABLE (omega^2 < 0)" if w2 < 0 else ("GHOST (negative energy)" if s < 0 else "healthy")
        if status == "healthy":
            healthy.append(L)
        p(f"   lambda = {L:5.2f}: lattice omega^2/D^2 = {w2:+.4f} (analytic {exact:+.4f}), norm {s:+.0f} -> {status}")
    p(f"healthy values of lambda found: {healthy if healthy else 'NONE'}")
    p("=> with only spatial gauge symmetry (cells can be moved, but time is absolute), the substrate")
    p("   ALWAYS carries a third, helicity-0 graviton that is either a ghost or unstable. At lambda = 1")
    p("   (the GR value) its kinetic coefficient diverges: it freezes, but becomes strongly coupled.")
    p("   This is the known pathology of projectable Horava gravity (Charmousis, Niz, Padilla & Saffin")
    p("   2009; Blas, Pujolas & Sibiryakov 2009; Koyama & Arroja 2010) -- reproduced here on the lattice.")

    p.section("E. Two ways out")
    p("(i) healthy extension (M4): let the lapse vary in space with stiffness alpha (grad ln N)^2:")
    for L, al in ((1.2, 0.5), (1.05, 0.1), (2.0, 1.5), (1.2, 2.5)):
        w2, s = scalar_mode(L, alpha=al)
        exact = (2 - al) / al * (L - 1) / (3 * L - 1)
        st = "UNSTABLE" if w2 < 0 else ("GHOST" if s < 0 else "healthy")
        p(f"   lambda = {L:4.2f}, alpha = {al:3.1f}: omega^2/D^2 = {w2:+.4f} (BPS analytic {exact:+.4f}) -> {st}")
    p("   healthy for lambda > 1, 0 < alpha < 2. But the extra scalar then exists and must be hidden:")
    p("   preferred-frame tests (|alpha_1| < ~4e-5 pulsars, |alpha_2| < ~2e-9 solar spin/pulsars; Shao & Wex")
    p("   2012, Shao et al. 2013) and GW170817 squeeze the extra couplings to the 1e-5 level or below")
    p("   (Gumrukcuoglu, Saravani & Sotiriou 2018).")
    p("(ii) the local Hamiltonian constraint (M5): exactly 2 helicity-2 modes, as observed. It says")
    p("   'the energy at each place is a constraint, not a clock': time reparametrisation is a gauge")
    p("   symmetry. A substrate with an absolute time does not have it automatically. It is the")
    p("   spacetime version of Page-Wootters (time = correlations; H Psi = 0) -- but LOCAL, at each cell.")

    p.section("F. Out of the box: graviton = photon x photon (the double copy)")
    p("Tree-level gravity amplitudes are squares of gauge amplitudes (Kawai-Lewellen-Tye 1986; Bern,")
    p("Carrasco & Johansson 2008-10). In polarisation language, twist (x) twist:")
    n = np.array([0, 0, 1.0])
    ep = np.array([1, 1j, 0]) / np.sqrt(2)
    em = np.conj(ep)
    S = -1j * np.einsum("abc,c->ab", EPS, n)
    for a, la in ((ep, "+1"), (em, "-1")):
        for b, lb in ((ep, "+1"), (em, "-1")):
            h = np.outer(a, b)
            Jh = S @ h - h @ S
            hel = np.real(np.sum(np.conj(h) * Jh) / np.sum(np.conj(h) * h))
            p(f"   photon {la} x photon {lb}: helicity {hel:+.0f}")
    p("   => helicity +2, -2 (graviton) + two helicity-0 states (dilaton = trace, axion = antisymmetric).")
    p("   The dilaton couples to T like a scalar: it would make gamma != 1 and violate the equivalence")
    p("   principle unless massive. Torsion balances exclude a gravity-strength Yukawa beyond ~39 um")
    p(f"   (Lee et al., PRL 124, 101101 (2020)) -> dilaton mass > hbar c / 39 um = {1.97327e-7 / 38.6e-6 * 1e3:.1f} meV.")
    p("   So 'gravity = light squared' fits the substrate idea (r02 gives the twist), but the extra")
    p("   scalars must be gapped, and it is a relation between amplitudes, not a construction.")

    # ---------- figures
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    path = [(0, 0, 0), (np.pi, 0, 0), (np.pi, np.pi, 0), (np.pi, np.pi, np.pi), (0, 0, 0)]
    ticks, xs, rows = [0], [], {"M1": [], "M3": [], "M5": []}
    t = 0.0
    for a, b in zip(path[:-1], path[1:]):
        a, b = np.array(a, float), np.array(b, float)
        for s in np.linspace(0, 1, 40, endpoint=False)[1:] if t == 0 else np.linspace(0, 1, 40, endpoint=False):
            kk = a + s * (b - a)
            if np.linalg.norm(kk) < 1e-9:
                continue
            xs.append(t + s * np.linalg.norm(b - a))
            for m in rows:
                rows[m].append(modes(m, kk, lam=1.2))
        t += np.linalg.norm(b - a)
        ticks.append(t)
    xs = np.array(xs)
    col = {2: S1, 1: S2, 0: S3}
    titles = {"M1": "Elastic tensor medium: 6 waves (3 overlap)",
              "M3": "Absolute-time substrate (λ = 1.2): 3 waves",
              "M5": "Full GR constraints: 2 waves, both helicity 2"}
    for ax, m in zip(axs, ("M1", "M3", "M5")):
        seen = set()
        for i in range(len(rows[m][0])):
            w2 = np.array([r[i][0] for r in rows[m]])
            hh = int(round(np.median([r[i][1] for r in rows[m]])))
            y = np.sign(w2) * np.sqrt(np.abs(w2))
            lab = None if hh in seen else {2: "helicity ±2 (graviton)", 1: "helicity ±1", 0: "helicity 0"}[hh]
            seen.add(hh)
            ax.plot(xs, y, ".", ms=2.2, color=col[hh], label=lab)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xticks(ticks)
        ax.set_xticklabels(["Γ", "X", "M", "R", "Γ"])
        ax.set(title=titles[m], xlabel="wavevector path through the Brillouin zone",
               ylabel="frequency (negative = unstable, sign(ω²)√|ω²|)" if m == "M1" else None)
        ax.legend(loc="lower right" if m == "M3" else "lower center", fontsize=8.5, markerscale=5)
    axs[0].set_ylim(-0.3, 5.2)
    axs[1].set_ylim(-2.5, 4.2)
    axs[2].set_ylim(-0.3, 4.2)
    fig.tight_layout()
    save_fig(fig, NAME, "dispersion")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2))
    LL = np.linspace(-0.6, 3.0, 2000)
    w2a = -(LL - 1) / (3 * LL - 1)
    kin = (1 - 3 * LL) / (1 - LL)
    w2a[np.abs(w2a) > 3] = np.nan                   # break the curves at the poles
    kin[np.abs(kin) > 3] = np.nan
    axs[0].axvspan(-0.6, 1 / 3, color="#f4e4dc", lw=0)
    axs[0].axvspan(1, 3.0, color="#f4e4dc", lw=0)
    axs[0].axvspan(1 / 3, 1, color="#ebeae6", lw=0)
    axs[0].plot(LL, w2a, color=S3, lw=2, label="extra scalar: ω²/k²")
    axs[0].plot(LL, kin, color=MUTED, lw=1.5, ls="--", label="its kinetic coefficient (1−3λ)/(1−λ)")
    lam_pts = [-0.5, 0.0, 0.5, 0.8, 1.2, 2.0]
    axs[0].plot(lam_pts, [scalar_mode(L)[0] for L in lam_pts], "o", color=S3, mfc="none", ms=7, label="lattice calculation")
    axs[0].axhline(0, color=MUTED, lw=0.8)
    for x0, txt in ((-0.13, "unstable\n(ω² < 0)"), (0.67, "ghost\n(negative energy)"), (2.0, "unstable\n(ω² < 0)")):
        axs[0].text(x0, 2.35, txt, color=INK_2, fontsize=8.5, ha="center")
    axs[0].text(1.02, -0.55, "GR: λ = 1", color=INK_2, fontsize=8.5)
    axs[0].set(xlim=(-0.6, 3.0), ylim=(-3, 3), xlabel="λ (kinetic coefficient of the strain's trace)",
               title="Absolute-time substrate: the extra scalar is never healthy")
    axs[0].legend(loc="lower right", fontsize=8.5)
    rr = r.astype(float)
    axs[1].plot(rr, pot2 / abs(pot2[0]), "o-", color=S1, ms=4, label="Einstein stiffness (k²): 1/r, falls off")
    axs[1].plot(rr, pot4 / abs(pot4[-1]), "s-", color=S2, ms=4, label="curvature² stiffness (k⁴): grows ∝ r")
    axs[1].set(xlabel="distance from a point mass (cells)", ylabel="potential (scaled, sign-normalised)",
               title="Why the stiffness must be Einstein-like")
    axs[1].legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "scalar_mode")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
