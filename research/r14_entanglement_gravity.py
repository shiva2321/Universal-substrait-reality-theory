"""
r14 - Gravity from the substrate's entanglement: area law -> Bekenstein-Hawking -> G
(LAB_NOTEBOOK.md entry E19)

Questions (user): find the protected spin-2 mode "with field-established and out-of-the-box ways",
and "see if we can unify gravity and quantum mechanics, since they are one and the same thing,
just at a different scale".

The most direct field-established bridge between quantum mechanics and gravity:
  * the vacuum of ANY quantum field is entangled across any surface, and the entanglement
    entropy grows with the AREA, not the volume (Bombelli, Koul, Lee & Sorkin 1986; Srednicki 1993);
  * black holes carry entropy A/(4 l_P^2) (Bekenstein 1973, Hawking 1975);
  * Jacobson (1995): if every small patch of spacetime carries entropy eta x area, and heat flow
    obeys dQ = T dS (Unruh temperature), then Einstein's equations FOLLOW, with G = 1/(4 hbar eta).
    Entanglement equilibrium (Jacobson 2016) and Ryu-Takayanagi (2006) sharpen this.
So: compute eta for the substrate's vacuum, deduce the cell size that gives the measured G, and
compare with the completely different Sakharov route of r13 on the same lattice.

Method.  Free scalar field, ground state Gaussian: for a region A, the entanglement entropy follows
from the correlators X = <phi phi>, P = <pi pi> restricted to A: nu = eig sqrt(X_A P_A),
S = sum (nu+1/2) ln(nu+1/2) - (nu-1/2) ln(nu-1/2)   (Peschel / Srednicki).
  A. Srednicki's radial lattice (validation: he found S = 0.30 (R/a)^2).
  B. The cubic substrate lattice of r13, cubic regions of side l = 2..12 cells.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, Report, save_fig, style  # noqa: E402

NAME = "r14_entanglement_gravity"
SAK_M, SAK_B = 2.63231e-03, 5.43875e-03          # r13: lattice inertia and stiffness per scalar (1/a^2)


def entropy(nu):
    nu = nu[nu > 0.5 + 1e-12]
    return float(np.sum((nu + 0.5) * np.log(nu + 0.5) - (nu - 0.5) * np.log(nu - 0.5)))


def region_entropy(X, P):
    w, V = np.linalg.eigh(X)
    sX = (V * np.sqrt(np.clip(w, 0, None))) @ V.T
    C = sX @ P @ sX
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    return entropy(np.sqrt(np.clip(ev, 0.25, None)))


def srednicki(N=60, ns=(10, 14, 18, 22, 26, 30), lmax=6000):
    j = np.arange(1, N + 1)
    off = -(j[:-1] + 0.5) ** 2 / (j[:-1] * j[1:])
    S = np.zeros(len(ns))
    for ell in range(lmax + 1):
        K = np.diag(2 + 1 / (2 * j ** 2) + ell * (ell + 1) / j ** 2)
        K[0, 0] = 9 / 4 + ell * (ell + 1)
        K += np.diag(off, 1) + np.diag(off, -1)
        w, V = np.linalg.eigh(K)
        X = (V / (2 * np.sqrt(w))) @ V.T
        P = (V * np.sqrt(w) / 2) @ V.T
        for i, n in enumerate(ns):
            S[i] += (2 * ell + 1) * region_entropy(X[:n, :n], P[:n, :n])
    return np.array(ns) + 0.5, S


def cubic_correlators(L):
    """Ground-state <phi phi>, <pi pi> of the massless lattice scalar (antiperiodic box, no zero mode)."""
    k = 2 * np.pi * (np.arange(L) + 0.5) / L
    KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")
    om = np.sqrt(4 * (np.sin(KX / 2) ** 2 + np.sin(KY / 2) ** 2 + np.sin(KZ / 2) ** 2))
    r = np.arange(L)
    ph = np.exp(1j * np.pi * (r[:, None, None] + r[None, :, None] + r[None, None, :]) / L)
    return np.real(ph * np.fft.ifftn(1 / (2 * om))), np.real(ph * np.fft.ifftn(om / 2))


def cube_entropy(X, P, ell):
    c = np.array(np.meshgrid(*(np.arange(ell),) * 3, indexing="ij")).reshape(3, -1).T
    d = np.abs(c[:, None, :] - c[None, :, :])
    return region_entropy(X[d[..., 0], d[..., 1], d[..., 2]], P[d[..., 0], d[..., 1], d[..., 2]])


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Validation: Srednicki's radial lattice (60 shells, partial waves l <= 6000)")
    R, S = srednicki()
    ks = np.polyfit(R ** 2, S, 1)[0]
    for r_, s_ in zip(R, S):
        p(f"   sphere of radius {r_:5.1f} a: S = {s_:8.2f}   S/(R/a)^2 = {s_ / r_ ** 2:.4f}")
    p(f"fit S = kappa (R/a)^2 + const: kappa = {ks:.4f}   (Srednicki, PRL 71, 666 (1993): 0.30)")
    p("=> entanglement entropy grows like the AREA of the boundary, not the volume.")

    p.section("B. The cubic substrate lattice (same lattice as r13), cubes of side l")
    rows = {}
    for L in (48, 64):
        X, P = cubic_correlators(L)
        rows[L] = np.array([(ell, cube_entropy(X, P, ell)) for ell in range(2, 13)])
    ell, Sc = rows[64][:, 0], rows[64][:, 1]
    for e_, s_ in zip(ell, Sc):
        p(f"   cube {int(e_):2d}^3 cells: boundary {int(6 * e_ * e_):4d} a^2, S = {s_:7.3f}   S/boundary = {s_ / (6 * e_ * e_):.4f}")
    sel = ell >= 4
    A = np.vstack([6 * ell[sel] ** 2, ell[sel], np.ones(sel.sum())]).T
    kc, kedge, k0 = np.linalg.lstsq(A, Sc[sel], rcond=None)[0]
    A2 = np.vstack([6 * ell[sel] ** 2, ell[sel], np.log(ell[sel]), np.ones(sel.sum())]).T
    kc2 = np.linalg.lstsq(A2, Sc[sel], rcond=None)[0][0]
    kc48 = np.linalg.lstsq(A, rows[48][sel, 1], rcond=None)[0][0]
    p(f"fit S = eta_a (area/a^2) + b l + c (l >= 4): eta_a = {kc:.5f} per face of a cell"
      f"  (edges b = {kedge:+.4f})")
    p(f"   robustness: + log term {kc2:.5f};  box 48^3 {kc48:.5f};  radial lattice kappa/4pi = {ks / (4 * math.pi):.5f}")

    p.section("C. Jacobson / Bekenstein-Hawking: which cell size gives the measured G?")
    p("Bekenstein-Hawking: S = A / (4 l_P^2). Substrate with N scalar fields: S = N eta_a A / a^2.")
    p("Setting them equal (Jacobson 1995: then Einstein's equations follow): a = 2 sqrt(N eta_a) l_P.")
    a_ent = 2 * math.sqrt(kc)
    a_rad = 2 * math.sqrt(ks / (4 * math.pi))
    a_in = math.sqrt(16 * math.pi * SAK_M)
    a_st = math.sqrt(4 * math.pi * SAK_B)
    p(f"   entanglement, cubic lattice:   a = {a_ent:.3f} sqrt(N) l_P")
    p(f"   entanglement, radial lattice:  a = {a_rad:.3f} sqrt(N) l_P")
    p(f"   Sakharov (r13), from inertia:  a = {a_in:.3f} sqrt(N) l_P")
    p(f"   Sakharov (r13), from stiffness: a = {a_st:.3f} sqrt(N) l_P")
    p(f"=> two completely different quantum calculations -- how much the vacuum RESISTS straining")
    p(f"   (Sakharov) and how much it is ENTANGLED across a surface (Bekenstein-Hawking/Jacobson) --")
    p(f"   give the same cell size to within {100 * max(abs(a_in / a_ent - 1), abs(a_st / a_ent - 1)):.0f}%: cells of ~0.3 sqrt(N) Planck lengths.")
    p("   With a Lorentz-invariant cutoff the two agree EXACTLY: S_ent = A / (4 G_induced) (Susskind &")
    p("   Uglum 1994; Jacobson 1994). The lattice spread is the same rest-frame effect found in r13.")
    p(f"   (Noticed after the fact, one comparison tried: eta_a = {kc:.4f} is within"
      f" {100 * abs(kc / math.sqrt(4 * math.pi * SAK_M * math.pi * SAK_B) - 1):.0f}% of the geometric mean")
    p("    of the two Sakharov values of 1/(4G). Possibly a coincidence; not derived.)")
    for N in (1, 10, 100):
        p(f"   N = {N:3d} fields: a = {a_ent * math.sqrt(N):.2f} l_P = {a_ent * math.sqrt(N) * 1.616255e-35:.1e} m")

    p.section("D. What this says about 'gravity and quantum mechanics are one thing at different scales'")
    for line in (
        "* Gravity's strength G is NOT an independent constant here. It is fixed by quantum quantities of",
        "  the substrate: the number of fields N, the cell size a, and hbar:  G ~ a^2 c^3 / (4 N eta_a hbar).",
        "  The Planck length l_P = sqrt(hbar G / c^3) is then ~3.2 x (cell size) / sqrt(N).",
        "* Black-hole entropy A/4 l_P^2 becomes the entanglement of the substrate across the horizon,",
        "  counted with the same fields that set G: one consistent quantum origin for both.",
        "* Einstein's equations become an equation of state: the thermodynamics of substrate entanglement",
        "  (Jacobson 1995). Gravity is then quantum mechanics of the substrate seen at large scales,",
        "  like elasticity is the quantum mechanics of atoms seen at large scales.",
        "* What this does NOT give: the graviton's quantum dynamics at the Planck scale, and why the",
        "  emergent equations are exactly Einstein's (Lorentz invariance again: r12, r13).",
    ):
        p(line)

    # ---------- figure
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
    area = 6 * ell ** 2
    axs[0].plot(area, Sc, "o", color=S1, ms=6, label="cubic substrate lattice (computed)")
    aa = np.linspace(0, area.max() * 1.05, 100)
    ll = np.sqrt(aa / 6)
    axs[0].plot(aa, kc * aa + kedge * ll + k0, color=S1, lw=1.2, alpha=0.6,
                label=f"area law: {kc:.4f} × area + edge term")
    vol = ell ** 3
    axs[0].plot(area, Sc[-1] * vol / vol[-1], "s", color=MUTED, ms=5, mfc="none",
                label="what a volume law would look like")
    axs[0].set(xlabel="boundary area of the region (cell faces)", ylabel="entanglement entropy S (nats)",
               title="The substrate vacuum is entangled across every surface,\nin proportion to its area")
    axs[0].legend(loc="upper left", fontsize=8.5)
    names = ["Sakharov:\nstiffness (r13)", "entanglement:\ncubic lattice", "entanglement:\nradial lattice",
             "Sakharov:\ninertia (r13)"]
    vals = [a_st, a_ent, a_rad, a_in]
    cols = [S2, S1, S1, S2]
    y = np.arange(4)
    axs[1].barh(y, vals, color=cols, height=0.5)
    for yi, v in zip(y, vals):
        axs[1].text(v + 0.008, yi, f"{v:.3f}", va="center", color=INK_2, fontsize=9)
    axs[1].set(yticks=y, yticklabels=names, xlim=(0, 0.45),
               xlabel="cell size that gives the measured G, in units of √N Planck lengths",
               title="Two quantum routes to Newton's G agree\non the substrate cell size to within 17%")
    axs[1].grid(axis="y", visible=False)
    fig.tight_layout()
    save_fig(fig, NAME, "area_law")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
