"""
r01 - Follow-up questions, round 1 (2026-10-10).  See LAB_NOTEBOOK.md entries E1-E4.

Q1  Does the substrate "dent" around a mass create an opposite "high point" (antigravity)?
Q2  Does a flexible superfluid (no crystal) fix the direction problem, and can
    "interference from many ripples" slow light near mass?
Q3  Does a bigger trapped energy give a longer-reaching dent?  What happens if the
    effect spreads into extra dimensions?
Q4  What does a substrate say about the speed of light? (particles as trapped ripples)

Method
  * Q1/Q3: radial Gross-Pitaevskii ground state around a repulsive source of three
    strengths (healing-length units); look for density > 1 and fit the tail.
  * Q2: Bogoliubov dispersion for Planck-mass grains; the density dent needed to
    reproduce GR light bending; Shapiro delay.
  * Q3: healing length needed for a galaxy-scale range -> grain mass; Gauss's law
    in D dimensions.
  * Q4: discrete sine-Gordon chain (pendulums coupled by springs, wave speed c = 1):
    a kink (trapped twist) at several speeds, and under a constant push.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import solve_bvp  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import (G0, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, mP,  # noqa: E402
                    save_fig, style)

NAME = "r01_dent_range_relativity"
Msun, Rsun, Mearth, Rearth = 1.98847e30, 6.957e8, 5.9722e24, 6.371e6


def gp_dent(V0, r0=1.2):
    def ode(rr, y):
        return np.vstack((y[1], -2 / rr * y[1] + (y[0] ** 2 - 1 + V0 * np.exp(-(rr / r0) ** 2)) * y[0]))

    def bc(ya, yb):
        return np.array([ya[1], yb[0] - 1.0])
    rr = np.linspace(1e-3, 40, 4000)
    guess = np.vstack((1 - (1 - math.exp(-V0 / 4)) * np.exp(-(rr / 3) ** 2), np.zeros_like(rr)))
    return solve_bvp(ode, bc, rr, guess, max_nodes=200000, tol=1e-9)


def sine_gordon(v, f=0.0, T=40.0, dt=0.02, h=0.05, N=6000):
    """Discrete sine-Gordon chain; returns rows (t, kink position, max slope, energy)."""
    x = (np.arange(N) - N // 2) * h
    g = 1 / math.sqrt(1 - v * v)
    u = np.clip(g * (x + 40), -700, 700)
    phi = 4 * np.arctan(np.exp(u))
    dphi = -2 * g * v / np.cosh(u)

    def acc(p):
        lap = np.zeros_like(p)
        lap[1:-1] = (p[2:] - 2 * p[1:-1] + p[:-2]) / h ** 2
        return lap - np.sin(p) + f
    a = acc(phi)
    out = []
    for n in range(int(T / dt)):
        dphi += 0.5 * dt * a
        phi += dt * dphi
        a = acc(phi)
        dphi += 0.5 * dt * a
        if n % 50 == 0:
            d = np.diff(phi)
            i = np.argmax(np.abs(d))
            E = np.sum(0.5 * dphi[:-1] ** 2 + 0.5 * (d / h) ** 2 + (1 - np.cos(phi[:-1]))) * h
            out.append((n * dt, x[i], np.abs(d).max() / h, E))
    return np.array(out)


def main():
    p = Report(NAME)
    style(plt)

    # ---------------- Q1 / Q3: the dent ----------------
    p.section("Q1/Q3  Superfluid dent around a source (Gross-Pitaevskii, healing-length units)")
    dents = {}
    for V0 in (0.5, 3.5, 20.0):
        sol = gp_dent(V0)
        r = np.linspace(0.01, 30, 6000)
        rho = sol.sol(r)[0] ** 2
        tail = (r > 6) & (r < 16)
        k = np.polyfit(r[tail], np.log((1 - rho[tail]) * r[tail]), 1)[0]
        deficit = np.trapezoid(4 * np.pi * r ** 2 * (1 - rho), r)
        dents[V0] = (r, rho, k)
        p(f"source {V0:5.1f}: converged={sol.success}  centre density {rho[0]:.3f}  max density {rho.max():.6f}"
          f"  tail ~ exp({k:.3f} r)/r  displaced amount {deficit:.2f}")
    p("=> density never exceeds the background (no 'high point'); the displaced substrate spreads to")
    p("   infinity. A stronger source makes the dent DEEPER, but its range (healing length) is unchanged.")

    # ---------------- Q2 ----------------
    p.section("Q2  Flexible superfluid of Planck-mass grains: Bogoliubov dispersion")
    for label, lam in (("green light 500 nm", 500e-9), ("100 GeV gamma ray", 2 * math.pi * hbar * c / (100e9 * eV))):
        x = hbar * (2 * math.pi / lam) / (2 * mP() * c)
        p(f"{label:20s}: speed excess over c = {0.5 * x * x:.1e}  (identical in every direction)")
    p("BUT a superfluid carries only compression (longitudinal) waves: no transverse light. See r02.")
    p("")
    p("Density dent needed for light to slow/bend exactly as in GR (wave speed ~ sqrt(density)):")
    for label, M, R in (("Sun surface", Msun, Rsun), ("Earth surface", Mearth, Rearth)):
        p(f"  {label:14s}: delta_rho/rho = -4GM/(r c^2) = {-4 * G0 * M / (R * c * c):.2e}  (must fall as 1/r)")
    r_e, r_m = 1.496e11, 2.279e11
    dt = 2 * (2 * G0 * Msun / c ** 3) * math.log(4 * r_e * r_m / Rsun ** 2)
    p(f"Shapiro delay, Earth-Mars radar grazing the Sun (round trip): {dt * 1e6:.0f} microseconds (measured effect)")

    # ---------------- Q3 ----------------
    p.section("Q3  Range: healing length needed for long-range gravity, and extra dimensions")
    for label, L in (("1 kiloparsec", 3.086e19), ("1 megaparsec", 3.086e22),
                     ("LIGO graviton-mass bound", hbar * c / (1.27e-23 * eV))):
        m = hbar / (math.sqrt(2) * c * L)
        p(f"range >= {label:26s} ({L:.1e} m) -> grain mass <= {m:.1e} kg = {m * c * c / eV:.1e} eV"
          f" ({m / mP():.0e} x Planck mass)")
    for D in (3, 4, 5):
        p(f"D = {D} space dimensions: force ~ 1/r^{D - 1}; stable planetary orbits: "
          f"{'yes' if D == 3 else 'no (Ehrenfest 1917)'}")

    # ---------------- Q4 ----------------
    p.section("Q4  Particles as trapped ripples obey special relativity (sine-Gordon chain, c = 1)")
    speeds = [0.0, 0.3, 0.6, 0.8, 0.9, 0.95, 0.99]
    shrink, gam = [], []
    for v in speeds:
        run = sine_gordon(v)
        t, pos, slope, E = run[:, 0], run[:, 1], run[:, 2], run[:, 3]
        vel = np.polyfit(t[5:], pos[5:], 1)[0]
        g = 1 / math.sqrt(1 - v * v)
        shrink.append(slope[-1] / 2)
        gam.append(g)
        p(f"v = {v:4.2f}c: measured speed {vel:.3f}  width shrink {slope[-1] / 2:.3f}  Lorentz gamma {g:.3f}"
          f"  energy/8 {E[-1] / 8:.3f}")
    p("(at 0.99c the kink is ~3 grains wide and lattice effects appear: the graininess shows)")
    push = sine_gordon(0.0, f=0.05, T=60.0)
    t, pos = push[:, 0], push[:, 1]
    vv = np.abs(np.gradient(pos, t))
    for tt in (10, 25, 40, 55):
        i = np.argmin(abs(t - tt))
        Ft = 2 * math.pi * 0.05 * t[i] / 8
        p(f"constant push, t = {t[i]:4.1f}: speed {vv[i]:.3f}c   Newton {Ft:.2f}c   relativity {Ft / math.sqrt(1 + Ft * Ft):.3f}c")

    # ---------------- figures ----------------
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    for (V0, (r, rho, k)), col in zip(dents.items(), (S1, S2, S3)):
        axs[0].plot(r, rho, color=col, label=f"source strength {V0:g}")
        axs[1].semilogy(r, np.clip((1 - rho) * r, 1e-14, None), color=col, label=f"source {V0:g}: tail e$^{{{k:.3f}r}}$")
    axs[0].axhline(1.0, color=MUTED, ls="--", lw=1)
    axs[0].text(9.8, 1.02, "background density", ha="right", va="bottom", color=INK_2, fontsize=9)
    axs[0].set(xlim=(0, 10), ylim=(0, 1.12), xlabel="distance r (healing lengths)", ylabel="substrate density",
               title="Dent never rises above background (no 'high point')")
    axs[0].legend(loc="lower right")
    r_mid, rho_mid, _ = dents[3.5]
    level = (1 - rho_mid[np.argmin(abs(r_mid - 3))]) * 3      # a 1/r dent keeps (depth x r) constant
    axs[1].axhline(level, color=MUTED, ls="--", lw=1)
    axs[1].text(29, level * 2.2, "a 1/r dent (needed for gravity) would be flat here", ha="right", va="bottom",
                color=INK_2, fontsize=9)
    axs[1].set(xlim=(0, 30), ylim=(1e-13, 3), xlabel="distance r (healing lengths)", ylabel="dent depth x r",
               title="Stronger source = deeper, NOT longer range")
    axs[1].legend(loc="lower left")
    fig.tight_layout()
    save_fig(fig, NAME, "dent_vs_source")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    vv_line = np.linspace(0, 0.995, 300)
    axs[0].plot(vv_line, 1 / np.sqrt(1 - vv_line ** 2), color=S1, label="Einstein: Lorentz factor")
    axs[0].plot(speeds, shrink, "o", color=S2, ms=8, label="trapped ripple in the chain (simulated)")
    axs[0].set(xlabel="speed (fraction of the chain's wave speed)", ylabel="shrink factor",
               ylim=(0.8, 8), title="Moving ripple-particles contract exactly as relativity says")
    axs[0].annotate("lattice effect: particle only ~3 grains wide", xy=(0.99, shrink[-1]), xytext=(0.35, 5.5),
                    arrowprops=dict(arrowstyle="->", color=INK_2), fontsize=9, color=INK_2)
    axs[0].legend(loc="upper left")
    F = 2 * math.pi * 0.05 / 8
    tl = np.linspace(0, 60, 300)
    axs[1].plot(tl, F * tl / np.sqrt(1 + (F * tl) ** 2), color=S1, label="relativity")
    axs[1].plot(tl, F * tl, color=S2, ls="--", label="Newton")
    axs[1].plot(t[::4], vv[::4], "o", color=S3, ms=5, label="simulated ripple-particle")
    axs[1].axhline(1.0, color=MUTED, ls=":", lw=1.2)
    axs[1].text(1, 1.03, "wave speed of the medium (c)", color=INK_2, fontsize=9)
    axs[1].set(xlim=(0, 60), ylim=(0, 1.6), xlabel="time pushed (chain units)", ylabel="speed / c",
               title="Pushed steadily, it never reaches c")
    axs[1].legend(loc="upper left")
    fig.tight_layout()
    save_fig(fig, NAME, "relativity_from_ripples")
    plt.close(fig)

    p.save()


if __name__ == "__main__":
    main()
