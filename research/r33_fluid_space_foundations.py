"""
r33 - The fluid-space idea in equations, and a check that the equations are right
(LAB_NOTEBOOK.md entry E45, test F1)

Question (user): "lets work out the math for the fluid space idea ... first its a super fluide like matter or soemthing
and its in hyper dimentionas and we as an observers can only see and interact in 3d ... we will test ideas and things based
on that if they support or not we show thru calculations, formulations, simulations".

Model (the "fluid-space" model, FS): the medium is a superfluid with order parameter psi(x, t) obeying the Gross-Pitaevskii
equation
        i hbar d psi/dt = [ -hbar^2 nabla^2 / 2m + g |psi|^2 - mu ] psi ,
in D spatial dimensions (D = 3 for a medium without hyper-dimensions, D = 4 with one extra dimension; observers see a 3D slice).
Madelung form psi = sqrt(n) exp(i theta), velocity v = (hbar/m) grad theta:
        d n/dt + div(n v) = 0 ,        m dv/dt = - grad( g n + m v^2/2 + Q ) ,   Q = -(hbar^2/2m) nabla^2 sqrt(n) / sqrt(n).
Linearising about n0 gives the Bogoliubov dispersion
        omega^2 = c^2 k^2 + (hbar k^2 / 2m)^2 = c^2 k^2 (1 + k^2 xi^2 / 2) ,   c = sqrt(g n0 / m),  xi = hbar / (sqrt(2) m c).
Low-energy phonons obey a Lorentz-invariant wave equation with c as the "speed of light" (the acoustic metric, Unruh 1981);
the dispersion is superluminal above k ~ 1/xi, the first correction being v_g / c - 1 = (3/4)(k xi)^2.

Method:
  A. Simulate the GP equation (split-step Fourier, 1D) with a small density ripple of wavenumber k, measure its oscillation
     frequency, and compare with the Bogoliubov formula.  This validates the equations and the code used in r34-r36.
  B. Map the model to Planck units (c_s = c, xi = alpha l_P): constituent mass, and the arrival-time delay of a TeV photon
     over a gigaparsec that the (3/4)(k xi)^2 correction would cause, against timing sensitivities of 1-100 s.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, mP, save_fig, style  # noqa: E402

NAME = "r33_fluid_space_foundations"
GPC = 3.0857e25                     # metres


def gp_mode_frequency(k, length=64.0, n_grid=512, dt=0.005, t_end=80.0, eps=1.0e-3):
    """Units hbar = m = g = n0 = 1, so c = 1 and xi = 1/sqrt(2).  Start from density n0 (1 + eps cos kx) with zero
    phase; the cosine amplitude of the density then oscillates as eps cos(omega t).  Returns the fitted omega."""
    x = np.arange(n_grid) * length / n_grid
    kk = 2.0 * np.pi * np.fft.fftfreq(n_grid, d=length / n_grid)
    psi = np.sqrt(1.0 + eps * np.cos(k * x)).astype(complex)
    half_kinetic = np.exp(-0.5j * dt * 0.5 * kk ** 2)
    steps = int(round(t_end / dt))
    every = 10
    times, amp = [], []
    for s in range(steps + 1):
        if s % every == 0:
            times.append(s * dt)
            amp.append(2.0 * np.mean((np.abs(psi) ** 2 - 1.0) * np.cos(k * x)))
        psi = np.fft.ifft(half_kinetic * np.fft.fft(psi))
        psi *= np.exp(-1j * dt * (np.abs(psi) ** 2 - 1.0))
        psi = np.fft.ifft(half_kinetic * np.fft.fft(psi))
    omega_guess = math.sqrt(k * k + 0.25 * k ** 4)
    popt, _ = curve_fit(lambda t, a, w: a * np.cos(w * t), np.array(times), np.array(amp), p0=(eps, omega_guess))
    return popt[1]


def photon_delay_seconds(xi, energy_ev=1.0e13, distance=GPC):
    """Arrival delay of a photon of the given energy over the distance, for v_g/c - 1 = (3/4)(k xi)^2."""
    k_xi = energy_ev * eV * xi / (hbar * c)
    return distance / c * 0.75 * k_xi ** 2


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. Is the Bogoliubov dispersion right?  A direct simulation of the superfluid equation")
    # ------------------------------------------------------------------------------------------------------
    p("Units hbar = m = g = n0 = 1 (c = 1, xi = 1/sqrt(2)); box 64, 512 points, split-step Fourier, dt = 0.005, T = 80.")
    p("Initial state: density ripple of relative size 1e-3 at wavenumber k; the fitted oscillation frequency is omega_sim.")
    xi = 1.0 / math.sqrt(2.0)
    ks = [2.0 * math.pi * j / 64.0 for j in (2, 4, 8, 16, 24, 32, 48)]
    rows = []
    p(f"    {'k':>6s} {'k xi':>6s} {'omega_sim':>10s} {'omega_Bogoliubov':>17s} {'error':>8s} {'omega_phonon (c k)':>19s}")
    for k in ks:
        w_sim = gp_mode_frequency(k)
        w_bog = math.sqrt(k * k + 0.25 * k ** 4)
        rows.append((k, w_sim, w_bog))
        p(f"    {k:6.3f} {k * xi:6.2f} {w_sim:10.5f} {w_bog:17.5f} {abs(w_sim / w_bog - 1):8.1e} {k:19.5f}")
    worst = max(abs(r[1] / r[2] - 1) for r in rows)
    sound_only_miss = max(abs(r[0] / r[2] - 1) for r in rows)
    p(f"    => the simulation reproduces the Bogoliubov formula to {worst:.1e} at every k; pure sound (omega = c k) misses by up to "
      f"{sound_only_miss:.0%} at k xi = {ks[-1] * xi:.1f}.")

    # ======================================================================================================
    p.section("B. If the medium's healing length is a Planck length (c_s = c)")
    # ------------------------------------------------------------------------------------------------------
    p("xi = hbar / (sqrt(2) m c) fixes the constituent mass, m = m_P / (sqrt(2) alpha) for xi = alpha l_P:")
    for alpha in (1.0, 5.0):
        p(f"    alpha = {alpha:.0f}: xi = {alpha * lP():.2e} m, m = {mP() / (math.sqrt(2) * alpha):.2e} kg = {mP() / (math.sqrt(2) * alpha) * c ** 2 / eV / 1e9:.2e} GeV")
    p("Superluminal dispersion, v_g / c - 1 = (3/4)(k xi)^2: delay of a 10 TeV photon over 1 Gpc,")
    p(f"    {'xi (m)':>12s} {'delay (s)':>12s}")
    for xi_val in (lP(), 1e-30, 1e-28, 1e-27, 1e-26):
        p(f"    {xi_val:12.2e} {photon_delay_seconds(xi_val):12.2e}")
    xi_1s = (hbar * c / (1.0e13 * eV)) * math.sqrt(1.0 * c / (0.75 * GPC))
    xi_100s = xi_1s * 10.0
    delay_planck = photon_delay_seconds(lP())
    p(f"    a timing precision of 1 s probes xi ~ {xi_1s:.1e} m and 100 s probes xi ~ {xi_100s:.1e} m; a Planck-length medium")
    p(f"    (xi = {lP():.2e} m) gives {delay_planck:.1e} s, {1.0 / delay_planck:.0e} times below the 1 s sensitivity.")
    p("    A medium that is NOT Planck-sized is testable: xi above ~1e-28 m would already be visible in TeV timing.")
    p("    Not tested here: the matter particles' own dispersion. In He-3 each species has its own 'speed of light' and")
    p("    making them all equal to 1e-15 is a fine-tuning (E9, open problem 2); a single superfluid does not provide it.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F1a: the superfluid equation has phonons with Bogoliubov dispersion",
         f"CONFIRMED by simulation to {worst:.1e}; sound alone misses by up to {sound_only_miss:.0%}"),
        ("F1b: a Planck-length superfluid conflicts with observed Lorentz invariance",
         f"NO CONFLICT, NO TEST: delay {delay_planck:.1e} s against 1-100 s sensitivity (xi < ~{xi_100s:.0e} m is allowed)"),
        ("F1c: one medium gives one light cone for everything",
         "NOT PROVIDED: only phonons are Lorentz invariant by construction; other species need their own tuning"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<72s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 5.0))

    ax = axs[0]
    kf = np.linspace(0.01, 5.0, 300)
    ax.plot(kf, np.sqrt(kf ** 2 + 0.25 * kf ** 4), color=S1, lw=2.0, label="Bogoliubov formula")
    ax.plot(kf, kf, color=MUTED, ls="--", lw=1.2, label="pure sound, ω = c k")
    ax.plot([r[0] for r in rows], [r[1] for r in rows], "o", color=S2, ms=7, label="simulation of the superfluid equation")
    ax.set(xlabel="wavenumber k (units of 1/healing length × √2)", ylabel="frequency ω (units of c/ξ × 1/√2)",
           title="Ripples in the simulated superfluid follow the Bogoliubov law")
    ax.legend(loc="upper left", fontsize=9)

    ax = axs[1]
    xs = np.geomspace(lP(), 1e-25, 200)
    ax.plot(xs, [photon_delay_seconds(x_) for x_ in xs], color=S1, lw=2.0)
    ax.axhspan(1.0, 100.0, color=S3, alpha=0.15, lw=0)
    ax.axvline(lP(), color=MUTED, ls=":", lw=1.2)
    ax.set(xscale="log", yscale="log", xlim=(1e-36, 1e-25), ylim=(1e-16, 1e6), xlabel="healing length ξ of the medium (m)",
           ylabel="delay of a 10 TeV photon over 1 Gpc (s)",
           title="Planck-size medium: delay far below what timing can see")
    ax.text(2.5e-36, 3e-14, "Planck length", fontsize=9, color=INK_2)
    ax.text(2e-35, 8.0, "timing sensitivity 1–100 s", fontsize=9, color=S3)
    ax.text(3e-30, 3e-12, "(3/4)(Eξ/ħc)² × D/c", fontsize=9, color=S1)

    fig.tight_layout()
    save_fig(fig, NAME, "foundations")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
