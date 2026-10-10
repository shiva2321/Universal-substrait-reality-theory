"""
r13 - Sakharov's induced gravity in the substrate: G from the cells, and the speed problem
(LAB_NOTEBOOK.md entry E18)

Question (user): find the protected spin-2 mode "with field-established and out-of-the-box ways
... and see if we can solve it or not, based on our theory as well".

Sakharov (1967): spacetime's stiffness (1/16 pi G) need not be fundamental.  The zero-point
jiggling of every field living in the substrate resists being strained, and that resistance IS
the Einstein-Hilbert term.  Here we compute it directly, for scalar fields living on the cubic
substrate lattice, and ask two questions the field rarely asks this concretely:
  1. how big must the cells be to give the measured G?
  2. does the induced graviton travel at the same speed as light (GW170817 says: to 1e-15)?

Method.  Strain the lattice with a transverse-traceless "+" wave h_xx = -h_yy = h(t) cos(qz):
the scalar's stiffness becomes g^{ij} = delta - h.  Second-order vacuum energy gives
  static stiffness  E(q) - E(0) = (h^2/16) beta q^2,   beta = -1/2 d^2/dq^2 Int g^2/(w w'(w+w')),
  inertia           L = (1/2) M hdot^2 (uniform strain), M = Int g^2 / (32 w^5),
with g = d_x^2 - d_y^2 the strain vertex.  The induced graviton speed is c_g^2 = beta/(4M), and
G = 1/(16 pi M) (Einstein-Hilbert: L = hdot^2/(32 pi G) for this strain).
Checks: the second-order formula against exact diagonalisation; a Lorentz-invariant regulator
(Pauli-Villars) must give c_g = 1 and Sakharov's heat-kernel value 1/16piG = mu^2 ln2/(96 pi^2).
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.optimize import brentq, curve_fit  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r13_induced_gravity"
PI = math.pi
PV = ((1, 0.0), (-2, 1.0), (1, math.sqrt(2)))      # Pauli-Villars: sum c = 0, sum c m^2 = 0
GW170817 = 3e-15                                   # |v_gw - c|/c (r11)


# ---------------------------------------------------------------- A. validation on a small lattice
def exact_E0(L, m, h, qn):
    ks = 2 * PI * np.arange(L) / L
    z = np.arange(L)
    q = 2 * PI * qn / L
    lap = 2 * np.eye(L) - np.roll(np.eye(L), 1, 0) - np.roll(np.eye(L), -1, 0)
    E = 0.0
    for kx in ks:
        for ky in ks:
            dx2, dy2 = 4 * np.sin(kx / 2) ** 2, 4 * np.sin(ky / 2) ** 2
            K = lap + np.diag((1 - h * np.cos(q * z)) * dx2 + (1 + h * np.cos(q * z)) * dy2 + m * m)
            E += 0.5 * np.sum(np.sqrt(np.linalg.eigvalsh(K)))
    return E


def second_order(L, m, h, qn):
    ks = 2 * PI * np.arange(L) / L
    q = 2 * PI * qn / L
    PX, PY, PZ = np.meshgrid(ks, ks, ks, indexing="ij")
    dx2, dy2 = 4 * np.sin(PX / 2) ** 2, 4 * np.sin(PY / 2) ** 2
    w = np.sqrt(dx2 + dy2 + 4 * np.sin(PZ / 2) ** 2 + m * m)
    w2 = np.sqrt(dx2 + dy2 + 4 * np.sin((q - PZ) / 2) ** 2 + m * m)
    return -(h * h / 16) * np.sum((dx2 - dy2) ** 2 / (w * w2 * (w + w2)))


# ---------------------------------------------------------------- B. continuum (radial integrands)
def M_cont(p, m):
    w = math.hypot(p, m)
    return p ** 6 / w ** 5 / (240 * PI ** 2)


def B_cont(p, m):
    w = math.hypot(p, m)
    return -(p ** 6 * ((8 * p * p / 21) / w ** 7 - 0.8 / w ** 5)) / (16 * PI ** 2)


def pv_continuum(f, mu=1.0):
    g = lambda p: sum(cc * f(p, m * mu) for cc, m in PV)   # noqa: E731
    return quad(g, 0, 50 * mu, limit=500)[0] + quad(g, 50 * mu, np.inf, limit=500)[0]


# ---------------------------------------------------------------- C. lattice Brillouin-zone integrals
def gl_grid(edges, n):
    x, w = np.polynomial.legendre.leggauss(n)
    X = [0.5 * (b - a) * x + 0.5 * (b + a) for a, b in zip(edges[:-1], edges[1:])]
    W = [0.5 * (b - a) * w for a, b in zip(edges[:-1], edges[1:])]
    return np.concatenate(X), np.concatenate(W)


def lattice_MB(m, edges, n=16):
    """Inertia M and stiffness beta (units of 1/a^2) for one scalar of mass m on the cubic lattice."""
    x, w = gl_grid(edges, n)                       # octant [0, pi]; integrands are even
    PX, PY, PZ = np.meshgrid(x, x, x, indexing="ij")
    WW = w[:, None, None] * w[None, :, None] * w[None, None, :]
    dx2, dy2 = 4 * np.sin(PX / 2) ** 2, 4 * np.sin(PY / 2) ** 2
    om = np.sqrt(dx2 + dy2 + 4 * np.sin(PZ / 2) ** 2 + m * m)
    g2 = (dx2 - dy2) ** 2
    M = np.sum(WW * g2 / (32 * om ** 5)) * 8 / (2 * PI) ** 3
    uq, uqq = -2 * np.sin(PZ), 2 * np.cos(PZ)
    wq = uq / (2 * om)
    wqq = uqq / (2 * om) - uq ** 2 / (4 * om ** 3)
    Fqq = (7 / (4 * om ** 5)) * wq ** 2 - (3 / (4 * om ** 4)) * wqq
    B = -0.5 * np.sum(WW * g2 * Fqq) * 8 / (2 * PI) ** 3
    return M, B


def lattice_pv(mu, n=16):
    edges = sorted({0, mu / 8, mu / 3, mu, 3 * mu, 10 * mu, PI})
    edges = [e for e in edges if e <= PI]
    tot = np.zeros(2)
    for cc, m in PV:
        tot += cc * np.array(lattice_MB(m * mu, edges, n))
    return tot


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Check the method: second-order vacuum energy vs exact diagonalisation")
    L, m, h = 12, 0.3, 0.02
    e0 = exact_E0(L, m, 0.0, 0)
    for qn in (1, 2, 3):
        ex = 0.5 * (exact_E0(L, m, h, qn) + exact_E0(L, m, -h, qn)) - e0
        pt = second_order(L, m, h, qn)
        p(f"12^3 lattice, mass 0.3, strain h = {h}, q = 2 pi {qn}/12: exact {ex:.7f}, formula {pt:.7f}"
          f"  (rel. diff {abs(ex - pt) / abs(ex):.1e})")
    p("=> the formula is right; the energy rises with q, so strained space is STIFF (beta > 0).")

    p.section("B. Continuum: a Lorentz-invariant regulator gives c_g = c and Sakharov's G")
    Mh = quad(M_cont, 0, 1, args=(0.0,))[0]
    Bh = quad(B_cont, 0, 1, args=(0.0,))[0]
    p(f"hard momentum cutoff Lambda = 1: M = {Mh * 480 * PI ** 2:.4f} Lambda^2/(480 pi^2),  beta = "
      f"{Bh * 840 * PI ** 2 / 11:.4f} x 11 Lambda^2/(840 pi^2)")
    p(f"   -> c_g^2 = beta/(4M) = {Bh / (4 * Mh):.5f} = 11/7: the graviton would be {math.sqrt(Bh / (4 * Mh)):.3f} c")
    Mpv, Bpv = pv_continuum(M_cont), pv_continuum(B_cont)
    sak = math.log(2) / (96 * PI ** 2)
    p(f"Pauli-Villars (masses 0, mu, sqrt2 mu; weights 1, -2, 1): M = {Mpv:.7e} mu^2,"
      f" Sakharov heat kernel mu^2 ln2/(96 pi^2) = {sak:.7e}")
    p(f"   -> c_g^2 = {Bpv / (4 * Mpv):.9f}")
    p("=> with a Lorentz-invariant cutoff the induced graviton moves at exactly c and the induced G is")
    p("   Sakharov's. With a cutoff that singles out a rest frame, c_g is off by O(1).")

    p.section("C. The substrate lattice itself (one scalar field, cell size a)")
    Ml, Bl = lattice_MB(0.0, [0, 0.05, 0.2, 0.6, 1.5, PI], 16)
    Ml2, Bl2 = lattice_MB(0.0, [0, 0.05, 0.2, 0.6, 1.5, PI], 24)
    cg2 = Bl / (4 * Ml)
    p(f"inertia M = {Ml:.5e}/a^2, stiffness beta = {Bl:.5e}/a^2 (24-point rule: {Ml2:.5e}, {Bl2:.5e})")
    p(f"=> c_g^2 = {cg2:.4f}: the induced graviton travels at {math.sqrt(cg2):.3f} c, {100 * (1 - math.sqrt(cg2)):.0f}% slower than light")
    p(f"   GW170817 allows {GW170817:.0e}: excluded by a factor ~{(1 - math.sqrt(cg2)) / GW170817:.0e}.")
    p("   (known in general: Collins, Perez, Sudarsky, Urrutia & Vucetich, PRL 93, 191301 (2004) -- a")
    p("    rest-frame cutoff leaks O(1) Lorentz violation into low energies; here for the graviton.)")
    for N in (1, 10, 100):
        aM = math.sqrt(16 * PI * N * Ml)
        aB = math.sqrt(4 * PI * N * Bl)
        p(f"   cell size that reproduces the measured G with N = {N:3d} scalar fields: a = {aM:.2f} l_P (from"
          f" inertia), {aB:.2f} l_P (from stiffness)")
    p("   -> Sakharov on a lattice puts the cells at about the Planck length (0.3 sqrt(N) l_P), but the")
    p("      two numbers disagree because the induced gravity is not Lorentz invariant.")

    p.section("D. Can the substrate protect c_g = c? A Lorentz-invariant cutoff below the cell scale")
    p("Add to the lattice two regulator fields of mass mu and sqrt2 mu with weights -2, +1 (the Pauli-")
    p("Villars pattern). They are FORMAL: negative weight means they are not ordinary particles. They")
    p("stand for any mechanism that cuts the fluctuations off Lorentz-invariantly at a scale mu below")
    p("the cell scale 1/a. (Ordinary fermions do not do this: they ADD to 1/G like ~2 scalars each.)")
    mus = np.array([0.8, 0.4, 0.2, 0.1, 0.05])
    dev, ratio = [], []
    for mu in mus:
        Mp, Bp = lattice_pv(mu)
        dev.append(Bp / (4 * Mp) - 1)
        ratio.append(Mp / (mu ** 2 * sak))
        p(f"   mu a = {mu:4.2f}: c_g^2 - 1 = {dev[-1]:+.3e},  M / Sakharov = {ratio[-1]:.4f}")
    dev = np.array(dev)
    fit = lambda x, K, C: K * x ** 2 * np.log(C / x)    # noqa: E731
    (K, C), _ = curve_fit(fit, mus[2:], -dev[2:], p0=(0.4, 2.0))
    p(f"   fit (mu a <= 0.2): c_g^2 - 1 = -{K:.3f} (mu a)^2 ln({C:.2f}/(mu a))  [the (scale ratio)^2")
    p("   suppression expected when Lorentz violation enters only through higher-dimension operators:")
    p("   Groot Nibbelink & Pospelov, PRL 94, 081601 (2005) (via supersymmetry); Polchinski, CQG 29,")
    p("   088001 (2012)]")
    need = brentq(lambda x: fit(x, K, C) - 2 * GW170817, 1e-14, 0.1)
    p(f"   GW170817 (|c_g^2 - 1| < {2 * GW170817:.0e}) needs mu a < {need:.1e} (extrapolating the fitted form")
    p("   from mu a = 0.05 down -- an assumption, not a computation, over those 6-7 decades)")
    for N in (1, 10, 100):
        mu_P = math.sqrt(6 * PI / (N * math.log(2)))
        p(f"   N = {N:3d}: measured G needs partner mass mu = {mu_P:.2f} m_P -> cells a < {need / mu_P:.1e} l_P")
    p("=> a substrate CAN induce gravity with c_g = c, but only if (i) something cuts its fluctuations")
    p("   off Lorentz-invariantly (what physical mechanism does this is OPEN), and (ii) its cells are")
    p("   ~10^7-10^8 times SMALLER than the Planck length. The Planck scale is then set by mu, not by")
    p("   the cell size, and the r10 lattice signatures (TeV photon delays) become unobservable.")

    p.section("Status")
    p("* computed here: Sakharov's G and the induced graviton speed on the substrate lattice;")
    p("  c_g = 0.72 c without protection (excluded); a Lorentz-invariant cutoff at mu restores c_g = c")
    p("  if mu a < 3e-8, i.e. cells far below the Planck length.")
    p("* limits: scalar fields only (fermions and gauge fields add with their own weights; gauge fields")
    p("  have Kabat contact-term subtleties); one polarisation and direction; the metric is put in as an")
    p("  external strain -- Sakharov explains its STIFFNESS, not why a metric variable exists (r12 does).")

    # ---------- figure
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
    names = ["substrate lattice\n(rest-frame cutoff)", "hard momentum\ncutoff", "Lorentz-invariant\nregulator (PV)"]
    vals = [math.sqrt(cg2), math.sqrt(Bh / (4 * Mh)), math.sqrt(Bpv / (4 * Mpv))]
    cols = [S2, S2, S1]
    y = np.arange(3)
    axs[0].barh(y, vals, color=cols, height=0.5)
    for yi, v in zip(y, vals):
        axs[0].text(v + 0.02, yi, f"{v:.3f} c", va="center", color=INK_2, fontsize=9)
    axs[0].axvline(1.0, color=MUTED, ls="--", lw=1.2)
    axs[0].text(0.985, 2.42, "GW170817:\nc ± 3×10⁻¹⁵", ha="right", va="bottom", fontsize=8.5, color=INK_2)
    axs[0].set(yticks=y, yticklabels=names, xlim=(0, 1.45), ylim=(-0.5, 3.0),
               xlabel="speed of the induced graviton (light = c)",
               title="Gravity induced by the substrate's jiggling:\nits waves travel at c only with a Lorentz-invariant cutoff")
    axs[0].grid(axis="y", visible=False)
    xx = np.logspace(math.log10(0.05), 0, 60)
    xe = np.logspace(-9, math.log10(0.05), 120)
    axs[1].loglog(mus, -dev, "o", color=S1, ms=7, label="lattice + PV regulator fields (computed)")
    axs[1].loglog(xx, fit(xx, K, C), color=S1, lw=1.3, alpha=0.7, label=f"fit {K:.2f}(μa)² ln({C:.1f}/μa)")
    axs[1].loglog(xe, fit(xe, K, C), color=S1, lw=1.3, alpha=0.7, ls=":", label="same fit, extrapolated")
    axs[1].axhline(2 * GW170817, color=S2, ls="--", lw=1.4, label="GW170817 limit")
    axs[1].axvline(need, color=MUTED, ls=":", lw=1.2)
    axs[1].text(need * 1.6, 1e-20, f"μa < {need:.0e}", color=INK_2, fontsize=9)
    axs[1].set(xlabel="regulator mass × cell size (μa)", ylabel="|c_g² − 1|", ylim=(1e-22, 1),
               title="A Lorentz-invariant cutoff μ restores c_g = c\nonly if μa < 3×10⁻⁸")
    axs[1].legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "graviton_speed")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
