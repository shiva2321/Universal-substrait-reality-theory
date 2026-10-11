"""
r40 - Matter as lumps of the medium, second look: what they would cost, and how they would fall  (LAB_NOTEBOOK.md entry E47, tests H1-H3)

Question (user): option 2 of the stage-2 menu, "matter as ..." and "how would they react" -- matter concentrations and gravity.
r38 showed that lumps of a Gross-Pitaevskii medium (dark solitons, vortex rings, cavities) have E < cP, no rest mass and no persistence.
Here we ask two further questions that decide whether lumps could still be matter:

  H1. Cost.  If the medium has a Planck-length healing length (r33 mapping, xi = alpha l_P), what is the energy of a lump as big as an
      electron's Compton wavelength, compared with the electron's mass?  Same for the smallest lump (size xi).
  H2. Fall.  In the 'gravity is the flow of the medium' picture (r34) the medium's own parcels fall with the flow acceleration g.  How do
      other things fall?  Measured by simulation in 1D: a sound packet and a dark soliton in a plain GP medium, and a sound packet in a
      medium with constant sound speed (logarithmic GP); the added-mass table for a 3D lump of density x * (medium density); and the
      Eotvos-type bound on any dependence of the fall rate on composition.

Idea behind H2 (Galilean equivalence).  A medium accelerating at g relative to an inertial frame is, in its own frame, a medium at rest
in an effective gravity g (hydrostatic: grad P = -rho g).  An object that does not couple to the medium stays inertial: in the medium's frame
it 'falls' at g; in the inertial frame it does not fall at all.  A sound packet in a medium of sound speed c_s(rho) responds to the pressure
gradient by refraction: its acceleration relative to the medium is Gamma g / 2 (along the gradient, 1D) with Gamma = d ln c_s^2 / d ln rho.
So in the inertial frame it falls at g (1 - Gamma/2): equal to the medium's own g only for Gamma = 0, i.e. a constant sound speed (P = c^2 rho + const).
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import dblquad
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit, least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, hbar, c, lP, mP, save_fig, style  # noqa: E402
from common import m_e_kg  # noqa: E402

NAME = "r40_lumps_in_the_flow"
MICROSCOPE_ETA, MICROSCOPE_ERR = 1.5e-15, 2.5e-15       # |eta| (Ti, Pt), stat + syst in quadrature, typed from memory (PRL 2022)
TI_BE, PT_BE, AMU_MEV = 8.72, 7.92, 931.494             # MeV per nucleon (binding energy per nucleon, textbook), atomic mass unit


# ----------------------------------------------------------------------------------------------------------------------
# 1D Gross-Pitaevskii solvers (hbar = m = 1): i psi_t = [-psi''/2 + V psi + f(|psi|^2) psi],  split-step (Strang) in x-space/k-space.
# Stability of the split-step needs dt k_max^2 / 2 < pi (found in r38).
# ----------------------------------------------------------------------------------------------------------------------
class Medium1D:
    def __init__(self, length, n_grid, omega, kind, strength):
        self.L, self.N, self.omega, self.kind, self.g = length, n_grid, omega, kind, strength
        self.x = (np.arange(n_grid) - n_grid // 2) * (length / n_grid)
        self.dx = length / n_grid
        self.k2 = (2.0 * np.pi * np.fft.fftfreq(n_grid, d=self.dx)) ** 2
        self.v = 0.5 * omega ** 2 * self.x ** 2

    def f(self, dens):
        if self.kind == "gp":
            return self.g * dens
        return self.g * np.log(np.maximum(dens, 1e-300))          # logarithmic GP: mu = kappa ln n, c_s^2 = kappa

    def step(self, psi, dt, imaginary=False):
        h = 0.5 * dt
        pot = self.v + self.f(np.abs(psi) ** 2)
        psi = psi * (np.exp(-h * pot) if imaginary else np.exp(-1j * h * pot))
        psi = np.fft.ifft(np.exp(-0.5 * self.k2 * dt * (1.0 if imaginary else 1j)) * np.fft.fft(psi))
        pot = self.v + self.f(np.abs(psi) ** 2)
        return psi * (np.exp(-h * pot) if imaginary else np.exp(-1j * h * pot))

    def ground_state(self, n_particles, psi0, tau=60.0, dtau=0.004):
        psi = psi0.astype(complex)
        for _ in range(int(tau / dtau)):
            psi = self.step(psi, dtau, imaginary=True)
            psi *= math.sqrt(n_particles / (np.sum(np.abs(psi) ** 2) * self.dx))
        return psi

    def peak(self, field, x_guess, window):
        """Position of the maximum of `field` within +-window of x_guess, refined by a parabola through three points."""
        sel = np.where(np.abs(self.x - x_guess) <= window)[0]
        i = sel[np.argmax(field[sel])]
        if 0 < i < self.N - 1:
            y0, y1, y2 = field[i - 1], field[i], field[i + 1]
            den = y0 - 2 * y1 + y2
            if abs(den) > 1e-300:
                return self.x[i] + 0.5 * self.dx * (y0 - y2) / den
        return self.x[i]


def run_phonon(medium, psi_gs, x1, eps, width, t_end, dt, n_samples):
    """Launch a right-moving sound packet (density bump eps * n_gs * gaussian with the matching velocity c_s eps f) and track the maximum of
    delta n = n - n_gs.  Returns (times, positions)."""
    n_gs = np.abs(psi_gs) ** 2
    cs = np.sqrt(n_gs * medium.g) if medium.kind == "gp" else math.sqrt(medium.g) * np.ones_like(n_gs)
    bump = eps * np.exp(-0.5 * ((medium.x - x1) / width) ** 2)
    theta = np.cumsum(cs * bump) * medium.dx
    psi = psi_gs * (1.0 + 0.5 * bump) * np.exp(1j * theta)
    steps = int(t_end / dt)
    every = max(1, steps // n_samples)
    ts, xs = [], []
    guess = x1
    for i in range(steps + 1):
        if i % every == 0:
            dn = np.abs(psi) ** 2 - n_gs
            guess = medium.peak(dn, guess, 4.0 if i else 1.0)
            ts.append(i * dt)
            xs.append(guess)
        psi = medium.step(psi, dt)
    return np.array(ts), np.array(xs)


def run_soliton(medium, psi_gs, x0, t_end, dt, n_samples):
    n_loc = float(np.interp(x0, medium.x, np.abs(psi_gs) ** 2))
    psi = psi_gs * np.tanh((medium.x - x0) * math.sqrt(n_loc * medium.g))
    steps = int(t_end / dt)
    every = max(1, steps // n_samples)
    ts, xs = [], []
    guess = x0
    for i in range(steps + 1):
        if i % every == 0:
            dens = np.abs(psi) ** 2
            guess = medium.peak(-dens, guess, 3.0)             # the soliton is the density minimum near its last position
            ts.append(i * dt)
            xs.append(guess)
        psi = medium.step(psi, dt)
    return np.array(ts), np.array(xs)


def ray_path(c0, gamma, omega, x_start, ts):
    """Right-moving ray in a medium at rest in V = omega^2 x^2 / 2 whose sound speed obeys c^2(x) = c0^2 - Gamma omega^2 x^2 / 2
    (hydrostatic balance d c^2/dx = -Gamma g with g = omega^2 x, Gamma = d ln c_s^2 / d ln rho)."""
    def rhs(t, y):
        return [math.sqrt(max(c0 ** 2 - 0.5 * gamma * omega ** 2 * y[0] ** 2, 1e-6))]
    return solve_ivp(rhs, (ts[0], ts[-1]), [x_start], t_eval=ts, rtol=1e-10, atol=1e-10).y[0]


def local_speed(ts, xs, win=1.2):
    """Packet speed against position: slope of a straight-line fit to the track within +-win time units of each sample; samples after the
    tracker jumps (|dx| > 1 between samples) are dropped."""
    good = np.concatenate([[True], np.abs(np.diff(xs)) < 1.0])
    first_bad = np.argmin(good) if not good.all() else len(good)
    ts, xs = ts[:first_bad], xs[:first_bad]
    xm, v = [], []
    for i in range(len(ts)):
        m = np.abs(ts - ts[i]) < win
        if m.sum() >= 5:
            xm.append(xs[i])
            v.append(np.polyfit(ts[m], xs[m], 1)[0])
    return np.array(xm), np.array(v)


def gamma_from_windows(ts, xs, omega, xc1, xc2, half=4.0):
    """Refraction index Gamma from the packet's local speed in two windows, x near xc1 and x near xc2:
    v1^2 - v2^2 = -Gamma omega^2 (x2^2 - x1^2) / 2.  A speed factor common to both windows (dispersion, pulse shape) cancels to first order."""
    v = []
    for xc in (xc1, xc2):
        m = np.abs(xs - xc) < half
        v.append((np.polyfit(ts[m], xs[m], 1)[0], float(np.mean(xs[m]))))
    (v1, x1), (v2, x2) = v
    return 2.0 * (v1 ** 2 - v2 ** 2) / (omega ** 2 * (x2 ** 2 - x1 ** 2)), v1, v2


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("H1. What a lump costs, against the mass of a real particle (Planck-length medium, xi = alpha l_P)")
    # ------------------------------------------------------------------------------------------------------
    p("Units: n0 = (n xi^3) / xi^3 constituents per volume (n xi^3 >= 1 for mean field), c_s = c, so n0 hbar c is an energy per area and")
    p("(n xi^3) hbar c / xi is the energy scale of anything of size xi.  Wall (dark-soliton sheet) energy per area (4/3) n0 hbar c (r38);")
    p("vortex-ring energy 2 pi^2 hbar^2 n0 R [ln(8R/xi) - 2] / m with m = m_P/(sqrt2 alpha) (r33, r38).")
    m_e_planck = m_e_kg[0] / mP()
    lam_c = hbar / (m_e_kg[0] * c)
    p(f"    electron: m_e = {m_e_kg[0]:.3e} kg = {m_e_planck:.2e} m_P;  Compton wavelength hbar/(m_e c) = {lam_c:.2e} m = {lam_c / lP():.2e} l_P.")
    p(f"    {'lump':>34s} {'size':>12s} {'energy / (m_P c^2)':>20s} {'energy / (m_e c^2)':>20s}")
    rows = []
    for alpha in (1.0, 0.1):
        for nx3 in (1.0, 100.0):
            n0_lp3 = nx3 / alpha ** 3                       # n0 l_P^3
            r_c = lam_c / lP()                              # Compton radius in Planck lengths
            e_wall = 4.0 * math.pi * r_c ** 2 * (4.0 / 3.0) * n0_lp3            # in m_P c^2 (hbar c / l_P = m_P c^2)
            m_over_mp = 1.0 / (math.sqrt(2.0) * alpha)
            e_ring = 2.0 * math.pi ** 2 * n0_lp3 * r_c / m_over_mp * (math.log(8.0 * r_c / alpha) - 2.0)
            e_point = nx3 / alpha                           # a lump of size xi: (n xi^3) hbar c / xi
            rows.append((alpha, nx3, e_point, e_wall, e_ring))
            tag = f"alpha={alpha:g}, n xi^3={nx3:g}"
            p(f"    {'point lump, size xi (' + tag + ')':>34s} {alpha * 1.0:12.1e} {e_point:20.2e} {e_point / m_e_planck:20.2e}")
            p(f"    {'wall of electron size (' + tag + ')':>34s} {lam_c:12.1e} {e_wall:20.2e} {e_wall / m_e_planck:20.2e}")
            p(f"    {'vortex ring, electron radius':>34s} {lam_c:12.1e} {e_ring:20.2e} {e_ring / m_e_planck:20.2e}")
    r_max_wall = math.sqrt(m_e_planck / (4.0 * math.pi * (4.0 / 3.0)))
    p(f"    A wall of energy m_e c^2 (alpha = 1, n xi^3 = 1) would have radius {r_max_wall:.1e} l_P, far below the healing length: no such lump exists.")
    p(f"    The lightest lump of any kind costs >= {rows[0][2] / m_e_planck:.1e} electron masses.  A Planck-scale medium can carry only")
    p("    excitations whose energy is NOT set by the medium's own scale: waves (E = hbar omega, as small as you like) and protected")
    p("    fermion modes (E = c p, masses only through small symmetry breaking, r41); lumps cannot be light.")

    # ======================================================================================================
    p.section("H2a. Falling, measured: sound and a soliton in a 1D medium held in a harmonic trap")
    # ------------------------------------------------------------------------------------------------------
    p("Medium at rest in V = omega^2 x^2 / 2 (effective gravity g(x) = omega^2 x pointing to the centre).  A decoupled mass would oscillate")
    p("at omega (acceleration ratio 1).  Plain GP: i psi_t = [-psi''/2 + V + |psi|^2] psi (hbar = m = 1, c_s^2 = n, Gamma = 1).")
    omega, mu, n_part = 0.1, 8.0, 4.0 * 8.0 * (math.sqrt(2 * 8.0) / 0.1) / 3.0
    gp = Medium1D(120.0, 2048, omega, "gp", 1.0)
    psi0 = np.sqrt(np.maximum(mu - gp.v, 0.0))
    psi_gs = gp.ground_state(n_part, psi0, tau=80.0)
    n_gs = np.abs(psi_gs) ** 2
    h_psi = -0.5 * np.gradient(np.gradient(psi_gs, gp.dx), gp.dx) + (gp.v + n_gs) * psi_gs
    mu_act = float(np.real(np.sum(np.conj(psi_gs) * h_psi) / np.sum(np.abs(psi_gs) ** 2)))
    resid = float(np.max(np.abs(h_psi - mu_act * psi_gs)[np.abs(gp.x) < 30]) / mu_act)
    p(f"    ground state (imaginary-time relaxation): chemical potential {mu_act:.3f}, central density {n_gs[gp.N // 2]:.3f}, Thomas-Fermi radius {math.sqrt(2 * mu_act) / omega:.1f};")
    p(f"      residual of the GP equation {resid:.1e} (relative to mu, |x| < 30).")
    # soliton
    t_s, x_s = run_soliton(gp, psi_gs, 15.0, 100.0, 0.0015, 200)
    fit_s = curve_fit(lambda t, a, w, ph: a * np.cos(w * t + ph), t_s, x_s, p0=[15.0, omega / math.sqrt(2), 0.0])[0]
    ratio_s = (fit_s[1] / omega) ** 2
    p(f"    dark soliton released at rest at x = 15: fit x = A cos(Omega t + phi): A = {fit_s[0]:.2f}, Omega/omega = {abs(fit_s[1]) / omega:.4f}  (1/sqrt2 = {1 / math.sqrt(2):.4f});")
    p(f"      acceleration relative to a decoupled mass = (Omega/omega)^2 = {ratio_s:.3f}   [Busch & Anglin 2000: 1/2 exactly]")
    # sound: a small (linear) pulse; a 5 % pulse runs 8 % fast because a simple wave moves at c (1 + 1.5 dn/n)
    gam_gp_list = []
    for width in (1.5, 3.0):
        t_p, x_p = run_phonon(gp, psi_gs, 0.0, 0.004, width, 14.0, 0.0015, 140)
        gam, v1, v2 = gamma_from_windows(t_p, x_p, omega, 0.0, 22.0)
        gam_gp_list.append(gam)
        p(f"    sound packet, amplitude 0.4 %, width {width:g}: speed {v1:.3f} near x = 0 and {v2:.3f} near x = 22 (sqrt(n): {math.sqrt(n_gs[gp.N // 2]):.3f}, "
          f"{math.sqrt(np.interp(22.0, gp.x, n_gs)):.3f}) -> Gamma = {gam:.3f}")
        if width == 1.5:
            t_p15, x_p15 = t_p, x_p
    t_g20, x_g20 = run_phonon(gp, psi_gs, -20.0, 0.004, 1.5, 14.0, 0.0015, 140)      # same start as the constant-c_s run, for the figure
    keep = np.abs(x_g20) < 28.0
    t_g20, x_g20 = t_g20[keep], x_g20[keep]
    gam_gp, gam_gp_err = float(np.mean(gam_gp_list)), 0.5 * abs(gam_gp_list[0] - gam_gp_list[1])
    p(f"      Gamma = {gam_gp:.2f} +- {gam_gp_err:.2f} (half the spread between the two widths)   [prediction d ln c_s^2 / d ln rho = 1]")
    ratio_p = gam_gp / 2.0
    # constant sound speed
    kappa = 8.0
    a_gauss = -kappa + math.sqrt(kappa ** 2 + omega ** 2)
    lg = Medium1D(240.0, 4096, omega, "log", kappa)
    psi_lg = np.exp(-0.5 * a_gauss * lg.x ** 2) * (2 * a_gauss / math.pi) ** 0.25 * math.sqrt(100.0)
    # stationarity check: the exact Gaussian ground state of the logarithmic medium must not evolve
    psi_t = psi_lg.copy()
    for _ in range(int(5.0 / 0.0015)):
        psi_t = lg.step(psi_t, 0.0015)
    drift = float(np.max(np.abs(np.abs(psi_t) ** 2 - np.abs(psi_lg) ** 2)) / np.max(np.abs(psi_lg) ** 2))
    p(f"    logarithmic medium (mu = kappa ln n, c_s^2 = kappa = {kappa:g} everywhere, Gamma = 0): exact Gaussian ground state n = exp(-a x^2), a = {a_gauss:.3e};")
    p(f"      the solver keeps it stationary to {drift:.1e} over t = 5.")
    gam_lg_list = []
    for width in (1.5, 3.0):
        t_l, x_l = run_phonon(lg, psi_lg, -20.0, 0.004, width, 14.0, 0.0015, 140)
        gam, v1, v2 = gamma_from_windows(t_l, x_l, omega, -2.0, 18.0)
        gam_lg_list.append(gam)
        p(f"    sound packet, amplitude 0.4 %, width {width:g}: speed {v1:.3f} near x = -2 and {v2:.3f} near x = 18 (c_s = {math.sqrt(kappa):.3f}) -> Gamma = {gam:.3f}")
        if width == 1.5:
            t_l15, x_l15 = t_l, x_l
    gam_lg, gam_lg_err = float(np.mean(gam_lg_list)), 0.5 * abs(gam_lg_list[0] - gam_lg_list[1])
    p(f"      Gamma = {gam_lg:.2f} +- {gam_lg_err:.2f}   [prediction 0]; for comparison a plain-GP medium gives {gam_gp:.2f} with the same method.")
    ratio_l = gam_lg / 2.0
    p("    => inertial-frame fall rates in units of the medium's own acceleration g (flow-gravity reading of the trap):")
    p(f"       decoupled mass 0 (it stays inertial);  GP sound 1 - Gamma/2 = {1 - ratio_p:.2f};  GP dark soliton 1 - {ratio_s:.3f} = {1 - ratio_s:.2f};  constant-c_s sound {1 - ratio_l:.2f}.")
    p("       Only a medium with constant sound speed (P = c_s^2 rho + const, the bag/tension equation of state of r39 G1) lets light fall with the")
    p("       medium; r34's uniform-c flows implicitly assumed it.  In plain GP, light would fall at half the medium's rate.")

    # ======================================================================================================
    p.section("H2b. Falling, 3D: the added-mass table (inviscid, incompressible, body much larger than the healing length)")
    # ------------------------------------------------------------------------------------------------------
    p("A sphere of volume V and density x*rho in a flow whose parcels accelerate at g feels the pressure-gradient force rho V g and the")
    p("added-mass reaction C_m rho V (g - a):  x rho V a = rho V g + C_m rho V (g - a)  =>  a / g = (1 + C_m) / (x + C_m).")
    cm_num = dblquad(lambda th, r: 0.5 * (2.0 * math.pi * r ** 2 * math.sin(th)) * ((1.0 / r ** 3) ** 2 * (math.cos(th) ** 2 + 0.25 * math.sin(th) ** 2)),
                     1.0, 400.0, 0.0, math.pi, epsabs=1e-10, epsrel=1e-10)[0]
    # potential of a sphere (R = 1) moving at U = 1: phi = -cos(th) / (2 r^2); |grad phi|^2 = (cos^2 th + sin^2 th / 4) / r^6; T = (rho/2) int |grad phi|^2 dV
    cm_val = 2.0 * cm_num / (4.0 / 3.0 * math.pi)             # T = (1/2) C_m rho V U^2  ->  C_m = 2 T / (rho V)
    p(f"    C_m of a sphere from the kinetic energy of its potential flow (numerical quadrature): {cm_val:.4f}   (exact 1/2).")
    cm = 0.5
    p(f"    {'density of the lump / medium':>30s} {'fall rate a / g':>16s}")
    table = []
    for x in (0.0, 0.5, 1.0, 2.0, 10.0, 1e6):
        table.append((x, (1 + cm) / (x + cm)))
        label = "cavity (x = 0)" if x == 0 else ("neutral parcel (x = 1)" if x == 1 else f"x = {x:g}")
        p(f"    {label:>30s} {(1 + cm) / (x + cm):16.3f}")
    p("    A cavity falls three times as fast as the medium, a heavy lump hardly falls, and only a lump with the density of the medium itself")
    p("    follows the flow.  Fall rate depends on what the object is made of: the equivalence principle fails at order one unless every kind of")
    p("    matter has x = 1 -- i.e. unless matter is not a lump in the medium but an excitation carried by it.")
    d_be = (TI_BE - PT_BE) / AMU_MEV
    slope = abs(-(1 + cm) / (1 + cm) ** 2)
    delta_a = slope * d_be
    bound = math.hypot(MICROSCOPE_ETA, MICROSCOPE_ERR)
    p(f"    Size of the effect if a lump's x tracked its composition only through nuclear binding: Ti vs Pt differ by {TI_BE - PT_BE:.2f} MeV per nucleon = {d_be:.1e} of the mass,")
    p(f"    so delta a / a = |d ln a / dx| delta x = {slope:.2f} x {d_be:.1e} = {delta_a:.1e}.  MICROSCOPE (Ti vs Pt): |eta| = ({MICROSCOPE_ETA:.1e} +- {MICROSCOPE_ERR:.1e}), typed from memory.")
    p(f"    The effect would exceed the measurement by a factor ~{delta_a / bound:.0e}.  (Illustration only: it assumes x responds to binding energy at order one.)")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("H1: a lump as big as an electron is as light as an electron",
         f"NO: wall {rows[0][3] / m_e_planck:.0e} m_e, ring {rows[0][4] / m_e_planck:.0e} m_e, even a size-xi lump {rows[0][2] / m_e_planck:.0e} m_e; a wall of mass m_e would be {r_max_wall:.0e} l_P across"),
        ("H2a: in plain GP, sound falls with the medium",
         f"NO: Gamma = {gam_gp:.2f} +- {gam_gp_err:.2f}; sound and the dark soliton fall at {1 - ratio_p:.2f} and {1 - ratio_s:.2f} of the medium's own rate (predictions 0.5, 0.5)"),
        ("H2a': in a constant-sound-speed medium, sound falls with the medium",
         f"YES: Gamma = {gam_lg:.2f} +- {gam_lg_err:.2f} (prediction 0): the packet keeps its speed c_s and falls at {1 - ratio_l:.2f} of the medium's rate; needs P = c_s^2 rho + const"),
        ("H2b: lumps of any density fall like the medium",
         f"NO: a/g = 3 (cavity) ... 1 (x = 1) ... 0 (heavy); composition dependence ~{delta_a:.0e} vs the measured bound ~{bound:.0e}"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(17.0, 5.2))

    ax = axs[0]
    ax.plot(t_s, x_s, "o", color=S1, ms=3.5, label="dark soliton (simulation)")
    tt = np.linspace(0, 100, 400)
    ax.plot(tt, 15.0 * np.cos(omega / math.sqrt(2) * tt), color=S1, lw=1.2, alpha=0.7, label="cos(ωt/√2)")
    ax.plot(tt, 15.0 * np.cos(omega * tt), color=MUTED, ls="--", lw=1.4, label="decoupled mass (Ω = ω)")
    ax.set(xlabel="time", ylabel="position (trap centre at 0)", ylim=(-19, 19), title="A soliton falls at half a free mass's rate")
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1]
    xg, vg = local_speed(t_g20, x_g20)
    xl, vl = local_speed(t_l15, x_l15)
    ax.plot(xg, vg, "s", color=S2, ms=3.5, label="plain GP medium (simulation)")
    xx = np.linspace(-22, 22, 200)
    ax.plot(xx, np.sqrt(np.interp(xx, gp.x, n_gs)), color=S2, lw=1.3, alpha=0.7, label="√n(x)  (c_s of plain GP)")
    ax.plot(xl, vl, "o", color=S3, ms=3.5, label="constant c_s medium (simulation)")
    ax.axhline(math.sqrt(kappa), color=S3, lw=1.3, alpha=0.7)
    ax.set(xlabel="position of the sound packet (trap centre at 0)", ylabel="speed of the packet", ylim=(2.0, 3.3),
           title="Sound slows with the trap only if c_s depends on density")
    ax.legend(loc="lower center", fontsize=9)

    ax = axs[2]
    xs = np.geomspace(0.01, 100.0, 300)
    ax.plot(xs, (1 + cm) / (xs + cm), color=S1, lw=2.0)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.axvline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.plot([1.0], [1.0], "o", color=S3, ms=9)
    ax.text(1.15, 1.12, "same density as the medium:\nfalls with the medium", fontsize=9, color=S3)
    ax.text(0.011, 2.65, "cavity: 3×", fontsize=9, color=INK_2)
    ax.text(25.0, 0.18, "heavy lump:\nhardly falls", fontsize=9, color=INK_2)
    ax.set(xscale="log", xlabel="density of the lump ÷ density of the medium", ylabel="fall rate ÷ the medium's own acceleration",
           ylim=(0, 3.2), title="A lump falls at a rate set by its density")
    fig.tight_layout()
    save_fig(fig, NAME, "lumps")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
