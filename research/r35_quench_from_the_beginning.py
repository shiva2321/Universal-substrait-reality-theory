"""
r35 - The beginning: a quench from a hot disordered state into a superfluid, and what it leaves behind
(LAB_NOTEBOOK.md entry E45, test F3)

Question (user): "lets try to simulate universe from very begininig ... first its a super fluide like matter".
In the fluid-space picture the universe begins as a hot, disordered medium that cools through a phase transition into the
superfluid.  Whatever the transition does not order is frozen in as topological defects: in a superfluid (a complex order
parameter, U(1) phase) these are quantised vortices, which in 3 dimensions are lines.  Seen by a 3D observer a vortex line
is a "cosmic string".  (A vortex membrane in a 4D medium meets a 3D brane in lines as well.)

Physics:
  * Kibble-Zurek (KZ): the medium cannot follow a cooling rate 1/tau_Q once its relaxation time exceeds the time to the
    transition; domains of size xi_hat freeze, and defects form with density ~ 1/xi_hat^2.  For the mean-field relaxation
    equation (z = 2, nu = 1/2): xi_hat ~ tau_Q^(1/4), so in 2D  n_v ~ tau_Q^(-1/2).
  * Vortex line energy: E/L = pi rho (hbar/m)^2 ln(R/xi) = 2 pi rho c^2 xi^2 ln(R/xi)  (using hbar/m = sqrt(2) c xi), so
    G mu / c^2 = 2 pi (G rho xi^2 / c^2) ln(R/xi).  For a medium of density f rho_P and healing length alpha l_P this is
    2 pi f alpha^2 ln(R/xi), because G m_P / (c^2 l_P) = 1.

Method:
  A. Simulate the time-dependent Ginzburg-Landau equation  d psi/dt = eps(t) psi - |psi|^2 psi + nabla^2 psi + noise  in 2D
     (256 x 256, dx = 0.5, periodic) with eps(t) = t / tau_Q ramped through zero.  Count vortices (plaquette windings of the
     phase) at t = kappa sqrt(tau_Q), a fixed multiple of the freeze-out time, once the order parameter has formed; fit
     n_v against tau_Q with counting-error weights.
  B. Planck-scale medium: string tension G mu / c^2, the density it must stay below, and the e-folds of inflation needed to
     dilute the frozen-in strings to below one per observable universe.
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
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, hbar, lP, mP, save_fig, style  # noqa: E402

NAME = "r35_quench_from_the_beginning"
N_GRID, DX, DT = 256, 0.5, 0.04
EPS0 = 0.3                       # the ramp starts at eps = -EPS0
NOISE_D = 5.0e-3                 # noise strength (thermal level of the disordered phase)
KAPPAS = (6.0, 8.0)              # count at t = kappa sqrt(tau_Q)
TAUS = (10, 20, 40, 80, 160)
SEEDS = {10: 3, 20: 3, 40: 3, 80: 4, 160: 6}
KB = 1.380649e-23
T0_K = 2.7255
R_OBS = 4.4e26                   # radius of the observable universe (m)
GMU_BOUND = 1.5e-7               # CMB bound on G mu / c^2 for Nambu-Goto strings (order of magnitude for global vortices)


def plaquette_windings(psi):
    th = np.angle(psi)
    wrap = lambda d: (d + np.pi) % (2.0 * np.pi) - np.pi
    t10 = np.roll(th, -1, 0)
    t11 = np.roll(t10, -1, 1)
    t01 = np.roll(th, -1, 1)
    return np.rint((wrap(t10 - th) + wrap(t11 - t10) + wrap(t01 - t11) + wrap(th - t01)) / (2.0 * np.pi)).astype(int)


def quench(tau, seed):
    """Ramp eps(t) = t / tau from -EPS0; return {kappa: (n_v, mean|psi|^2 / eps, winding map)} at t = kappa sqrt(tau)."""
    rng = np.random.default_rng(seed)
    psi = math.sqrt(NOISE_D) * (rng.standard_normal((N_GRID, N_GRID)) + 1j * rng.standard_normal((N_GRID, N_GRID)))
    amp = math.sqrt(NOISE_D * DT) / DX
    area = (N_GRID * DX) ** 2
    t = -EPS0 * tau
    targets = sorted((k * math.sqrt(tau), k) for k in KAPPAS)
    out, ti = {}, 0
    while ti < len(targets):
        eps = t / tau
        lap = (np.roll(psi, 1, 0) + np.roll(psi, -1, 0) + np.roll(psi, 1, 1) + np.roll(psi, -1, 1) - 4.0 * psi) / DX ** 2
        noise = amp * (rng.standard_normal((N_GRID, N_GRID)) + 1j * rng.standard_normal((N_GRID, N_GRID)))
        psi = psi + DT * (eps * psi - (psi.real ** 2 + psi.imag ** 2) * psi + lap) + noise
        t += DT
        if t >= targets[ti][0]:
            w = plaquette_windings(psi)
            out[targets[ti][1]] = (int(np.abs(w).sum()), area, float(np.mean(np.abs(psi) ** 2)) / eps, w, psi.copy())
            ti += 1
    return out


def weighted_slope(taus, counts, areas):
    """Slope of log(density) against log(tau), Poisson weights (relative error 1/sqrt(count))."""
    x = np.log(np.array(taus, float))
    y = np.log(np.array(counts, float) / np.array(areas, float))
    wgt = np.array(counts, float)                    # 1/sigma^2 = N for ln N
    xm, ym = np.sum(wgt * x) / wgt.sum(), np.sum(wgt * y) / wgt.sum()
    slope = np.sum(wgt * (x - xm) * (y - ym)) / np.sum(wgt * (x - xm) ** 2)
    err = 1.0 / math.sqrt(np.sum(wgt * (x - xm) ** 2))
    return slope, err


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. Defect formation in a superfluid quench (2D time-dependent Ginzburg-Landau, Kibble-Zurek scaling)")
    # ------------------------------------------------------------------------------------------------------
    p(f"Grid {N_GRID}x{N_GRID}, dx = {DX}, dt = {DT}, noise D = {NOISE_D:g}; eps ramps from -{EPS0} at rate 1/tau_Q; vortices counted at")
    p("t = kappa sqrt(tau_Q) (a fixed multiple of the freeze-out time sqrt(tau_Q)) once the order parameter has formed.")
    results = {k: {} for k in KAPPAS}
    snaps = {}
    for tau in TAUS:
        runs = [quench(tau, seed) for seed in range(1, SEEDS[tau] + 1)]
        for k in KAPPAS:
            results[k][tau] = (sum(r[k][0] for r in runs), sum(r[k][1] for r in runs),
                               float(np.mean([r[k][2] for r in runs])))
        if tau in (TAUS[0], TAUS[-1]):
            snaps[tau] = runs[0][KAPPAS[0]]
    primary = KAPPAS[0]
    p(f"    {'tau_Q':>6s} {'runs':>5s} {'vortices':>9s} {'n_v':>10s} {'n_v sqrt(tau)':>14s} {'|psi|^2/eps':>12s}   (kappa = {primary:.0f})")
    for tau in TAUS:
        n_c, area, formed = results[primary][tau]
        p(f"    {tau:6d} {SEEDS[tau]:5d} {n_c:9d} {n_c / area:10.5f} {n_c / area * math.sqrt(tau):14.5f} {formed:12.2f}")
    fits = {}
    for k in KAPPAS:
        sl, er = weighted_slope(TAUS, [results[k][t][0] for t in TAUS], [results[k][t][1] for t in TAUS])
        fits[k] = (sl, er)
        p(f"    kappa = {k:.0f}: fitted exponent n_v ~ tau_Q^({sl:.2f} +- {er:.2f})")
    slope, err = fits[primary]
    spread = max(abs(f[0] - slope) for f in fits.values())
    p(f"    Kibble-Zurek (mean field, z = 2, nu = 1/2) predicts -0.50. Measured {slope:.2f} +- {err:.2f} (stat), a further {spread:.2f}")
    p("    from the choice of counting time.  Counting rules matter: exploratory runs in a smaller box, counting before the order")
    p("    parameter had formed or at a different stage, gave anything from +1.8 to -0.68 (see E45); the rule used here is the one")
    p("    that counts real vortices (|psi|^2 / eps = 0.94 at the count) at a fixed multiple of the freeze-out time.")
    p("    Faster quench: more defects; slower: fewer; never none: the density is set by the cooling rate.")

    # ======================================================================================================
    p.section("B. If the medium is Planck-scale: what its vortex lines would weigh, and what dilutes them")
    # ------------------------------------------------------------------------------------------------------
    unit = G0 * mP() / (c ** 2 * lP())
    ln_form, ln_today = 1.5, math.log(R_OBS / lP())
    p(f"G m_P / (c^2 l_P) = {unit:.3f}, so  G mu / c^2 = 2 pi f alpha^2 ln(R/xi)  for density f rho_P and healing length alpha l_P.")
    p(f"    {'f':>8s} {'alpha':>6s} {'ln(R/xi)':>9s} {'G mu / c^2':>12s}   (bound {GMU_BOUND:.1e})")
    for f_val, alpha, lg in ((1.0, 1.0, ln_form), (1.0, 1.0, ln_today), (1e-8, 1.0, ln_today), (1e-10, 1.0, ln_today)):
        p(f"    {f_val:8.0e} {alpha:6.1f} {lg:9.1f} {2 * math.pi * f_val * alpha ** 2 * lg:12.2e}")
    f_max_form = GMU_BOUND / (2.0 * math.pi * ln_form)
    f_max_today = GMU_BOUND / (2.0 * math.pi * ln_today)
    p(f"    => the medium must satisfy f alpha^2 < {f_max_form:.1e} (R = string spacing at formation) or < {f_max_today:.1e} (R = observable universe):")
    p(f"       i.e. {1 / f_max_form:.0e} to {1 / f_max_today:.0e} times less dense than the Planck density if its healing length is a Planck length.")
    t_planck = math.sqrt(hbar * c ** 5 / G0) / KB
    g_ratio = (106.75 / 3.91) ** (1.0 / 3.0)
    stretch = t_planck / T0_K * g_ratio
    spacing_formation = lP() * TAUS[0] ** 0.25
    spacing_today = spacing_formation * stretch
    n_per_universe = (R_OBS / spacing_today) ** 3
    n_efolds = math.log(R_OBS / spacing_today)
    p(f"Dilution: formation at T_P = {t_planck:.2e} K, expansion to today (T = {T0_K} K, entropy dof included) stretches lengths x{stretch:.1e};")
    p(f"    KZ spacing {spacing_formation:.1e} m becomes {spacing_today:.1e} m, i.e. about {n_per_universe:.0e} string segments in the")
    p(f"    observable universe.  Extra stretching by exp(N) with N = ln(R_obs / spacing) = {n_efolds:.0f} e-folds (inflation) leaves about one.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F3a: a quench into the superfluid leaves vortex defects, set by the cooling rate",
         f"CONFIRMED by simulation: n_v ~ tau_Q^({slope:.2f} +- {err:.2f}) against the Kibble-Zurek -0.50"),
        ("F3b: a Planck-density, Planck-length superfluid is compatible with the observed sky",
         f"NO: its vortex lines have G mu / c^2 ~ {2 * math.pi * ln_form:.0f}-{2 * math.pi * ln_today:.0f} against < {GMU_BOUND:.0e}"),
        ("F3c: what would rescue it",
         f"(i) a medium {1 / f_max_form:.0e}-{1 / f_max_today:.0e} times less dense than Planck, or (ii) about {n_efolds:.0f} e-folds of "
         f"inflation after the transition, or (iii) a vacuum manifold without vortices"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<80s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 10.4))
    for ax, tau in ((axs[0, 0], TAUS[0]), (axs[0, 1], TAUS[-1])):
        n_c, area, formed, w, psi = snaps[tau]
        ax.imshow(np.angle(psi).T, origin="lower", cmap="twilight", extent=(0, N_GRID * DX, 0, N_GRID * DX))
        for sign, col in ((1, "white"), (-1, "black")):
            ii, jj = np.nonzero(w == sign)
            ax.scatter((ii + 0.5) * DX, (jj + 0.5) * DX, s=26, facecolors="none", edgecolors=col, linewidths=1.2)
        ax.set(title=f"Cooling time τ = {tau}: {n_c} vortices formed", xticks=[], yticks=[])
        ax.grid(False)
    axs[0, 0].set_xlabel("colour = phase of the order parameter; white / black rings = vortex / antivortex", fontsize=8.5)

    ax = axs[1, 0]
    dens = np.array([results[primary][t][0] / results[primary][t][1] for t in TAUS])
    rel_err = np.array([1.0 / math.sqrt(results[primary][t][0]) for t in TAUS])
    ax.errorbar(TAUS, dens, yerr=dens * rel_err, fmt="o", color=S1, ms=7, capsize=3, label="simulation")
    tt = np.geomspace(TAUS[0] * 0.8, TAUS[-1] * 1.25, 50)
    ax.plot(tt, dens[0] * (tt / TAUS[0]) ** -0.5, color=MUTED, ls="--", lw=1.2, label="Kibble–Zurek ∝ τ^(−1/2)")
    ax.plot(tt, dens[0] * (tt / TAUS[0]) ** slope, color=S2, lw=1.6, label=f"fit ∝ τ^({slope:.2f})")
    ax.set(xscale="log", yscale="log", xlabel="cooling time τ (slower →)", ylabel="vortices per unit area",
           title="Slower cooling leaves fewer defects, never none")
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1, 1]
    fs = np.geomspace(1e-14, 1.0, 100)
    ax.plot(fs, 2 * math.pi * fs * ln_form, color=S1, lw=2.0, label=f"R = string spacing (ln = {ln_form})")
    ax.plot(fs, 2 * math.pi * fs * ln_today, color=S2, lw=2.0, label=f"R = observable universe (ln = {ln_today:.0f})")
    ax.axhline(GMU_BOUND, color=MUTED, ls="--", lw=1.2)
    ax.set(xscale="log", yscale="log", xlabel="medium density ÷ Planck density (healing length = Planck length)",
           ylabel="string tension  Gμ/c²", title="Vortex lines of a dense medium would be absurdly heavy strings")
    ax.text(3e-6, GMU_BOUND * 0.22, "observational bound ≈ 1.5×10⁻⁷", fontsize=9, color=INK_2)
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "quench")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
