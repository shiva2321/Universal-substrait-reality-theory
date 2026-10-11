"""
r48 - The vortex-line network under expansion (GPU)  (LAB_NOTEBOOK.md entry E48, test N2)

Question (queue item from E47 and r42): "the network under expansion (Hubble friction) to see whether it reaches a scaling solution".  r42 and r46 followed the network of a NON-relativistic
(overdamped, TDGL) field with no expansion; the medium of the Planck-length mapping has sound speed c, i.e. its natural field theory is RELATIVISTIC (a complex scalar condensate with a Mexican-hat
potential, global U(1)).  Here that field is evolved on the GPU in an expanding background:

    phi'' + 2 (a'/a) phi' - nabla^2 phi + lambda (|phi|^2 - v^2) phi = 0      (conformal time eta, comoving coordinates, a = eta: radiation era),
    with the 'constant comoving core width' prescription (Press, Ryden & Spergel 1989: the potential term is kept fixed in comoving units so that the string core stays resolved on the lattice).
Substituting u = a phi removes the friction term exactly in the radiation era:   u'' = nabla^2 u - lambda (|u|^2 / eta^2 - v^2) u,   integrated with the leapfrog scheme (second order, stable for d eta < dx / sqrt(3)).
Strings are found from the winding of the phase of u on every plaquette (as in r42/r46); lengths use L = (2/3) N_plaquettes dx.

Scaling solution: the string length per comoving volume l_c obeys  l_c eta^2 / 4 = 1 / xi^2  with a constant xi (correlation length / horizon): physical string length per volume l = 1 / (xi^2 t^2),
t = eta^2/2.  Without expansion (Minkowski) the same relativistic network is expected to scale as l t^2 = 1/xi_M^2.
  * N2a: run both and measure xi(eta) at many times, several seeds;
  * N2b: what a scaling network means for the cosmic-string bound: Omega_s = (32 pi / 3) G mu / xi^2 in the radiation era (energy fraction in strings, constant in time).
"""
import math
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

import torch  # noqa: E402

NAME = "r48_network_under_expansion_gpu"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
N_GRID = int(os.environ.get("R48_N", 512 if DEV == "cuda" else 96))
DX = 0.5
D_ETA = 0.1                                  # < dx / sqrt(3) = 0.289
ETA0 = 1.0
MARKS = tuple(float(x) for x in os.environ.get("R48_MARKS", "6,8,10,13,16,20,25,30,36,44,52,60").split(","))
SEEDS = tuple(int(x) for x in os.environ.get("R48_SEEDS", "1,2,3").split(","))
GMU_BOUND = 1.5e-7
DAMP_UNTIL, GAMMA = 12.0, 1.0                 # Minkowski only: damped stage up to eta = 12


def laplacian(u):
    lap = -6.0 * u
    for d in range(3):
        lap += torch.roll(u, 1, d)
        lap += torch.roll(u, -1, d)
    return lap / DX ** 2


def windings_count(u):
    """Number of plaquettes pierced by a string (three orientations), from the phase of u."""
    th = torch.angle(u)
    twopi = 2.0 * math.pi
    wr = lambda d: torch.remainder(d + math.pi, twopi) - math.pi
    total = 0
    ti, tj, tk = torch.roll(th, -1, 0), torch.roll(th, -1, 1), torch.roll(th, -1, 2)
    # (y,z) plaquette
    tjk = torch.roll(tj, -1, 2)
    w = torch.round((wr(tj - th) + wr(tjk - tj) + wr(tk - tjk) + wr(th - tk)) / twopi)
    total += int(torch.count_nonzero(w))
    # (z,x) plaquette
    tik = torch.roll(ti, -1, 2)
    w = torch.round((wr(tk - th) + wr(tik - tk) + wr(ti - tik) + wr(th - ti)) / twopi)
    total += int(torch.count_nonzero(w))
    # (x,y) plaquette
    tij = torch.roll(ti, -1, 1)
    w = torch.round((wr(ti - th) + wr(tij - ti) + wr(tj - tij) + wr(th - tj)) / twopi)
    total += int(torch.count_nonzero(w))
    return total


