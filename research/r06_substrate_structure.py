"""
r06 - The structure of the substrate after the audit and research entries E1-E8
(2026-10-10, LAB_NOTEBOOK.md entry E10).

Question (user): "So what's the structure of the substrate based on the improvements and
modifications to the Universal Substrate Theory?"

This script does not introduce new physics.  It collects what E1-E8 established into one
layered picture ("USRT v2"), and computes the parameter ranges that the measurements
already allow:
  * cell size a: from the Planck length up to the dispersion bound (r03);
  * coupling J and tick tau that make the lattice speed limit equal c (r05: c = 2 J a / hbar);
  * the gauge coupling: our alpha vs the confinement threshold of the simplest lattice gauge
    substrate (compact U(1), Wilson action, beta_c = 1.0111; Arnold et al. 2003);
  * vacuum energy: Volovik's equilibrium value (0) vs the observed dark-energy density.
It also draws the layer diagram.
"""
import math
import os
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import ALPHA, G0, INK, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r06_substrate_structure"
Mpc = 3.0857e22


def main():
    p = Report(NAME)
    style(plt)

    p.section("1. Cell size, coupling and tick of the substrate (allowed ranges)")
    a_max = hbar * c / (1e11 * 1e9 * eV)          # order-2 dispersion bound, r03
    cases = (("Planck length", lP()),
             ("induced gravity, N = 100 fields (a ~ sqrt(N) l_P)", 10 * lP()),
             ("largest allowed by order-2 dispersion bound", a_max))
    p(f"{'cell size a':52s} {'a (m)':>10} {'coupling J = hbar c/2a':>24} {'tick a/c (s)':>14}")
    for label, a in cases:
        J = hbar * c / (2 * a)
        p(f"{label:52s} {a:10.2e} {J / (1e9 * eV):17.2e} GeV {a / c:14.2e}")
    p("A twist-only (gauge) lattice is symmetric under k -> -k, so its leading dispersion is order 2")
    p("and both polarisations stay degenerate at every k (r02): no vacuum birefringence. Data therefore")
    p(f"allow cells up to ~{a_max:.0e} m; gravity's strength (Sakharov) points to a few Planck lengths.")
    R_obs = 4.4e26
    p(f"cells in the observable universe if a = l_P: (R/a)^3 = {(R_obs / lP()) ** 3:.1e}")

    p.section("2. Is the substrate in the phase that has photons? (Coulomb vs confined)")
    beta_c = 1.0111331                              # 4D compact U(1), Wilson action, first-order transition
    alpha_c = 1 / (4 * math.pi * beta_c)
    alpha_mz = 1 / 127.951                          # PDG 2024, alpha at the Z mass (MS-bar)
    p(f"simplest lattice gauge substrate (compact U(1), Wilson action): photons exist only for")
    p(f"  beta = 1/e^2 > {beta_c:.4f}, i.e. alpha = e^2/(4 pi) < alpha_c = {alpha_c:.4f}  (about 1/{1 / alpha_c:.1f})")
    p(f"our alpha(0) = 1/{1 / ALPHA:.3f} is {alpha_c / ALPHA:.1f}x below the threshold; alpha(M_Z) = 1/{1 / alpha_mz:.2f} "
      f"is {alpha_c / alpha_mz:.1f}x below")
    p("=> the substrate must sit in its Coulomb (deconfined) phase, comfortably. Quantum spin ice's emergent")
    p("   alpha ~ 0.08 (Pace et al. 2021) sits right at that threshold; ours is an order of magnitude weaker.")
    p("   Why 1/137 exactly is still open.")

    p.section("3. Vacuum energy")
    H0 = 67.36e3 / Mpc
    rho_crit = 3 * H0 ** 2 / (8 * math.pi * G0)
    rho_L = 0.6847 * rho_crit
    rho_P = c ** 5 / (hbar * G0 ** 2)
    p(f"observed dark-energy density (Planck 2018): {rho_L:.2e} kg/m^3 = {rho_L * c * c:.2e} J/m^3")
    p(f"Planck density c^5/(hbar G^2): {rho_P:.2e} kg/m^3 -> ratio {rho_L / rho_P:.1e}")
    p("Volovik (Gibbs-Duhem): a substrate in equilibrium has zero vacuum pressure, so the naive 1e120 term")
    p("is absent. The small observed value then has to come from the universe being slightly out of")
    p("equilibrium; its size is still an input, not derived.")

    p.section("4. The layers (USRT v2) and their status")
    layers = (
        ("6  Extra dimension (optional)", "curled up or warped (RS2 bulk is no shortcut); entanglement needs an "
         "instant, non-signalling link (ER = EPR-like)", "open", "E3, E7"),
        ("5  Gravity", "a collective METRIC shared by every excitation: spin-2, infinite range, stiffness "
         "c^4/8piG = 4.8e42 N (not a density dent)", "open", "E3, E6"),
        ("4  Matter", "defects of the condensate: string ends = charges (can be fermions), Weyl points "
         "(massless by topology), trapped ripples (mass = confined energy, obey relativity); mass VALUES not derived",
         "computed here", "E4, E5"),
        ("3  Light", "the twist of the loop condensate: exactly 2 polarisations, isotropic on a cubic lattice, "
         "massless by gauge symmetry, strength alpha", "computed here", "E5, E6"),
        ("2  Vacuum state", "a frictionless condensate of closed flux loops (string-net), in its Coulomb phase "
         "(alpha < 0.079); equilibrium pressure zero", "established", "E5, r06"),
        ("1  Couplings", "each unit coupled only to its neighbours (energy J): built-in speed limit "
         "c = 2Ja/hbar, one cell per tick", "computed here", "E8"),
        ("0  Units", "uncharged quantum units (spins/rotors, not hard balls) on a cubic lattice or no fixed "
         "lattice; cell between the Planck length and ~2e-27 m", "open", "E5, r06"),
    )
    for name, body, status, src in layers:
        p(f"  {name:30s} [{status}] ({src})")
        p(f"  {'':30s} {body}")

    # ---------------- diagram
    colours = {"established": S3, "computed here": S1, "open": S2}
    fig = plt.figure(figsize=(15, 9.2))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.2)
    ax.axis("off")
    ax.text(0.35, 8.85, "Structure of the substrate after the audit and research (USRT v2)",
            fontsize=15, fontweight="bold", color=INK, va="center")
    ax.text(0.35, 8.47, "Each layer emerges from the one below it. Colour = how well it is supported. "
            "Time = the substrate's own ticks (relational, Page–Wootters).", fontsize=10, color=INK_2, va="center")
    x0, w, h, gap, ytop = 0.35, 9.6, 0.88, 0.16, 7.95
    for i, (name, body, status, src) in enumerate(layers):
        y = ytop - (i + 1) * h - i * gap
        col = colours[status]
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=col + "1f", ec=col, lw=1.8))
        ax.text(x0 + 0.18, y + h - 0.24, name, fontsize=11.5, fontweight="bold", color=INK, va="center")
        ax.text(x0 + w - 0.15, y + h - 0.24, f"{status}  ·  {src}", fontsize=9, color=col, va="center",
                ha="right", fontweight="bold")
        ax.text(x0 + 0.18, y + 0.32, textwrap.fill(body, 118), fontsize=9.2, color=INK_2, va="center",
                linespacing=1.35)
        if i < len(layers) - 1:
            ax.add_patch(FancyArrowPatch((x0 + w / 2, y - gap + 0.02), (x0 + w / 2, y - 0.02),
                                         arrowstyle="-|>", mutation_scale=12, color=MUTED, lw=1.2))
    # side panel: what was dropped
    sx, sw = 10.35, 4.3
    ax.add_patch(FancyBboxPatch((sx, 3.25), sw, 4.7, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#f1f0ec", ec=MUTED, lw=1.2))
    ax.text(sx + 0.2, 7.62, "Dropped from the original USRT", fontsize=11.5, fontweight="bold", color=INK)
    dropped = ("Planck-mass balls joined by springs", "close-packed HCP crystal", "light = elastic shear wave",
               "the 4.2e19 GeV 'gap'", "gravity = density dent (cavity)", "electron, proton, muon formulas",
               "local vortex entanglement", "c 'derived' from hbar and G")
    for j, item in enumerate(dropped):
        ax.text(sx + 0.25, 7.18 - j * 0.48, "–  " + item, fontsize=9.6, color=INK_2)
    # side panel: kept / numbers
    ax.add_patch(FancyBboxPatch((sx, 0.83), sw, 2.22, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#f1f0ec", ec=MUTED, lw=1.2))
    ax.text(sx + 0.2, 2.75, "Inputs it still needs (measured)", fontsize=11.5, fontweight="bold", color=INK)
    for j, item in enumerate(("c = 299,792,458 m/s  (fixes J·a)", "alpha = 1/137.036  (gauge strength)",
                              "G  (gravity stiffness c^4/8piG)", "dark-energy density  (~1e-123 Planck)")):
        ax.text(sx + 0.25, 2.33 - j * 0.42, "–  " + item, fontsize=9.6, color=INK_2)
    # legend + time note
    for k, (lab, col) in enumerate(colours.items()):
        ax.add_patch(FancyBboxPatch((0.4 + k * 2.6, 0.18), 0.32, 0.22, boxstyle="round,pad=0.01",
                                    fc=col + "1f", ec=col, lw=1.5))
        ax.text(0.82 + k * 2.6, 0.29, lab, fontsize=9.5, color=INK_2, va="center")
    save_fig(fig, NAME, "layers")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
