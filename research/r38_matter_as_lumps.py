"""
r38 - Matter as lumps, rings and bubbles of the medium: do they behave like particles?
(LAB_NOTEBOOK.md entry E46, test F6)

Question (user): "d" (a new idea of yours), taken here as the picture in the user's own words from E44/E45: "matter eithree creates cavity or
a bubble in/on the sapce ... it isolates a section/area of it to exist and trapp that energy which then contributes to creating
the reality" - matter as a localised lump of trapped energy of the superfluid medium.

Physics: a relativistic particle with rest mass M has E^2 = (cP)^2 + M^2 c^4, so E >= cP always, and E / (cP) = c / v.  A lump of a
superfluid is a state of a Galilean-invariant medium: nothing forces E >= cP.  Three lumps of the Gross-Pitaevskii medium (units
hbar = m = g = n0 = 1, so c = 1 and the healing length is 1 / sqrt 2 in the xi convention of r33):
  * the dark soliton (a planar notch in the density), exact moving solution psi = i v + sqrt(1 - v^2) tanh( sqrt(1 - v^2) (x - v t) ):
    E(v) = (4/3)(1 - v^2)^(3/2), canonical momentum P(v) = 2 [ arccos v - v sqrt(1 - v^2) ], with dE/dP = v, inertial mass dP/dv;
  * the vortex ring (large-ring asymptotics, Roberts & Grant 1971): E = (1/2) rho kappa^2 R [ln(8R/a) - 2], P = pi rho kappa R^2,
    v = dE/dP = kappa [ln(8R/a) - 1] / (4 pi R)  (kappa = h/m, core size a ~ 1; constants inside the log do not matter here);
  * the cavity (a bubble, a hole in the density), whose lifetime is simulated in spherical symmetry.

Method:
  A. Dark soliton: simulate two solitons (+v and -v, so the box is periodic) with split-step Fourier, measure speed, depth and energy
     against the exact formulas, then E, P, inertial mass and E/(cP).
  B. Vortex rings: E/(cP), v and the absence of a rest frame from the asymptotic formulas.
  C. Cavity: spherically symmetric 3D GP via u = r (psi - 1) and the sine transform; deficit of particles inside the original size
     against time for three sizes.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import dst, idst

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r38_matter_as_lumps"
CORE_A = 1.0


def soliton_energy(v):
    return (4.0 / 3.0) * (1.0 - v ** 2) ** 1.5


def soliton_momentum(v):
    return 2.0 * (np.arccos(v) - v * np.sqrt(1.0 - v ** 2))


def soliton_mass(v):
    return -4.0 * np.sqrt(1.0 - v ** 2)


def profile(x, v):
    s = math.sqrt(1.0 - v * v)
    return 1j * v + s * np.tanh(s * x)


def simulate_soliton_pair(v, length=256.0, n_grid=2048, dt=0.005, t_end=50.0):
    """Two solitons of speed v (opposite velocities; periodic box).  Returns measured speed, minimum density, energy per soliton."""
    x = (np.arange(n_grid) - n_grid // 2) * length / n_grid
    kk = 2.0 * np.pi * np.fft.fftfreq(n_grid, d=length / n_grid)
    # phase jumps 2 arcsin(v) - pi and -2 arcsin(v) - pi add to -2 pi: the product is periodic
    psi = profile(x - 64.0, v) * profile(x + 64.0, -v)
    half = np.exp(-0.5j * dt * 0.5 * kk ** 2)

    def energy(ps):
        dpsi = np.fft.ifft(1j * kk * np.fft.fft(ps))
        return np.sum(0.5 * np.abs(dpsi) ** 2 + 0.5 * (np.abs(ps) ** 2 - 1.0) ** 2) * length / n_grid

    e0 = energy(psi)
    times, pos, nmin = [], [], []
    steps = int(round(t_end / dt))
    for s in range(steps + 1):
        if s % 200 == 0:
            n = np.abs(psi) ** 2
            mask = x > 0
            j = np.argmin(np.where(mask, n, 10.0))
            y0, y1, y2 = n[j - 1], n[j], n[j + 1]
            shift = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
            times.append(s * dt)
            pos.append(x[j] + shift * length / n_grid)
            nmin.append(y1 - 0.25 * (y0 - y2) * shift)
        psi = np.fft.ifft(half * np.fft.fft(psi))
        psi *= np.exp(-1j * dt * (np.abs(psi) ** 2 - 1.0))
        psi = np.fft.ifft(half * np.fft.fft(psi))
    e1 = energy(psi)
    speed = np.polyfit(times, pos, 1)[0]
    return speed, float(np.mean(nmin)), 0.5 * e0, 0.5 * e1


def ring_properties(r):
    ln = math.log(8.0 * r / CORE_A)
    kappa = 2.0 * math.pi
    energy = 0.5 * kappa ** 2 * r * (ln - 2.0)
    mom = math.pi * kappa * r ** 2
    vel = kappa * (ln - 1.0) / (4.0 * math.pi * r)
    return energy, mom, vel


def cavity_run(width, depth=0.9, radius=160.0, n_grid=1280, dt=0.01, t_end=None):
    """Spherically symmetric 3D GP, psi = 1 + phi, u = r phi with u(0) = u(R) = 0 (sine transform).  Returns time, deficit inside
    r < width (normalised), central density, total excess energy."""
    dr = radius / n_grid
    r = dr * np.arange(1, n_grid)
    psi = np.sqrt(1.0 - depth * np.exp(-r ** 2 / (2.0 * width ** 2))).astype(complex)
    k = np.pi * np.arange(1, n_grid) / radius
    kin = np.exp(-1j * dt * 0.5 * k ** 2)

    def deficit(ps):
        return float(np.sum(4.0 * np.pi * r ** 2 * (1.0 - np.abs(ps) ** 2) * (r < width)) * dr)

    def energy(ps):
        dpsi = np.gradient(ps, dr)
        return float(np.sum(4.0 * np.pi * r ** 2 * (0.5 * np.abs(dpsi) ** 2 + 0.5 * (np.abs(ps) ** 2 - 1.0) ** 2)) * dr)

    t_end = t_end if t_end is not None else 4.0 * width
    steps = int(round(t_end / dt))
    d0, e0 = deficit(psi), energy(psi)
    ts, ds, ns = [0.0], [1.0], [float(abs(psi[0]) ** 2)]
    for s in range(1, steps + 1):
        psi *= np.exp(-0.5j * dt * (np.abs(psi) ** 2 - 1.0))
        u = r * (psi - 1.0)
        uk = dst(u.real, type=1) + 1j * dst(u.imag, type=1)
        uk *= kin
        u = idst(uk.real, type=1) + 1j * idst(uk.imag, type=1)
        psi = 1.0 + u / r
        psi *= np.exp(-0.5j * dt * (np.abs(psi) ** 2 - 1.0))
        if s % 20 == 0:
            ts.append(s * dt)
            ds.append(deficit(psi) / d0)
            ns.append(float(abs(psi[0]) ** 2))
    return np.array(ts), np.array(ds), np.array(ns), e0, energy(psi)


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. The dark soliton: a lump of the medium, simulated")
    # ------------------------------------------------------------------------------------------------------
    p("Two solitons (speed +v and -v, periodic box 256, 2048 points, dt = 0.005, T = 50) started from the exact profile.")
    p("(The split-step method is stable only for dt k_max^2 / 2 < pi; a finer grid with the same dt blew up, so the grid spacing is 0.125.)")
    p(f"    {'v':>5s} {'speed sim':>10s} {'min density sim':>16s} {'v^2':>7s} {'E sim (t=0)':>12s} {'E sim (T)':>10s} {'(4/3)(1-v^2)^1.5':>17s}")
    sim_rows = []
    for v in (0.2, 0.5, 0.8):
        sp, nm, e_a, e_b = simulate_soliton_pair(v)
        sim_rows.append((v, sp, nm, e_a, e_b))
        p(f"    {v:5.2f} {sp:10.5f} {nm:16.5f} {v * v:7.4f} {e_a:12.5f} {e_b:10.5f} {soliton_energy(v):17.5f}")
    worst_speed = max(abs(abs(r[1]) / r[0] - 1.0) for r in sim_rows)
    worst_energy = max(abs(r[4] / soliton_energy(r[0]) - 1.0) for r in sim_rows)
    p(f"    => speed, depth and energy agree with the exact formulas (worst relative difference {max(worst_speed, worst_energy):.1e}); the lump is stable in 1D.")
    p(f"    {'v':>5s} {'E':>9s} {'P':>9s} {'inertial mass dP/dv':>20s} {'E / (c P)':>10s} {'relativistic c/v':>17s}")
    for v in (0.05, 0.2, 0.5, 0.8, 0.95):
        p(f"    {v:5.2f} {soliton_energy(v):9.4f} {soliton_momentum(v):9.4f} {soliton_mass(v):20.4f} {soliton_energy(v) / soliton_momentum(v):10.4f} {1.0 / v:17.2f}")
    vs = np.linspace(0.01, 0.999, 400)
    ratio_sol = soliton_energy(vs) / soliton_momentum(vs)
    p(f"    => the energy FALLS as the lump speeds up and the inertial mass is NEGATIVE ({soliton_mass(0.0):.0f} at rest); E/(cP) stays between "
      f"{ratio_sol.min():.2f} and {ratio_sol.max():.2f}, below 1 for v < c, whereas any particle with rest mass has E/(cP) = c/v > 1.")
    p("    A flat soliton also bends and breaks in higher dimensions (snake instability, r36).")

    # ======================================================================================================
    p.section("B. Vortex rings")
    # ------------------------------------------------------------------------------------------------------
    p("Large-ring asymptotics (units hbar = m = n0 = 1, kappa = 2 pi, c = 1):")
    p(f"    {'R':>6s} {'v':>8s} {'E':>10s} {'P':>10s} {'E / (c P)':>10s} {'E / (P v)':>10s}")
    ring_rows = []
    for rr in (4.0, 8.0, 16.0, 40.0, 100.0, 400.0):
        e, pm, vel = ring_properties(rr)
        ring_rows.append((rr, vel, e, pm))
        p(f"    {rr:6.0f} {vel:8.4f} {e:10.1f} {pm:10.1f} {e / pm:10.4f} {e / (pm * vel):10.3f}")
    p("    (R below ~4 core sizes is outside the asymptotic formulas and only qualitatively right.)")
    p("    => E/(cP) = 2 (v/c)(ln - 2)/(ln - 1), always below 2v/c: every ring has E < cP (impossible for a particle with a real rest mass); E/(Pv) -> 2 where a particle")
    p("       with rest mass has c^2/v^2 -> infinity as v -> 0; and as R grows the ring slows (v -> 0) while E ~ R ln R and P ~ R^2 grow without limit:")
    p("       there is no state at rest with a finite energy, so no rest mass.  As R shrinks to the core size the ring becomes a sound pulse (E -> cP).")

    # ======================================================================================================
    p.section("C. A cavity (bubble) in the medium")
    # ------------------------------------------------------------------------------------------------------
    p("Spherically symmetric 3D GP, hole of depth 90 % and Gaussian width w; deficit of particles inside r < w against time.")
    widths = (2.0, 4.0, 8.0)
    cav = {}
    p(f"    {'w':>5s} {'t_half (c/w)':>13s} {'t_half':>8s} {'central density at t = w/c':>28s} {'energy drift':>13s}")
    t_halves = []
    for w in widths:
        ts, ds, ns, e0, e1 = cavity_run(w)
        cav[w] = (ts, ds, ns)
        below = np.nonzero(ds <= 0.5)[0]
        t_half = float(ts[below[0]]) if len(below) else float("nan")
        t_halves.append(t_half)
        p(f"    {w:5.1f} {t_half / w:13.3f} {t_half:8.2f} {float(np.interp(w, ts, ns)):28.3f} {abs(e1 / e0 - 1.0):13.1e}")
    p(f"    => the deficit inside the original size halves in t = {np.mean([t / w for t, w in zip(t_halves, widths)]):.2f} w/c for every size: a cavity")
    p("       of size w lives about w/c, then its emptiness leaves as a sound pulse.  A 1 mm cavity would last 3 ps; a Planck-size one a few Planck times.")
    p("       Only a source that keeps pushing (a repulsive impurity, E1, r01) holds it open, and then the dent is screened (short range).")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F6a: matter is a lump of the medium obeying E >= cP",
         f"NO: dark soliton E/(cP) = {ratio_sol.min():.2f}-{ratio_sol.max():.2f} (< 1), vortex rings E/(cP) ~ 2v/c <= {max(r[2] / r[3] for r in ring_rows):.2f}"),
        ("F6b: such a lump has a positive rest mass and a rest frame",
         f"NO: the soliton's inertial mass is {soliton_mass(0.0):.0f} (negative), and a ring's energy and momentum diverge as it slows to rest"),
        ("F6c: a cavity of trapped energy persists on its own",
         f"NO: a cavity of size w empties in ~{np.mean([t / w for t, w in zip(t_halves, widths)]):.1f} w/c (sound crossing time)"),
        ("F6d: what would make lumps matter-like",
         "a Lorentz-invariant field equation at the lump scale (relativistic kinks obey E = gamma M c^2: r01); a superfluid only gives that for phonons"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<62s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(17.5, 5.3))

    ax = axs[0]
    vv = np.linspace(0.02, 0.999, 300)
    ax.plot(vv, 1.0 / vv, color=MUTED, ls="--", lw=1.4, label="any particle with rest mass: c/v")
    ax.plot(vs, ratio_sol, color=S1, lw=2.0, label="dark soliton (lump)")
    rv = np.array([r[1] for r in ring_rows])
    rr_ratio = np.array([r[2] / r[3] for r in ring_rows])
    ax.plot(rv, rr_ratio, "o-", color=S2, ms=6, lw=1.6, label="vortex rings, R = 4 … 400")
    ax.axhline(1.0, color=INK_2, lw=1.0)
    ax.set(yscale="log", ylim=(0.01, 60.0), xlabel="speed v ÷ c", ylabel="E ÷ (c P)",
           title="Matter must have E ≥ cP; the medium's lumps do not")
    ax.text(0.02, 1.15, "E = cP (sound)", fontsize=9, color=INK_2)
    ax.legend(loc="upper right", fontsize=9)

    ax = axs[1]
    ax.plot(vs, soliton_energy(vs), color=S1, lw=2.0, label="dark soliton: energy falls with speed")
    ax.plot(vs, soliton_energy(0.0) / np.sqrt(1.0 - vs ** 2), color=MUTED, ls="--", lw=1.4, label="particle: E = γ M c² (rises)")
    ax.plot([r[0] for r in sim_rows], [r[4] for r in sim_rows], "o", color=S2, ms=8, label="simulation")
    ax.set(ylim=(0.0, 3.0), xlabel="speed v ÷ c", ylabel="energy (soliton rest energy = 4/3)", title="A faster lump is lighter: negative inertial mass")
    ax.legend(loc="upper left", fontsize=9)

    ax = axs[2]
    for w, col in zip(widths, (S1, S2, S3)):
        ts, ds, _ = cav[w]
        ax.plot(ts / w, ds, color=col, lw=2.0, label=f"cavity size w = {w:g}")
    ax.axhline(0.5, color=MUTED, ls="--", lw=1.2)
    ax.axhline(0.0, color=INK_2, lw=1.0)
    ax.set(xlabel="time × c / w", ylabel="deficit inside the original size (fraction left)", xlim=(0, 4), ylim=(-0.6, 1.05),
           title="A cavity empties in about one sound-crossing time")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "lumps")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