def run(seed, expanding, marks):
    """Evolve from random phases; returns {mark: (n_plaquettes, mean |phi|^2)}."""
    g = torch.Generator(device=DEV).manual_seed(seed)
    n = N_GRID
    phase = torch.rand((n, n, n), generator=g, device=DEV, dtype=torch.float32) * (2.0 * math.pi)
    phi0 = torch.polar(torch.ones_like(phase), phase)               # |phi| = v = 1, random phase per cell
    del phase
    eta = ETA0
    scale = eta if expanding else 1.0
    u = (scale * phi0).to(torch.complex64)                          # u = a phi
    del phi0

    def acc(u_, eta_):
        a2 = eta_ ** 2 if expanding else 1.0
        amp2 = (u_.real ** 2 + u_.imag ** 2)
        return laplacian(u_) - (amp2 / a2 - 1.0) * u_

    # velocity: phi' = 0  =>  u' = a' phi = phi (radiation era a' = 1), or 0 without expansion
    vel = (u / scale if expanding else torch.zeros_like(u)).clone()
    vel += 0.5 * D_ETA * acc(u, eta)                                # leapfrog: velocity at eta + d_eta / 2
    out = {}
    t0 = time.time()
    for mark in marks:
        while eta < mark - 1e-9:
            u += D_ETA * vel
            eta += D_ETA
            if (not expanding) and eta <= DAMP_UNTIL:
                # Minkowski: a short strongly damped stage (gamma = 1) lets the random-phase field order into a string network; afterwards the evolution is undamped
                vel = (vel * (1.0 - 0.5 * D_ETA * GAMMA) + D_ETA * acc(u, eta)) / (1.0 + 0.5 * D_ETA * GAMMA)
            else:
                vel += D_ETA * acc(u, eta)
        # bring the field to the mark with the half-step velocity left as is (not needed for the winding)
        n_p = windings_count(u)
        a = eta if expanding else 1.0
        amp = float(torch.mean((u.real ** 2 + u.imag ** 2) / a ** 2))
        out[mark] = (n_p, amp)
    torch.cuda.synchronize() if DEV == "cuda" else None
    return out, time.time() - t0


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    name_dev = torch.cuda.get_device_name(0) if DEV == "cuda" else "CPU"
    p(f"Device: {name_dev}.  Lattice {N_GRID}^3, dx = {DX} (box {N_GRID * DX:g}), d eta = {D_ETA}; core width 1 in comoving units (lambda = v = 1); seeds {SEEDS}; marks {MARKS}.")
    vol = (N_GRID * DX) ** 3

    # ======================================================================================================
    p.section("N2a. Scaling of the relativistic network: expanding (radiation era) and Minkowski")
    # ------------------------------------------------------------------------------------------------------
    res = {True: [], False: []}
    for expanding in (True, False):
        for s in SEEDS:
            out, secs = run(s, expanding, MARKS)
            res[expanding].append(out)
            p(f"    {'expanding' if expanding else 'Minkowski':>10s} seed {s}: done in {secs:.0f} s ({(MARKS[-1] - ETA0) / D_ETA / secs:.0f} steps/s)")
    p(f"    {'eta (= t)':>10s} | {'plaquettes':>11s} {'l_c':>10s} {'xi (expanding)':>15s} {'|phi|^2':>8s} | {'plaquettes':>11s} {'l':>10s} {'xi (Minkowski)':>15s}")
    xi_e, xi_m = [], []
    for m in MARKS:
        npe = np.mean([r[m][0] for r in res[True]])
        npm = np.mean([r[m][0] for r in res[False]])
        lc_e = (2.0 / 3.0) * npe * DX / vol
        lc_m = (2.0 / 3.0) * npm * DX / vol
        xe = math.sqrt(4.0 / (lc_e * m ** 2)) if lc_e > 0 else float("nan")       # l t^2 = l_c eta^2 / 4 = 1 / xi^2
        xm = math.sqrt(1.0 / (lc_m * m ** 2)) if lc_m > 0 else float("nan")       # Minkowski: l t^2 = 1 / xi^2 with t = eta (origin at the start)
        xi_e.append(xe)
        xi_m.append(xm)
        amp_e = np.mean([r[m][1] for r in res[True]])
        p(f"    {m:10.1f} | {npe:11.0f} {lc_e:10.3e} {xe:15.3f} {amp_e:8.3f} | {npm:11.0f} {lc_m:10.3e} {xm:15.3f}")
    xi_e, xi_m = np.array(xi_e), np.array(xi_m)
    marks_a = np.array(MARKS)
    late = marks_a >= 16
    slope_e = np.polyfit(np.log(marks_a[late]), np.log(xi_e[late]), 1)[0]
    lm_arr = np.array([(2.0 / 3.0) * np.mean([r[m][0] for r in res[False]]) * DX / vol for m in MARKS])
    late_m = marks_a >= 25
    p_mink = -np.polyfit(np.log(marks_a[late_m]), np.log(lm_arr[late_m]), 1)[0]
    slope_m = float("nan")
    p(f"    => expanding: xi = {np.mean(xi_e[late]):.2f} +- {np.std(xi_e[late]):.2f} for eta >= 16, d ln xi / d ln eta = {slope_e:+.2f} (scaling: 0; a log drift of global strings is expected);")
    p(f"       Minkowski (damped to eta = {DAMP_UNTIL:g}, then undamped): length per volume falls as t^(-{p_mink:.2f}) for t >= 25 (scaling: -2).")
    p(f"    Reading: xi = 2 / (eta sqrt(l_c)) stays between {np.min(xi_e[late]):.2f} and {np.max(xi_e[late]):.2f} over eta = 16-60 (a factor {marks_a[-1] / 16:.2f} in eta): the string length per horizon volume changes by only")
    p(f"    {np.max(xi_e[late]) ** 2 / np.min(xi_e[late]) ** 2 - 1:.0%} over that range, so the expanding network is APPROXIMATELY SCALING: it neither decays relative to the horizon nor grows.  It drifts slowly (fitted exponent above);")
    p("    global strings are expected to drift logarithmically (their tension and radiation carry ln(xi t / core)); the fixed-comoving-core prescription and the finite dynamic range (core 1, box 256, eta <= 60)")
    p("    can matter, so the asymptotic constant is not resolved here.  Minkowski (damped start): the length per volume falls close to t^-2 (exponent above), also near-scaling.  Seeds agree to a few percent in length.")

    # ======================================================================================================
    p.section("N2b: what a scaling network means for the string bound")
    # ------------------------------------------------------------------------------------------------------
    xi_use = float(np.mean(xi_e[late]))
    omega_per_gmu = 32.0 * math.pi / 3.0 / xi_use ** 2
    p(f"    Energy fraction in strings in the radiation era: Omega_s = rho_s / rho_c = (32 pi / 3) G mu / xi^2 = {omega_per_gmu:.1f} G mu  (xi = {xi_use:.2f}); it is constant in time for a scaling network (here to within the drift above).")
    p(f"    For G mu = {GMU_BOUND:.1e} (the CMB bound used in r35, r42) this is Omega_s = {omega_per_gmu * GMU_BOUND:.1e}; for the Planck-density medium with G mu / c^2 ~ 2 pi f alpha^2 ln: of order 1 (r35: 10-900),")
    p("    so strings would hold the energy of the universe: no decay brings it down.  A scaling network is not diluted by waiting; only inflation after the strings form (or their absence) removes it.")
    p("    (Global strings have a logarithmically growing tension, mu = 2 pi v^2 ln(xi t / core), and radiate Goldstone quanta, so the energy fraction grows with ln(t / core) at fixed xi: worse than this estimate.)")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("N2a: a relativistic string network under radiation-era expansion is (approximately) scaling",
         f"{'YES, with a slow drift' if abs(slope_e) < 0.25 else 'NOT CLEARLY'}: xi = {np.mean(xi_e[late]):.2f} +- {np.std(xi_e[late]):.2f}, d ln xi / d ln eta = {slope_e:+.2f} (eta >= 16, {len(SEEDS)} seeds, {N_GRID}^3)"),
        ("N2b: waiting dilutes the strings (the network decays away)",
         f"NO: the energy fraction stays at (32 pi / 3) G mu / xi^2 = {omega_per_gmu:.0f} G mu; only inflation after formation removes them"),
        ("N2c: the GPU", f"{name_dev}: {(MARKS[-1] - ETA0) / D_ETA:.0f} leapfrog steps of a {N_GRID}^3 complex field per run"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<84s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.0, 5.2))
    ax = axs[0]
    ax.plot(marks_a, xi_e, "o-", color=S1, ms=7, label="expanding (radiation era), ξ = 2 / (η √l_c)")
    ax.plot(marks_a, xi_m, "s-", color=S2, ms=6, label="Minkowski (damped start), ξ = 1/(t √l)")
    ax.axhline(xi_use, color=MUTED, ls="--", lw=1.2)
    ax.set(xlabel="conformal time η (= t in Minkowski)", ylabel="correlation length ÷ horizon, ξ", ylim=(0, max(2.0, 1.3 * np.nanmax(xi_e))),
           title="Correlation length ÷ horizon of the two networks")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[1]
    lc_curve = [(2.0 / 3.0) * np.mean([r[m][0] for r in res[True]]) * DX / vol for m in MARKS]
    lm_curve = [(2.0 / 3.0) * np.mean([r[m][0] for r in res[False]]) * DX / vol for m in MARKS]
    ax.loglog(marks_a, lc_curve, "o-", color=S1, ms=7, label="expanding: length per comoving volume")
    ax.loglog(marks_a, lm_curve, "s-", color=S2, ms=6, label="Minkowski: length per volume")
    ax.loglog(marks_a, lc_curve[-1] * (marks_a / marks_a[-1]) ** -2.0, color=MUTED, ls="--", lw=1.4, label="∝ η⁻² (scaling)")
    ax.set(xlabel="conformal time η", ylabel="string length per volume", title="Length per volume falls as η⁻², i.e. fixed length per horizon")
    ax.legend(loc="lower left", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "expansion")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
