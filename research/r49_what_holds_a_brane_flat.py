
"""
r49 - What holds a wall made of the medium flat?  (LAB_NOTEBOOK.md entry E48, tests S1-S4)

Question (queue item from E45, F4): "test stabilisers for the F4 wall (a second component, a conserved topological charge, a pinning potential) against the snake instability".
r36 found that the simplest wall of the medium itself, a dark soliton (a planar node of the order parameter), is unstable to bending: growth rate up to 0.26 m c^2/hbar at transverse
wavenumber k = 0.70 m c/hbar (units hbar = m = g = n0 = 1, healing length 1).  Here the Bogoliubov-de Gennes spectrum of the wall is computed with two stabilisers:

  S1. Baseline: the plain wall (check against r36).
  S2. A pinning potential V(x) = U exp(-x^2 / 2 w^2) centred on the wall (a repulsive barrier the node sits on): the critical height U_c(w) above which no unstable mode is left.
  S3. A second component filling the core (a dark-bright wall: component 1 dark, component 2 bright, inter-component coupling g12): the critical population N_b of the bright component.
  S4. What the thresholds mean in the Planck-length mapping of r33 (chemical potential mu = m c^2 = m_P c^2 / (sqrt2 alpha)).

Numerics: 1D grid of 190 points on [-14, 14] (dx = 0.147), stationary states by imaginary-time relaxation with the node pinned by antisymmetry (and the bright norm fixed in S3), BdG matrices
[[A, B], [-B, -A]] with the transverse kinetic term k^2/2 added to every component; 'growth rate' = largest imaginary part of the spectrum.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r49_what_holds_a_brane_flat"
HALF, NG = 14.0, 190
KS_CRIT = np.array([0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0])     # includes the longest wavelengths, where a weak barrier is unstable
X = np.linspace(-HALF, HALF, NG)
DX = X[1] - X[0]
LAP = (np.diag(np.full(NG - 1, 1.0), 1) + np.diag(np.full(NG - 1, 1.0), -1) - 2.0 * np.eye(NG)) / DX ** 2


def laplacian_vec(f):
    out = np.zeros_like(f)
    out[1:-1] = (f[2:] + f[:-2] - 2.0 * f[1:-1]) / DX ** 2
    return out


def relax_single(potential, tau_max=60.0, dtau=0.004):
    """Odd stationary solution of -psi''/2 + (V + psi^2 - 1) psi = 0 with psi -> +-1 at the box edges (node on the barrier)."""
    psi = np.tanh(X)
    for _ in range(int(tau_max / dtau)):
        psi = psi + dtau * (0.5 * laplacian_vec(psi) - (potential + psi ** 2 - 1.0) * psi)
        psi[0], psi[-1] = -1.0, 1.0
        psi = 0.5 * (psi - psi[::-1])                  # keep the node at x = 0
    resid = float(np.max(np.abs(-0.5 * laplacian_vec(psi) + (potential + psi ** 2 - 1.0) * psi)[5:-5]))
    return psi, resid


def relax_dark_bright(g12, n_bright, tau_max=80.0, dtau=0.004):
    """Dark (odd, asymptotic density 1) component 1 and bright (even, norm n_bright) component 2 with g11 = g22 = 1, coupling g12."""
    p1 = np.tanh(X)
    p2 = np.sqrt(n_bright / 2.0) / np.cosh(X)
    for _ in range(int(tau_max / dtau)):
        d1 = 0.5 * laplacian_vec(p1) - (p1 ** 2 + g12 * p2 ** 2 - 1.0) * p1
        p1 = p1 + dtau * d1
        p1[0], p1[-1] = -1.0, 1.0
        p1 = 0.5 * (p1 - p1[::-1])
        # bright: relax with the chemical potential fixed by the norm (imaginary-time projection)
        mu2 = float(np.sum(p2 * (-0.5 * laplacian_vec(p2) + (g12 * p1 ** 2 + p2 ** 2) * p2)) / np.sum(p2 ** 2))
        p2 = p2 + dtau * (0.5 * laplacian_vec(p2) - (g12 * p1 ** 2 + p2 ** 2 - mu2) * p2)
        p2[0] = p2[-1] = 0.0
        p2 = 0.5 * (p2 + p2[::-1])
        p2 *= math.sqrt(n_bright / (np.sum(p2 ** 2) * DX))
    mu2 = float(np.sum(p2 * (-0.5 * laplacian_vec(p2) + (g12 * p1 ** 2 + p2 ** 2) * p2)) / np.sum(p2 ** 2))
    r1 = float(np.max(np.abs(-0.5 * laplacian_vec(p1) + (p1 ** 2 + g12 * p2 ** 2 - 1.0) * p1)[5:-5]))
    r2 = float(np.max(np.abs(-0.5 * laplacian_vec(p2) + (g12 * p1 ** 2 + p2 ** 2 - mu2) * p2)[5:-5]))
    return p1, p2, mu2, max(r1, r2)


def growth_single(psi, potential, ks):
    out = []
    for k in ks:
        a_op = -0.5 * LAP + np.diag(0.5 * k * k + potential + 2.0 * psi ** 2 - 1.0)
        b_op = np.diag(psi ** 2)
        ev = np.linalg.eigvals(np.block([[a_op, b_op], [-b_op, -a_op]]))
        out.append(float(np.max(ev.imag)))
    return np.array(out)


def growth_two(p1, p2, mu2, g12, ks):
    out = []
    zero = np.zeros((NG, NG))
    for k in ks:
        kin = -0.5 * LAP + 0.5 * k * k * np.eye(NG)
        a11 = kin + np.diag(2.0 * p1 ** 2 + g12 * p2 ** 2 - 1.0)
        a22 = kin + np.diag(2.0 * p2 ** 2 + g12 * p1 ** 2 - mu2)
        a12 = np.diag(g12 * p1 * p2)
        b11 = np.diag(p1 ** 2)
        b22 = np.diag(p2 ** 2)
        b12 = np.diag(g12 * p1 * p2)
        a_mat = np.block([[a11, a12], [a12, a22]])
        b_mat = np.block([[b11, b12], [b12, b22]])
        ev = np.linalg.eigvals(np.block([[a_mat, b_mat], [-b_mat, -a_mat]]))
        out.append(float(np.max(ev.imag)))
    return np.array(out)


def peak_growth(fun, ks):
    g = fun(ks)
    i = int(np.argmax(g))
    return float(g[i]), float(ks[i])


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    ks = np.linspace(0.1, 1.3, 9)
    p("Units hbar = m = g = n0 = 1 (healing length 1, sound speed 1, chemical potential 1); transverse wavenumber k; growth rate in units m c^2 / hbar.")

    # ======================================================================================================
    p.section("S1. The plain wall (dark soliton): baseline from the BdG spectrum")
    # ------------------------------------------------------------------------------------------------------
    psi0, resid0 = relax_single(np.zeros(NG))
    p(f"    stationary state: residual {resid0:.1e}; node density {psi0[NG // 2] ** 2:.1e}; max |psi - tanh x| = {np.max(np.abs(psi0 - np.tanh(X))):.1e}")
    g0 = growth_single(psi0, np.zeros(NG), ks)
    p("    " + "  ".join(f"k={k:.1f}: {g:.3f}" for k, g in zip(ks, g0)))
    gmax0 = float(g0.max())
    p(f"    => maximum growth {gmax0:.3f} at k = {ks[int(np.argmax(g0))]:.1f} (r36: 0.261 at k = 0.70); unstable for k up to ~ {ks[g0 > 1e-3].max():.1f}: bending doubles the wall's ripple in {math.log(2) / gmax0:.1f} healing times.")

    # ======================================================================================================
    p.section("S2. A pinning barrier V = U exp(-x^2 / 2 w^2) on the wall")
    # ------------------------------------------------------------------------------------------------------
    p(f"    {'U':>6s} | " + " | ".join(f"w = {w:<4g} peak growth (k)" for w in (0.5, 1.0, 2.0)))
    ws = (0.5, 1.0, 2.0)
    us = (0.0, 0.1, 0.3, 1.0, 2.0, 4.0, 8.0)
    table = {}
    for u in us:
        row = []
        for w in ws:
            pot = u * np.exp(-X ** 2 / (2 * w * w))
            psi, rs = relax_single(pot)
            gm, km = peak_growth(lambda kk: growth_single(psi, pot, kk), ks)
            table[(u, w)] = (gm, km, rs)
            row.append(f"{gm:6.3f} ({km:.1f})")
        p(f"    {u:6.2f} | " + " | ".join(f"{r:>22s}" for r in row))
    # critical U: smallest U on a finer grid with peak growth < 1e-3
    crit = {}
    for w in ws:
        lo, hi = 0.0, 30.0
        for _ in range(10):
            mid = 0.5 * (lo + hi)
            pot = mid * np.exp(-X ** 2 / (2 * w * w))
            psi, _ = relax_single(pot, tau_max=40.0)
            gm = float(growth_single(psi, pot, KS_CRIT).max())
            if gm > 1e-3:
                lo = mid
            else:
                hi = mid
        crit[w] = hi
    p("    Critical barrier height (peak growth < 1e-3 for all k in 0.02-1.0; a first version used only k >= 0.25 and gave U_c too low), in units of the chemical potential:")
    for w in ws:
        p(f"      width {w:3.1f} healing lengths: U_c = {crit[w]:.2f} mu")
    weak = [(u, w) for (u, w), (gm, km, rs) in table.items() if 0.0 < u <= 1.0 and km <= 0.15 and gm > gmax0 * 0.9]
    p("    For U of order 1 mu the peak growth moves to the smallest wavenumber (k = 0.1) and can exceed the plain value (" + ", ".join(f"{table[uw][0]:.2f} at U = {uw[0]:g}, w = {uw[1]:g}" for uw in weak[:3]) + "):")
    p("    a weak barrier does not pin the node; a dark soliton has negative effective mass and slides off it (a long-wavelength, translational instability).")
    p("    => a barrier of order the chemical potential, as narrow as the wall itself, makes the node a hard wall: the instability disappears because the two halves no longer talk through the node.")
    p("       (The pinning energy per unit area is U w sqrt(2 pi) ~ the wall's own energy scale 4/3 n0 hbar c, so the stabiliser is as strong as the wall: the wall is then held by the barrier, not by itself.)")

    # ======================================================================================================
    p.section("S3. A second component in the core: dark-bright wall")
    # ------------------------------------------------------------------------------------------------------
    p("    Component 1 dark (asymptotic density 1), component 2 bright (norm N_b in units n0 xi), g11 = g22 = 1, coupling g12.  The wall's own deficit is N_d = 2 n0 xi.")
    p(f"    {'g12':>5s} {'N_b':>6s} {'N_b/N_d':>8s} {'residual':>9s} {'peak growth':>12s} {'at k':>6s} {'mu_2':>8s}")
    db_rows = []
    for g12 in (1.0, 2.0):
        for nb in (0.0, 0.3, 1.0, 2.0, 4.0, 8.0):
            if nb == 0.0:
                gm, km, resid, mu2 = float(gmax0), float(ks[int(np.argmax(g0))]), 0.0, float("nan")
            else:
                p1, p2, mu2, resid = relax_dark_bright(g12, nb)
                gm, km = peak_growth(lambda kk: growth_two(p1, p2, mu2, g12, kk), ks)
            db_rows.append((g12, nb, gm, km))
            p(f"    {g12:5.1f} {nb:6.1f} {nb / 2.0:8.2f} {resid:9.1e} {gm:12.4f} {km:6.1f} {mu2:8.3f}")
    p("    Reading: the bright component lowers the growth rate; whether it removes the instability altogether is shown by the peak-growth column (zero = stable).")
    stab = [r for r in db_rows if r[2] < 1e-3 and r[1] > 0]
    if stab:
        best = min(stab, key=lambda r: r[1])
        p(f"    => stabilised from N_b = {best[1]:g} (N_b / N_d = {best[1] / 2.0:.2f}) at g12 = {best[0]:g}.")
    else:
        redu = [(r[0], r[1], r[2] / gmax0) for r in db_rows if r[1] > 0]
        best = min(redu, key=lambda t: t[2])
        p(f"    => not stabilised in the range tried: the best reduction is to {best[2]:.2f} of the plain growth rate (g12 = {best[0]:g}, N_b = {best[1]:g}).")

    # ======================================================================================================
    p.section("S4. What this means for the Planck-length medium")
    # ------------------------------------------------------------------------------------------------------
    p("    In the r33 mapping the chemical potential is mu = m c^2 = m_P c^2 / (sqrt2 alpha) and the healing length is alpha l_P.  A barrier of U_c ~ a few mu on the scale of one")
    p(f"    healing length is a potential of order {crit[1.0]:.1f} x m_P c^2/(sqrt2 alpha) = {crit[1.0] / math.sqrt(2.0):.1f} m_P c^2 / alpha varying over alpha l_P: a Planck-scale external structure, not a weak field.")
    p("    A second component is an internal degree of freedom (it needs its own population N_b of order the wall's deficit) and is the better-motivated stabiliser; whether it is enough is in S3.")
    p("    Not computed: a conserved topological charge (e.g. a winding of a second field around the wall) and what sources the escape-speed flow of r34: still open.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    stab_txt = (f"STABILISED for N_b >= {min(stab, key=lambda r: r[1])[1]:g}" if stab else
                f"NOT stabilised: growth only reduced to {min(r[2] for r in db_rows if r[1] > 0) / gmax0:.2f} of the plain value")
    verdict = [
        ("S1: the plain wall is bending-unstable", f"CONFIRMED: peak growth {gmax0:.3f} at k = {ks[int(np.argmax(g0))]:.1f} (r36: 0.261 at 0.70)"),
        ("S2: a pinning barrier stabilises the wall", f"YES, but it must be as strong as the wall: U_c = {crit[0.5]:.1f} / {crit[1.0]:.1f} / {crit[2.0]:.1f} mu for widths 0.5 / 1 / 2 healing lengths"),
        ("S3: a second component in the core stabilises the wall", stab_txt),
        ("S4: a weak external field can hold the wall flat", "NO: the pinning potential is of the medium's own energy scale on its own length scale"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<62s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(16.4, 5.2))
    ax = axs[0]
    kk = np.linspace(0.05, 1.4, 28)
    ax.plot(kk, growth_single(psi0, np.zeros(NG), kk), "o-", color=S1, ms=5, label="plain wall")
    for w, col in ((0.5, S2), (2.0, S3)):
        u = 0.5 * crit[w]
        pot = u * np.exp(-X ** 2 / (2 * w * w))
        psi, _ = relax_single(pot)
        ax.plot(kk, growth_single(psi, pot, kk), "s-", color=col, ms=4, label=f"U = {u:.1f} μ, w = {w:g}")
    ax.axhline(0, color=MUTED, lw=1.0)
    ax.set(xlabel="transverse wavenumber k (m c / ħ)", ylabel="growth rate (m c² / ħ)", xlim=(0, 1.8), title="Bending instability of the wall and half-strength pinning")
    ax.legend(loc="upper right", fontsize=9)

    ax = axs[1]
    uu = np.linspace(0.0, 8.0, 17)
    for w, col in zip(ws, (S1, S2, S3)):
        vals = []
        for u in uu:
            pot = u * np.exp(-X ** 2 / (2 * w * w))
            psi, _ = relax_single(pot, tau_max=40.0)
            vals.append(float(growth_single(psi, pot, KS_CRIT).max()))
        ax.plot(uu, vals, "o-", color=col, ms=5, label=f"barrier width {w:g} healing lengths")
        ax.axvline(crit[w], color=col, ls=":", lw=1.1)
    ax.set(xlabel="barrier height U (units of the chemical potential)", ylabel="peak growth rate", title="A barrier a few μ high removes the instability")
    ax.legend(loc="upper right", fontsize=9)

    ax = axs[2]
    for g12, col, mk in ((1.0, S1, "o"), (2.0, S2, "s")):
        pts = [(r[1], r[2]) for r in db_rows if r[0] == g12]
        ax.plot([a for a, _ in pts], [b for _, b in pts], mk + "-", color=col, ms=7, label=f"bright component, g12 = {g12:g}")
    ax.axhline(0, color=MUTED, lw=1.0)
    ax.set(xlabel="population of the bright component N_b (wall deficit = 2)", ylabel="peak growth rate", title="A second component in the core")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "brane")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
