"""
r36 - A hyper-dimensional medium and 3D observers: forces, the horizon problem, and the brane itself
(LAB_NOTEBOOK.md entry E45, test F4)

Question (user): "its a super fluide like matter ... in hyper dimentionas and we as an observers can only see and interact in 3d".
Three things follow from putting the medium in 4 space dimensions with observers on a 3D slice (a brane):

  A. FORCES.  A massless mode of the medium (a phonon / phase mode) mediates a static force between sources.  In D space
     dimensions its potential goes as r^-(D-2): 1/r in 3D, 1/r^2 in 4D.  If the extra direction is a circle of circumference L, the
     brane potential is the image sum  V(r) = (G/r) coth(pi r / L) = (G/r)(1 + 2 sum_n exp(-2 pi n r / L)):  a 3D 1/r law plus a
     tower of Yukawa terms with masses 2 pi n hbar / (L c).  Torsion balances test 1/r down to ~50 micrometres.
  B. HORIZON PROBLEM.  Opposite points of the last-scattering sphere were never in causal contact through light signals before
     recombination.  A bulk signal could connect them if it is fast enough.  How fast?
  C. THE BRANE.  The simplest brane made from the medium itself is a domain wall, a dark soliton psi0 = sqrt(n0) tanh(x / sqrt(2) xi)
     (= tanh(x) in units hbar = m = g = n0 = 1, where c = 1 and xi = 1/sqrt 2).
     Is it stable against bending?  The Bogoliubov-de Gennes equations for a perturbation with transverse wavenumber k are
         omega u = [ -d^2/2dx^2 + k^2/2 + 2 psi0^2 - 1 ] u + psi0^2 v ,   -omega v = [ same ] v + psi0^2 u
     (units hbar = m = g = n0 = 1); an eigenvalue with positive imaginary part means exponential growth (the snake instability).
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r36_hyperdimensional_medium"
UM = 1e-6
R_TESTED = 52 * UM               # shortest distance at which gravity has been tested (torsion balance, Eot-Wash)
DEV_ALLOWED = 0.25               # typed, from memory: deviations of order 25 % at that distance are already excluded

H_PLANCK, OM, ORH2 = 0.6736, 0.3153, 4.18e-5     # Planck 2018
OR_ = ORH2 / H_PLANCK ** 2
OL = 1.0 - OM - OR_
Z_STAR = 1089.92
C_OVER_H0_GPC = 299792.458 / (100.0 * H_PLANCK) / 1000.0


def coth_strength(r_over_l):
    """V r / G = coth(pi r / L): strength of the brane force relative to the 3D 1/r law."""
    return 1.0 / np.tanh(np.pi * np.asarray(r_over_l, float))


def image_sum_strength(r_over_l, n_images=200000):
    """Same quantity from the explicit sum over images of the 4D potential, (L/pi) r sum_n 1 / (r^2 + n^2 L^2)."""
    n = np.arange(-n_images, n_images + 1)
    return (1.0 / math.pi) * r_over_l * np.sum(1.0 / (r_over_l ** 2 + n ** 2))


def conformal_time_integral(a_lo, a_hi):
    """int da / (a^2 H) in units of c / H0 (flat LCDM with radiation)."""
    f = lambda a: 1.0 / math.sqrt(OR_ + OM * a + OL * a ** 4)
    return quad(f, a_lo, a_hi, epsabs=1e-13, epsrel=1e-12)[0]


def bdg_growth_rate(k, half_box=16.0, n_grid=360):
    """Largest imaginary part of the BdG spectrum of the dark soliton for transverse wavenumber k (units hbar = m = g = n0 = 1)."""
    x = np.linspace(-half_box, half_box, n_grid)
    dx = x[1] - x[0]
    psi0_sq = np.tanh(x) ** 2          # stationary dark soliton: -psi''/2 + psi^3 - psi = 0 for psi = tanh(x)
    lap = (np.diag(np.full(n_grid - 1, 1.0), 1) + np.diag(np.full(n_grid - 1, 1.0), -1) - 2.0 * np.eye(n_grid)) / dx ** 2
    a_op = -0.5 * lap + np.diag(0.5 * k * k + 2.0 * psi0_sq - 1.0)
    b_op = np.diag(psi0_sq)
    big = np.block([[a_op, b_op], [-b_op, -a_op]])
    ev = np.linalg.eigvals(big)
    return float(np.max(ev.imag)), ev


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. Forces on the brane from a massless mode that lives in a compact extra dimension")
    # ------------------------------------------------------------------------------------------------------
    p("Check of the closed form against the explicit image sum (200,001 images): V r / G = coth(pi r / L)")
    worst = 0.0
    p(f"    {'r / L':>8s} {'coth formula':>13s} {'image sum':>12s} {'difference':>11s}")
    for x in (0.01, 0.1, 0.3, 1.0, 3.0):
        a, b = float(coth_strength(x)), image_sum_strength(x)
        worst = max(worst, abs(a - b) / a)
        p(f"    {x:8.2f} {a:13.6f} {b:12.6f} {abs(a - b):11.1e}")
    slope_small = (math.log(coth_strength(0.0101) / 0.0101) - math.log(coth_strength(0.0099) / 0.0099)) / math.log(0.0101 / 0.0099)
    slope_large = (math.log(coth_strength(101.0) / 101.0) - math.log(coth_strength(99.0) / 99.0)) / math.log(101.0 / 99.0)
    p(f"Local power law of V(r) = (G/r) coth(pi r/L):  d ln V / d ln r = {slope_small:.3f} at r = 0.01 L (4D law, -2) and {slope_large:.3f} at r = 100 L (3D law, -1).")
    # allowed circumference from the typed torsion-balance assumption
    x_lim = 0.5 * math.log((1.0 + DEV_ALLOWED + 1.0) / (1.0 + DEV_ALLOWED - 1.0))    # coth x = 1 + DEV  ->  x = atanh(1/(1+DEV))
    l_max = math.pi * R_TESTED / x_lim
    m_kk = 2.0 * math.pi * hbar * c / l_max / eV
    p(f"Assumption (typed, from memory): torsion balances see no deviation above ~{DEV_ALLOWED:.0%} from 1/r^2 at r = {R_TESTED / UM:.0f} micrometres.")
    p(f"    coth(pi r / L) - 1 < {DEV_ALLOWED} at r = 52 um gives L < {l_max / UM:.0f} um (radius L/2pi < {l_max / UM / (2 * math.pi):.0f} um) and a first")
    p(f"    Kaluza-Klein mode heavier than {m_kk * 1e3:.1f} meV.  For L = 1 mm the force at 52 um would be {float(coth_strength(R_TESTED / 1e-3)):.1f} times Newton's.")
    p("    So a massless bulk mediator forces the extra dimension to be at most ~0.1 mm round, or the mediator to be massive/warped.")

    # ======================================================================================================
    p.section("B. The horizon problem: how fast must a bulk signal be?")
    # ------------------------------------------------------------------------------------------------------
    a_star = 1.0 / (1.0 + Z_STAR)
    eta_star = conformal_time_integral(0.0, a_star)
    d_c = conformal_time_integral(a_star, 1.0)
    s_common, s_direct = d_c / eta_star, 2.0 * d_c / eta_star
    theta_h = math.degrees(eta_star / d_c)
    p(f"Planck 2018 background, z* = {Z_STAR}: comoving horizon at recombination eta* = {eta_star * C_OVER_H0_GPC:.3f} Gpc,")
    p(f"    comoving distance to the last-scattering sphere d_C = {d_c * C_OVER_H0_GPC:.2f} Gpc; the horizon subtends {theta_h:.2f} degrees")
    p(f"    (about {(2 * d_c / eta_star) ** 2:.0f} causally disconnected patches over the sky).")
    p(f"    A common cause for two antipodal points needs signal speed >= d_C / eta* = {s_common:.0f} c; direct exchange needs >= 2 d_C / eta* = {s_direct:.0f} c.")
    p("    Gravitational waves travel at c to 1 part in 1e15 (GW170817), so the fast bulk mode cannot be the one carrying gravity;")
    p("    and any coupling of it to brane matter would show up as a preferred frame (Collins et al. 2004), so it must barely couple.")

    # ======================================================================================================
    p.section("C. Is a brane made from the medium's own domain wall stable?")
    # ------------------------------------------------------------------------------------------------------
    p("Dark soliton psi0 = tanh(x) (units hbar = m = g = n0 = 1: c = 1, xi = 1/sqrt 2, time unit hbar/(m c^2) = sqrt(2) xi / c).")
    p("Bogoliubov-de Gennes spectrum with transverse wavenumber k, finite differences on [-16, 16] with 360 points;")
    p("growth rate = largest imaginary part of omega.  Sanity check first: the stationary equation and the k = 0 spectrum.")
    xx = np.linspace(-6.0, 6.0, 2001)
    h = xx[1] - xx[0]
    psi_t = np.tanh(xx)
    resid = np.max(np.abs(-0.5 * (psi_t[2:] - 2 * psi_t[1:-1] + psi_t[:-2]) / h ** 2 + psi_t[1:-1] ** 3 - psi_t[1:-1]))
    _, ev_k0 = bdg_growth_rate(0.0)
    p(f"    residual of -psi''/2 + psi^3 - psi for tanh(x): {resid:.1e}; at k = 0 the largest |Im omega| is {np.max(np.abs(ev_k0.imag)):.1e} and the")
    p(f"    smallest |omega| is {np.min(np.abs(ev_k0)):.1e} (the translation zero mode, offset by discretisation); no instability for a straight soliton, as it must be.")
    ks = np.linspace(0.0, 1.2, 25)
    rates = []
    p(f"    {'k':>6s} {'growth rate':>12s}")
    for k in ks:
        g, _ = bdg_growth_rate(k)
        rates.append(g)
    for k, g in list(zip(ks, rates))[::3]:
        p(f"    {k:6.2f} {g:12.4f}")
    rates = np.array(rates)
    i_max = int(np.argmax(rates))
    k_cut = float(ks[np.nonzero(rates > 1e-3)[0][-1]]) if np.any(rates > 1e-3) else 0.0
    _, ev0 = bdg_growth_rate(0.0)
    g_fine, ev_fine = bdg_growth_rate(0.70, n_grid=720)
    g_coarse, _ = bdg_growth_rate(0.70, n_grid=360)
    _, ev_fine0 = bdg_growth_rate(0.0, n_grid=720)
    p(f"    Convergence at k = 0.70: growth rate {g_coarse:.4f} (360 points) and {g_fine:.4f} (720 points); the zero-mode offset falls from")
    p(f"    {np.min(np.abs(ev_k0)):.3f} to {np.min(np.abs(ev_fine0)):.3f} as the grid spacing halves, i.e. it is a discretisation error going to zero.")
    p(f"    maximum growth rate {rates[i_max]:.3f} (units m c^2 / hbar) at k = {ks[i_max]:.2f} (units m c / hbar); unstable for k below ~{k_cut:.2f}; growth at k = 0 is {rates[0]:.1e}.")
    p(f"    The wall's bending doubles in about {math.sqrt(2.0) * math.log(2) / rates[i_max]:.1f} xi / c.  For a Planck-length medium that is a few Planck times.")
    p("    This is the 'snake instability' of dark solitons (Kuznetsov & Turitsyn 1988; seen in cold atoms by Anderson et al. 2001):")
    p("    a flat wall in a repulsive superfluid breaks into vortex lines and rings.  A brane needs something more to hold it.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F4a: a hyper-dimensional medium gives 3D forces at large distance",
         f"ONLY IF the extra dimension is curled up: coth law verified to {worst:.0e}; torsion balances then need L < ~{l_max / UM:.0f} um"),
        ("F4b: a bulk shortcut can solve the horizon problem",
         f"POSSIBLE IN PRINCIPLE: needs a bulk signal of {s_common:.0f}-{s_direct:.0f} c, which cannot carry gravity (c to 1e-15) and must barely couple"),
        ("F4c: observers live on a 3D wall of the medium itself",
         f"NOT AS IT STANDS: the simplest wall (dark soliton) is unstable to bending, growth rate up to {rates[i_max]:.2f} mc^2/hbar, doubling in ~{math.sqrt(2.0) * math.log(2) / rates[i_max]:.0f} xi/c"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(17.5, 5.2))

    ax = axs[0]
    rr = np.geomspace(5.0, 2000.0, 300) * UM
    for l_val, col, lab in ((50 * UM, S1, "L = 50 μm"), (150 * UM, S3, "L = 150 μm"), (1000 * UM, S2, "L = 1 mm")):
        ax.plot(rr / UM, coth_strength(rr / l_val), color=col, lw=2.0, label=lab)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.axvline(R_TESTED / UM, color=MUTED, ls=":", lw=1.2)
    ax.set(xscale="log", yscale="log", ylim=(0.8, 400.0), xlabel="distance r (micrometres)",
           ylabel="brane force ÷ Newton's 1/r² force", title="Force law on the brane for extra-dimension size L")
    ax.text(R_TESTED / UM * 1.08, 130.0, "gravity tested down to 52 μm", fontsize=9, color=INK_2)
    ax.text(300.0, 0.86, "Newton", fontsize=9, color=INK_2)
    ax.legend(loc="upper right", fontsize=9)

    ax = axs[1]
    for sign in (-1, 1):
        x_a = sign * d_c * C_OVER_H0_GPC
        ax.fill([x_a - eta_star * C_OVER_H0_GPC, x_a + eta_star * C_OVER_H0_GPC, x_a], [eta_star * C_OVER_H0_GPC] * 2 + [0.0],
                facecolor=S1, alpha=0.5, edgecolor=S1, lw=1.5)
        ax.plot([x_a, 0.0], [eta_star * C_OVER_H0_GPC, 0.0], color=S2, lw=2.0)
        ax.plot(x_a, eta_star * C_OVER_H0_GPC, "o", color=INK_2, ms=6)
    ax.set(xlabel="comoving distance (Gpc)", ylabel="conformal time (Gpc / c)",
           title="Opposite CMB points: light cones never touch",
           xlim=(-16, 16), ylim=(-0.02, eta_star * C_OVER_H0_GPC * 1.45))
    ax.text(-15.5, 0.02, "blue: causal past by light\n(horizon 0.28 Gpc)", fontsize=9, color=S1)
    ax.text(-4.5, 0.17, f"orange: slowest bulk signal that\nconnects them, speed ≥ {s_common:.0f} c", fontsize=9, color=S2)

    ax = axs[2]
    ax.plot(ks, rates, "o-", color=S1, ms=5)
    ax.axhline(0.0, color=MUTED, ls="--", lw=1.2)
    ax.set(xlabel="bending wavenumber k of the wall (units mc/ħ)", ylabel="growth rate of the bending (units mc²/ħ)",
           title="A wall of the medium itself bends and breaks")

    fig.tight_layout()
    save_fig(fig, NAME, "hyperdimensional")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
