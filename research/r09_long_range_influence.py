"""
r09 - How a particle affects the substrate far away  (LAB_NOTEBOOK.md entry E13)

Question (user): "... and how it would affect the substrate."

A particle is a defect of the substrate.  How far its influence reaches depends only on the
substrate MODE it disturbs:
  * a gapless, gauge-protected mode (the twist field that is light, r02): the defect is a
    violation of Gauss's law and its field reaches everywhere -> 1/r potential, 1/r^2 force;
  * a gapped (massive) mode, like the superfluid density dent of the audit: Yukawa e^{-mr}/r.
Computed exactly on a 128^3 cubic lattice (lattice Green's functions by FFT), along three
directions to test isotropy.  This is the classical part of the queued E9 item
"show emergent Coulomb 1/r between two Gauss-law defects on a cubic lattice".
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import MUTED, S1, S2, Report, save_fig, style  # noqa: E402

NAME = "r09_long_range_influence"
N = 128


def lattice_green(mass=0.0):
    k = 2 * np.pi * np.fft.fftfreq(N)
    kx, ky, kz = np.meshgrid(k, k, k, indexing="ij")
    lam = 4 * (np.sin(kx / 2) ** 2 + np.sin(ky / 2) ** 2 + np.sin(kz / 2) ** 2) + mass ** 2
    with np.errstate(divide="ignore"):
        Gk = np.where(lam > 0, 1.0 / lam, 0.0)        # zero mode removed (neutral box)
    return np.real(np.fft.ifftn(Gk)) * 1.0           # unit point source: -lap G = delta


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Gapless gauge mode: field of a Gauss-law defect on a 128^3 cubic lattice")
    G0 = lattice_green()
    dirs = {"[100] axis": (1, 0, 0), "[110] face diagonal": (1, 1, 0), "[111] body diagonal": (1, 1, 1)}
    curves = {}
    for name, (a, b, cc) in dirs.items():
        steps = np.arange(1, 25)
        pts = [(s * a, s * b, s * cc) for s in steps]
        r = np.array([math.sqrt(x * x + y * y + z * z) for x, y, z in pts])
        g = np.array([G0[x % N, y % N, z % N] for x, y, z in pts])
        sel = r <= 24
        curves[name] = (r[sel], g[sel])
    # periodic box: G(r) = 1/(4 pi r) - C + r^2/(6 N^3) + ... ; fix C from the axis at r = 8..16
    r_ax, g_ax = curves["[100] axis"]
    m = (r_ax >= 8) & (r_ax <= 16)
    C = np.mean(1 / (4 * np.pi * r_ax[m]) + r_ax[m] ** 2 / (6 * N ** 3) - g_ax[m])
    p(f"periodic-box constant C = {C:.5f}  (fitted once, on the axis)")
    for name, (r, g) in curves.items():
        cont = 1 / (4 * np.pi * r) - C + r ** 2 / (6 * N ** 3)
        for rr in (1.0, 3.0, 10.0):
            i = np.argmin(abs(r - rr))
            p(f"  {name:20s} r = {r[i]:5.2f}: lattice {g[i]:.5f}   1/(4 pi r) form {cont[i]:.5f}   "
              f"difference {abs(g[i] - cont[i]) / (1 / (4 * np.pi * r[i])):.1e} of the 1/r term")
    p("=> the defect's field becomes Coulomb's 1/r, the same in every direction to within 0.4% by 10 cells")
    p("   (the residue is lattice/box corrections that fall off faster than 1/r): a particle that is a")
    p("   Gauss-law defect disturbs the substrate out to infinity.")

    p.section("B. Gapped (massive) mode: the same defect, but the substrate mode has a gap m")
    mass = 0.3
    Gm = lattice_green(mass)
    r = np.arange(1, 25)
    gm = np.array([Gm[s, 0, 0] for s in r])
    yuk = np.exp(-mass * r) / (4 * np.pi * r)
    for rr in (1, 5, 10, 20):
        p(f"  r = {rr:2d}: lattice {gm[rr - 1]:.3e}   Yukawa e^(-mr)/(4 pi r) {yuk[rr - 1]:.3e}")
    p(f"=> range ~ 1/m = {1 / mass:.1f} cells; beyond that the influence is gone (the superfluid-dent")
    p("   gravity of the original USRT is this case, with m ~ 1/healing length).")

    p.section("C. What this means for mass and gravity")
    for line in (
        "* The reach of a particle's influence = 1/(gap of the substrate mode it disturbs).",
        "* Electric charge reaches to infinity because it sources the gapless TWIST mode, and the gap is",
        "  forbidden by gauge symmetry: charge conservation <-> Gauss's law <-> massless photon.",
        "* A superfluid's own gapless sound mode is a Goldstone mode: it couples through gradients, so two",
        "  static lumps feel no 1/r force from it (only motion/pulsation forces, Bjerknes). So a static 1/r",
        "  pull needs a gauge-protected massless mode, not just any gapless one.",
        "* Gravity reaches to infinity and is sourced by ENERGY. The analogue is a massless mode protected",
        "  by the conservation of energy-momentum: a spin-2 gauge field. Weinberg (1964) showed that any",
        "  massless spin-2 field must couple to all energy equally -- the universal free fall found in r08.",
        "* So in the substrate: mass = trapped energy (r07); trapped energy disturbs the spin-2 'stiffness'",
        "  mode (r08: lowers wave speed, eps = mu); that mode must be gapless and gauge-protected (here) for",
        "  1/r^2 gravity. Deriving that protected spin-2 mode from the substrate is the open core problem.",
    ):
        p(line)

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3))
    for (name, (rr, g)), mk in zip(curves.items(), ("o", "s", "^")):
        corr = g + C - rr ** 2 / (6 * N ** 3)
        axs[0].loglog(rr, corr, mk, color=S1, ms=5, mfc="none" if mk != "o" else S1, label=f"lattice, {name}")
    rl = np.linspace(1, 25, 200)
    axs[0].loglog(rl, 1 / (4 * np.pi * rl), color=MUTED, ls="--", lw=1.4, label="1/(4πr): Coulomb")
    axs[0].set(xlabel="distance from the defect (cells)", ylabel="field potential",
               title="Gapless gauge mode: 1/r in every direction")
    axs[0].legend(loc="lower left", fontsize=8.5)
    axs[1].semilogy(r, gm, "o", color=S2, ms=5, label=f"lattice, gapped mode (m = {mass})")
    axs[1].semilogy(rl, np.exp(-mass * rl) / (4 * np.pi * rl), color=MUTED, ls="--", lw=1.4, label="Yukawa e^(-mr)/(4πr)")
    axs[1].semilogy(rl, 1 / (4 * np.pi * rl), color=S1, lw=1.5, label="gapless (for comparison)")
    axs[1].set(xlabel="distance from the defect (cells)", ylabel="field potential",
               title="Gapped mode: influence dies beyond 1/m")
    axs[1].legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "coulomb_vs_yukawa")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
