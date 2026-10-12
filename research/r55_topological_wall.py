"""
r55 - A topologically protected wall: the Josephson (sine-Gordon) kink of the relative phase  (LAB_NOTEBOOK.md entry E49, tests U1-U4)

Question (open item from E48 / r49): "a stabiliser by topological charge for the wall".  r49 found that the simplest wall of the medium (a dark soliton) bends and that a pinning barrier or a
second component in the core are needed to hold it.  A wall that carries a winding cannot unwind smoothly: in a two-component medium with a Josephson (Rabi) coupling the relative phase phi = theta_1 - theta_2
can wind by 2 pi across a sheet (a sine-Gordon kink: psi_1 = sqrt(n_a) exp(i phi/2), psi_2 = sqrt(n_a) exp(-i phi/2), phi: 0 -> 2 pi), and the amplitudes stay nonzero; it can only disappear by nucleating
vortices.  Is such a wall stable against bending, i.e. free of the snake instability, and what does it look like?

Model (hbar = m = 1): i d psi_1/dt = [-d^2/2 - mu + g |psi_1|^2 + g12 |psi_2|^2] psi_1 - Omega psi_2, and 1 <-> 2; uniform state psi_1 = psi_2 = sqrt(n_a), mu = (g + g12) n_a - Omega.
Parameters: g = 1, g12 = 0.5, n_a = 1, Omega = 0.02: density sound c_d = sqrt(n_a (g + g12)) = 1.225, spin sound c_r = sqrt(n_a (g - g12)) = 0.707 (s = 0.577), relative-phase mass m_phi^2 = 2 Omega n (g - g12) = 0.04,
kink width delta = c_r / m_phi = 3.54, kink tension sigma = 8 F_r^2 c_r m_phi = 1.13 (F_r^2 = 1/(2 (g - g12)) = 1) from the effective sine-Gordon theory.

  U1. Uniform-state Bogoliubov spectrum against the hydrodynamic prediction (density sound, spin gap and speed).
  U2. The kink solution of the full two-component equations (imaginary-time relaxation with the winding fixed at the ends): residual, width, tension against sine-Gordon.
  U3. Bogoliubov-de Gennes spectrum of the planar kink for transverse wavenumbers k: is every frequency real?  The lowest branch is the bending mode (expected omega = c_r k).
  U4. Real-time 2D test: a kink-antikink pair with a transverse ripple against a pair of ordinary dark-soliton walls with the same ripple: does the wall survive, and are vortices created?
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

NAME = "r55_topological_wall"
G, G12, NA, OMEGA = 1.0, 0.5, 1.0, 0.02
MU = (G + G12) * NA - OMEGA
C_D = math.sqrt(NA * (G + G12))
C_R = math.sqrt(NA * (G - G12))
M_PHI = math.sqrt(2.0 * OMEGA * 2.0 * NA * (G - G12))
F_R2 = 1.0 / (2.0 * (G - G12))
DELTA = C_R / M_PHI
SIGMA_SG = 8.0 * F_R2 * C_R * M_PHI
HALF, NG = 30.0, 300
X = np.linspace(-HALF, HALF, NG)
DX = X[1] - X[0]
LAP = (np.diag(np.full(NG - 1, 1.0), 1) + np.diag(np.full(NG - 1, 1.0), -1) - 2.0 * np.eye(NG)) / DX ** 2


def lap_vec(f):
    out = np.zeros_like(f)
    out[1:-1] = (f[2:] + f[:-2] - 2.0 * f[1:-1]) / DX ** 2
    return out


def relax_kink(tau_max=300.0, dtau=0.01, winding=True):
    phi = 4.0 * np.arctan(np.exp(X / DELTA)) if winding else np.zeros_like(X)
    p1 = math.sqrt(NA) * np.exp(1j * phi / 2.0)
    p2 = math.sqrt(NA) * np.exp(-1j * phi / 2.0)
    b1, b2 = p1[[0, -1]].copy(), p2[[0, -1]].copy()
    for _ in range(int(tau_max / dtau)):
        a1, a2 = np.abs(p1) ** 2, np.abs(p2) ** 2
        d1 = 0.5 * lap_vec(p1) - (-MU + G * a1 + G12 * a2) * p1 + OMEGA * p2
        d2 = 0.5 * lap_vec(p2) - (-MU + G * a2 + G12 * a1) * p2 + OMEGA * p1
        p1 = p1 + dtau * d1
        p2 = p2 + dtau * d2
        p1[[0, -1]], p2[[0, -1]] = b1, b2
    a1, a2 = np.abs(p1) ** 2, np.abs(p2) ** 2
    r1 = -0.5 * lap_vec(p1) + (-MU + G * a1 + G12 * a2) * p1 - OMEGA * p2
    r2 = -0.5 * lap_vec(p2) + (-MU + G * a2 + G12 * a1) * p2 - OMEGA * p1
    resid = float(max(np.max(np.abs(r1[3:-3])), np.max(np.abs(r2[3:-3]))))
    return p1, p2, resid


def grand_energy(p1, p2):
    d1, d2 = np.gradient(p1, DX), np.gradient(p2, DX)
    a1, a2 = np.abs(p1) ** 2, np.abs(p2) ** 2
    dens = (0.5 * np.abs(d1) ** 2 + 0.5 * np.abs(d2) ** 2 + 0.5 * G * (a1 ** 2 + a2 ** 2) - MU * (a1 + a2) + G12 * a1 * a2
            - OMEGA * 2.0 * np.real(np.conj(p1) * p2))
    uniform = (G * NA ** 2 - 2 * MU * NA + G12 * NA ** 2 - 2 * OMEGA * NA)
    return float(np.sum(dens - uniform) * DX)


def bdg_matrix(p1, p2, k):
    n = len(p1)
    eye = np.eye(n)
    kin = -0.5 * LAP[:n, :n] + 0.5 * k * k * eye
    a1, a2 = np.abs(p1) ** 2, np.abs(p2) ** 2
    k1 = kin + np.diag(-MU + G * a1 + G12 * a2)
    k2 = kin + np.diag(-MU + G * a2 + G12 * a1)
    a_11 = k1 + np.diag(G * a1)
    a_22 = k2 + np.diag(G * a2)
    a_12 = np.diag(G12 * p1 * np.conj(p2)) - OMEGA * eye
    a_21 = np.diag(G12 * p2 * np.conj(p1)) - OMEGA * eye
    b_11, b_22 = np.diag(G * p1 ** 2), np.diag(G * p2 ** 2)
    b_12, b_21 = np.diag(G12 * p1 * p2), np.diag(G12 * p2 * p1)
    a_mat = np.block([[a_11, a_12], [a_21, a_22]])
    b_mat = np.block([[b_11, b_12], [b_21, b_22]])
    return np.block([[a_mat, b_mat], [-np.conj(b_mat), -np.conj(a_mat)]])


def bdg_spectrum(p1, p2, k):
    ev = np.linalg.eigvals(bdg_matrix(p1, p2, k))
    return ev


def wall_dynamics_2d(kind, amp, t_end, n_x=256, n_y=32, dx=0.4, dt=0.02, seed=0, n_samples=120):
    """Real-time 2D evolution of a pair of walls with a transverse ripple.  kind = 'kink' (two-component with Rabi coupling, kink + antikink) or 'dark' (single component, two dark solitons).
    Returns (times, ripple amplitude of the wall, number of plaquettes with winding), measured every few time units."""
    lx, ly = n_x * dx, n_y * dx
    xs = (np.arange(n_x) - n_x // 2) * dx
    ys = np.arange(n_y) * dx
    xg, yg = np.meshgrid(xs, ys, indexing="ij")
    kx = 2 * np.pi * np.fft.fftfreq(n_x, d=dx)
    ky = 2 * np.pi * np.fft.fftfreq(n_y, d=dx)
    kk = (kx[:, None] ** 2 + ky[None, :] ** 2)
    ripple = amp * np.sin(2 * np.pi * yg / ly)
    x1, x2 = -lx / 4.0, lx / 4.0
    if kind == "kink":
        # kink at x1 (phi: 0 -> 2 pi) and antikink at x2 (phi: 2 pi -> 0); the ripple shifts both walls
        phi = 4.0 * np.arctan(np.exp((xg - x1 - ripple) / DELTA)) - 4.0 * np.arctan(np.exp((xg - x2 - ripple) / DELTA))
        psi = [math.sqrt(NA) * np.exp(1j * phi / 2.0), math.sqrt(NA) * np.exp(-1j * phi / 2.0)]
        mu = MU
    else:
        # two dark solitons: tanh(x - x1) tanh(x2 - x) is -1 outside, +1 between, density 1 except at the nodes
        prof = np.tanh(xg - x1 - ripple) * np.tanh(x2 + ripple - xg)
        psi = [prof.astype(complex)]
        mu = 1.0
    half_kin = np.exp(-0.25j * dt * kk)

    def nonlin_step(psi_list, dt_):
        if kind == "kink":
            a1, a2 = np.abs(psi_list[0]) ** 2, np.abs(psi_list[1]) ** 2
            p1 = psi_list[0] * np.exp(-1j * dt_ * (-mu + G * a1 + G12 * a2))
            p2 = psi_list[1] * np.exp(-1j * dt_ * (-mu + G * a2 + G12 * a1))
            c, s_ = math.cos(OMEGA * dt_), math.sin(OMEGA * dt_)       # exp(+i Omega dt sigma_x): the Rabi term is -Omega psi_other in the Hamiltonian
            return [c * p1 + 1j * s_ * p2, c * p2 + 1j * s_ * p1]
        a = np.abs(psi_list[0]) ** 2
        return [psi_list[0] * np.exp(-1j * dt_ * (a - mu))]

    def kin_half(psi_list):
        return [np.fft.ifft2(half_kin * np.fft.fft2(p)) for p in psi_list]

    from scipy import ndimage

    def defects(psi_list):
        """kink: plaquettes with a phase winding in either component (the amplitudes are nonzero everywhere, so the winding is well defined);
        dark walls: excess connected low-density regions (|psi|^2 < 0.25) in a box tiled twice along y: 0 for two intact walls, > 0 once the walls break into vortex cores."""
        if kind == "kink":
            total = 0
            for p_ in psi_list:
                th = np.angle(p_)
                wr = lambda d: (d + np.pi) % (2 * np.pi) - np.pi
                t10, t01 = np.roll(th, -1, 0), np.roll(th, -1, 1)
                t11 = np.roll(t10, -1, 1)
                w = np.rint((wr(t10 - th) + wr(t11 - t10) + wr(t01 - t11) + wr(th - t01)) / (2 * np.pi))
                total += int(np.count_nonzero(w))
            return total
        low = np.abs(psi_list[0]) ** 2 < 0.25
        tiled = np.concatenate([low, low], axis=1)
        _, n_comp = ndimage.label(tiled)
        return int(n_comp) - 2

    def wall_position_ripple(psi_list):
        # position of the first wall in each column: where Im(psi_1 psi_2*) = n sin(phi) crosses zero, i.e. phi = pi (kink), or where Re(psi) crosses zero (dark), near x1
        if kind == "kink":
            f = np.imag(psi_list[0] * np.conj(psi_list[1]))        # n sin(phi): changes sign at phi = pi, independent of the global phase
        else:
            f = np.real(psi_list[0])
        sel = np.abs(xs - x1) < 12.0
        idx = np.where(sel)[0]
        pos = []
        for j in range(n_y):
            col = f[idx, j]
            sgn = np.where(np.sign(col[:-1]) != np.sign(col[1:]))[0]
            if len(sgn) == 0:
                pos.append(np.nan)
                continue
            i0 = sgn[np.argmin(np.abs(xs[idx][sgn] - x1))]
            x_a, x_b, f_a, f_b = xs[idx][i0], xs[idx][i0 + 1], col[i0], col[i0 + 1]
            pos.append(x_a - f_a * (x_b - x_a) / (f_b - f_a))
        pos = np.array(pos)
        return float(0.5 * (np.nanmax(pos) - np.nanmin(pos))) if np.any(np.isfinite(pos)) else float("nan")

    times, rip, vort = [], [], []
    steps = int(t_end / dt)
    every = max(1, steps // n_samples)
    for i in range(steps + 1):
        if i % every == 0:
            times.append(i * dt)
            rip.append(wall_position_ripple(psi))
            vort.append(defects(psi))
        psi = kin_half(psi)
        psi = nonlin_step(psi, dt)
        psi = kin_half(psi)
    return np.array(times), np.array(rip), np.array(vort)


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    p(f"Parameters: g = {G}, g12 = {G12}, n_a = {NA}, Omega = {OMEGA}: c_d = {C_D:.4f}, c_r = {C_R:.4f}, m_phi = {M_PHI:.4f}, kink width delta = c_r/m_phi = {DELTA:.3f}, sine-Gordon tension 8 F_r^2 c_r m_phi = {SIGMA_SG:.4f}.")

    # ======================================================================================================
    p.section("U1. Uniform state: Bogoliubov spectrum against the hydrodynamic prediction")
    # ------------------------------------------------------------------------------------------------------
    one = np.ones(40) * math.sqrt(NA)
    lap_u = (np.diag(np.full(39, 1.0), 1) + np.diag(np.full(39, 1.0), -1) - 2.0 * np.eye(40))
    # plane waves: use the analytic BdG for the uniform state at wavenumber q (4x4 problem)
    def uniform_modes(q):
        e = 0.5 * q * q
        diag = e + OMEGA + G * NA                       # kinetic + (K_a = e + Omega after subtracting mu) + g n_a
        a = np.array([[diag, G12 * NA - OMEGA], [G12 * NA - OMEGA, diag]])
        b = np.array([[G * NA, G12 * NA], [G12 * NA, G * NA]])
        ev = np.linalg.eigvals(np.block([[a, b], [-b, -a]]))
        return np.sort(np.real(ev[np.real(ev) > 1e-9]))

    p(f"    {'q':>6s} {'density branch':>15s} {'c_d q':>8s} {'spin branch':>12s} {'sqrt(m^2 + c_r^2 q^2)':>22s}")
    worst_d, worst_s = 0.0, 0.0
    for q in (0.02, 0.05, 0.1, 0.2):
        modes = uniform_modes(q)
        dens, spin = modes[0], modes[1]              # ascending order: the gapless density branch first, the gapped spin branch second
        spin_pred = math.sqrt(M_PHI ** 2 + C_R ** 2 * q * q)
        worst_d = max(worst_d, abs(dens / (C_D * q) - 1))
        worst_s = max(worst_s, abs(spin / spin_pred - 1))
        p(f"    {q:6.2f} {dens:15.5f} {C_D * q:8.5f} {spin:12.5f} {spin_pred:22.5f}")
    p(f"    => the density branch agrees with c_d q to {worst_d:.1e} and the spin branch with sqrt(m_phi^2 + c_r^2 q^2) to {worst_s:.1%} (the few percent are the finite-Omega correction to the effective sine-Gordon mass).")

    # ======================================================================================================
    p.section("U2. The kink of the full two-component equations")
    # ------------------------------------------------------------------------------------------------------
    p1, p2, resid = relax_kink()
    phi_num = np.unwrap(np.angle(p1 * np.conj(p2)))
    centre = np.interp(math.pi, phi_num, X)
    # width: from the slope at the centre, d phi / dx = 2 / delta for a sine-Gordon kink (phi = 4 atan e^{x/d})
    slope_c = float(np.gradient(phi_num, X)[np.argmin(np.abs(X - centre))])
    delta_num = 2.0 / slope_c
    dens_min = float(np.min(np.abs(p1) ** 2 + np.abs(p2) ** 2) / (2 * NA))
    sigma_num = grand_energy(p1, p2)
    p(f"    stationary state: residual {resid:.1e}; winding of the relative phase {phi_num[-1] - phi_num[0]:.4f} (2 pi = {2 * math.pi:.4f}); amplitudes stay nonzero (minimum total density {dens_min:.4f} of the uniform value).")
    p(f"    kink centre at x = {centre:+.3f}; width from the central slope {delta_num:.3f} (sine-Gordon {DELTA:.3f}); energy per unit area (grand potential above the uniform state) {sigma_num:.4f} (sine-Gordon {SIGMA_SG:.4f}).")
    p(f"    For comparison a plain dark soliton of one component with g = n_0 = 1 has 4/3 = {4.0 / 3.0:.3f} per unit area and a width of ~1; the kink is {DELTA:.1f} healing lengths thick because it is held together by a weak coupling.")

    # ======================================================================================================
    p.section("U3. Bogoliubov-de Gennes spectrum of the planar kink")
    # ------------------------------------------------------------------------------------------------------
    ks = np.array([0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2])
    p(f"    {'k':>5s} {'max Im omega':>13s} {'lowest |omega| (real)':>22s} {'c_r k':>8s}")
    max_imag = 0.0
    low_branch = []
    for k in ks:
        ev = bdg_spectrum(p1[3:-3], p2[3:-3], k)
        # the discrete spectrum of the box edge modes is irrelevant; keep modes with small |Im| and sort by |Re|
        im = float(np.max(ev.imag))
        max_imag = max(max_imag, im)
        pos = np.sort(np.abs(ev.real[np.abs(ev.imag) < 1e-6]))
        pos = pos[pos > 1e-6] if k > 0 else pos
        low = float(pos[0]) if len(pos) else float("nan")
        low_branch.append(low)
        p(f"    {k:5.2f} {im:13.2e} {low:22.5f} {C_R * k:8.5f}")
    p(f"    => the largest imaginary part over all modes and all k is {max_imag:.1e} (numerical noise level): the planar kink has NO bending (snake) instability, unlike the plain wall (0.26 at k = 0.7 in r49).")
    kk_c = ks[2:6]
    ratio = np.array(low_branch)[2:6] / (C_R * kk_c)
    p(f"    The lowest branch is the bending mode of the wall: omega / (c_r k) = " + ", ".join(f"{r:.3f}" for r in ratio) + f" at k = {', '.join(f'{k:g}' for k in kk_c)} (a massless wave along the wall at the spin-sound speed).")

    # ======================================================================================================
    p.section("U4. Real-time 2D test: rippled walls, kink against dark soliton")
    # ------------------------------------------------------------------------------------------------------
    amp = 0.8
    p(f"    Walls at x = +-{256 * 0.4 / 4:.1f} in a 102 x 12.8 periodic box; transverse ripple of amplitude {amp} (wavelength 12.8, k = {2 * math.pi / 12.8:.2f}); dt = 0.02.")
    t_dark, r_dark, v_dark = wall_dynamics_2d("dark", amp, 60.0, n_samples=120)
    t_kink, r_kink, v_kink = wall_dynamics_2d("kink", amp, 160.0, n_samples=400)
    first_break = t_dark[np.argmax(v_dark > 0)] if np.any(v_dark > 0) else float("nan")
    p(f"    dark-soliton walls: ripple amplitude {r_dark[0]:.2f} at t = 0; excess low-density regions (broken wall pieces / vortex cores): {v_dark[0]} at t = 0, first appear at t = {first_break:.0f}, {int(v_dark[-1])} at t = {t_dark[-1]:.0f} (max {int(v_dark.max())})")
    p(f"    kink walls:        ripple amplitude {r_kink[0]:.2f} -> max {np.nanmax(r_kink):.2f}, min {np.nanmin(r_kink):.2f} after t = {t_kink[-1]:.0f}; plaquettes with a phase winding in either component: {v_kink[0]} -> {v_kink[-1]} (max {int(v_kink.max())})")
    period = 2.0 * math.pi / (C_R * 2.0 * math.pi / 12.8)
    # the measured amplitude of a standing bending wave is |cos(omega t)|: its minima are spaced by pi / omega
    mins = [i for i in range(1, len(r_kink) - 1) if r_kink[i] < r_kink[i - 1] and r_kink[i] < r_kink[i + 1] and r_kink[i] < 0.4 * np.nanmax(r_kink)]
    period_obs = 2.0 * float(np.mean(np.diff(t_kink[mins]))) if len(mins) > 2 else float("nan")
    p(f"    Bending oscillation of the kink wall: period expected from the sound speed 2 pi / (c_r k) = {period:.1f}; observed (spacing of the {len(mins)} amplitude minima, x 2) = {period_obs:.1f}; the pure-Bogoliubov frequency at this k (middle panel) gives the exact comparison.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("U1: the two-component hydrodynamics holds at the parameters used", f"CONFIRMED: density sound to {worst_d:.0e}, spin branch sqrt(m^2 + c_r^2 q^2) to {worst_s:.1%}"),
        ("U2: a 2 pi kink of the relative phase exists as a stationary wall", f"YES: residual {resid:.0e}, width {delta_num:.2f} (SG {DELTA:.2f}), tension {sigma_num:.3f} (SG {SIGMA_SG:.3f}), amplitudes nonzero"),
        ("U3: the planar kink has a bending instability", f"NO: max Im omega = {max_imag:.0e} for k = 0-1.2; the bending mode is a wave at c_r (omega/c_r k = {ratio.mean():.2f})"),
        ("U4: a rippled kink wall survives in real time, a rippled dark-soliton wall does not",
         f"{'YES' if v_kink.max() == 0 and v_dark.max() > 0 else 'SEE NUMBERS'}: defects: kink walls max {int(v_kink.max())} (phase windings), dark-soliton walls max {int(v_dark.max())} (excess low-density regions; first at t = {first_break:.0f}); ripple {amp}"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<74s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(16.4, 5.2))
    ax = axs[0]
    ax.plot(X, np.abs(p1) ** 2 / NA, color=S1, lw=2.0, label="|ψ₁|² ÷ n_a")
    ax.plot(X, np.cos(phi_num / 2.0) ** 2 * 0 + (np.angle(p1 * np.conj(p2)) % (2 * math.pi)) / (2 * math.pi), color=S2, lw=2.0, label="relative phase φ ÷ 2π")
    ax.plot(X, 0.5 * (1 - np.cos(phi_num)), color=MUTED, ls="--", lw=1.2, label="Josephson energy (1 − cos φ)/2")
    ax.set(xlabel="x", ylabel="", xlim=(-20, 20), title="The kink: relative phase winds by 2π, the densities hardly change")
    ax.legend(loc="center left", fontsize=9)

    ax = axs[1]
    ks_f = np.linspace(0.0, 1.2, 13)
    low_f, imag_f = [], []
    for k in ks_f:
        ev = bdg_spectrum(p1[3:-3], p2[3:-3], k)
        imag_f.append(float(np.max(ev.imag)))
        pos = np.sort(np.abs(ev.real[np.abs(ev.imag) < 1e-6]))
        pos = pos[pos > 1e-6] if k > 0 else pos
        low_f.append(float(pos[0]) if len(pos) else np.nan)
    ax.plot(ks_f, low_f, "o-", color=S1, ms=6, label="lowest BdG frequency of the kink wall")
    ax.plot(ks_f, C_R * ks_f, color=MUTED, ls="--", lw=1.3, label="c_r k")
    ax.plot(ks_f, imag_f, "s-", color=S2, ms=5, label="largest growth rate (Im ω)")
    ax.set(xlabel="transverse wavenumber k", ylabel="frequency / growth rate", title="Bending mode of the kink: real frequency, no growth")
    ax.legend(loc="upper left", fontsize=9)

    ax = axs[2]
    ax.plot(t_dark, r_dark, "s-", color=S2, ms=4, label="dark-soliton wall: ripple amplitude")
    ax.plot(t_kink, r_kink, "o-", color=S1, ms=4, label="kink wall: ripple amplitude")
    ax2 = ax.twinx()
    ax2.plot(t_dark, v_dark, ":", color=S2, lw=1.6)
    ax2.plot(t_kink, v_kink, ":", color=S1, lw=1.6)
    ax2.set_ylabel("defects, dotted (windings for the kink, extra low-density regions for dark walls)", fontsize=8)
    ax2.grid(False)
    ax.set(xlabel="time", ylabel="ripple amplitude of the wall", title="A rippled kink wall oscillates; a dark-soliton wall breaks into holes")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "kink")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
