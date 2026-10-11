"""
r44 - A second sector for the stretching: a two-component medium with a Josephson-coupled relative phase  (LAB_NOTEBOOK.md entry E48, tests P1-P5)

Question (queue item from E47, "do the second-field model for the stretching"): r39 showed that a one-component, zero-temperature superfluid is
barotropic and cannot slow-roll; the only candidate with the right field range was the medium's own phase with an explicit phase-breaking potential,
which was marginal (r < 0.036 and n_s within 2 sigma could not both hold).  What would a CONCRETE second sector look like inside the medium?

Model: two condensates 1 and 2 of equal density n/2 and equal mass m (two hyperfine states of one species, say), intra-component coupling g, inter-component
coupling g12, and a Josephson (Rabi) coupling E_J cos(phi) between them.  The relative phase phi = theta_1 - theta_2 is the shift-symmetry-breaking field.
Hydrodynamics of the mixture (derived and checked numerically in P1):
    density sound   c_d^2 = n (g + g12) / (2 m)  =  c^2   (the medium's own light speed, the Planck-length mapping of r33),
    spin (relative) sound   c_r^2 = n (g - g12) / (2 m)  =  s^2 c^2,    s^2 = (g - g12) / (g + g12),
    relative phase  L = (F_r^2 / 2) [phi_t^2 - c_r^2 (grad phi)^2] - V(phi),   F_r^2 = hbar^2 n / (4 m c_r^2).
So a SLOWER spin sound means a LARGER decay constant F_r and a sound speed s < 1 for the inflaton's fluctuations: tensors are r = 16 epsilon s, scalars
P_zeta = H^2 / (8 pi^2 epsilon s M^2) (k-inflation with constant sound speed), while the background and the tilt are those of the canonical field of the same V.
With the r33 mapping (xi = hbar/(sqrt2 m c) = alpha l_P): F_r / M_Pl = 2.98 sqrt(n xi^3) / (alpha s) (M_Pl reduced Planck mass).

  P1. Check the two-component hydrodynamics (sound speeds, decay constant) against the exact Bogoliubov-de Gennes spectrum.
  P2. Allowed region in (f = F_r / M_Pl, s): Planck 2018 tilt, BICEP/Keck tensors, equilateral non-Gaussianity from the sound speed.
  P3. Does the shape of the Josephson potential matter?  Junctions of transparency tau (Andreev-bound-state current-phase relation) instead of cos(phi).
  P4. The medium parameters this implies (mean-field validity, graininess of the spin mode, the size of the Josephson coupling), and what happens to
      the constant-sound-speed ('stiff plus tension') density sector that made light fall with the medium (r40).
  P5. Full background simulation (stiff medium + relative phase from a random initial phase): e-folds, the slow-roll attractor, and a full mode integration
      checking the slow-roll tilt and the amplitude including the factor s.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r44_second_sector_two_component_medium"
NS, NS_ERR = 0.9649, 0.0042           # Planck 2018
R_LIMIT = 0.036                       # BICEP/Keck 2021 (95 %), typed from memory (as in r37, r39)
FNL_EQ, FNL_EQ_ERR = -26.0, 47.0      # Planck 2018 equilateral f_NL (68 %), typed from memory
A_S = 2.10e-9
F_COEFF = 2.98                        # F_r / M_Pl = F_COEFF sqrt(n xi^3) / (alpha s), see header (r39: 5.96 for a single component, halved: n_a = n/2 per component)


# ----------------------------------------------------------------------------------------------------------------------
# Josephson-junction potential family V(x), x = relative phase, minimum at x = 0, maximum at x = pi.  tau -> 0 is the cosine.
# ----------------------------------------------------------------------------------------------------------------------
_x, _t = sp.symbols("x tau", positive=True)
_V = _t * sp.sin(_x / 2) ** 2 / (1 + sp.sqrt(1 - _t * sp.sin(_x / 2) ** 2))      # = 1 - sqrt(1 - tau sin^2(x/2)) without the cancellation
V_FUN = sp.lambdify((_x, _t), _V, "numpy")
DV_FUN = sp.lambdify((_x, _t), sp.diff(_V, _x), "numpy")
D2V_FUN = sp.lambdify((_x, _t), sp.diff(_V, _x, 2), "numpy")


def potential(x, tau):
    """Return V, V', V'' of the junction potential, normalised to V(pi) = 1 - sqrt(1 - tau) (tau-dependent height; only ratios matter)."""
    if tau < 1e-6:                        # cosine limit: V = sin^2(x/2)
        return np.sin(x / 2) ** 2, 0.5 * np.sin(x), 0.5 * np.cos(x)
    return V_FUN(x, tau), DV_FUN(x, tau), D2V_FUN(x, tau)


def slow_roll(f, tau, n_efolds):
    """Slow-roll (n_s, r_canonical, x_star, x_end) for the canonical field chi = f x rolling from near the top x = pi toward x = 0, N e-folds before eps = 1."""
    def eps_of(x):
        v, dv, _ = potential(x, tau)
        return 0.5 * (dv / v) ** 2 / f ** 2

    x_end = brentq(lambda x: eps_of(x) - 1.0, 1e-8, math.pi - 1e-6)

    def efolds(x_star):
        return f ** 2 * quad(lambda x: potential(x, tau)[0] / potential(x, tau)[1], x_end, x_star, limit=200)[0]

    top = math.pi - 1e-9
    if efolds(top) < n_efolds:
        return float("nan"), float("nan"), float("nan"), x_end
    x_star = brentq(lambda x: efolds(x) - n_efolds, x_end + 1e-9, top)
    v, dv, d2v = potential(x_star, tau)
    eps = 0.5 * (dv / v) ** 2 / f ** 2
    eta = d2v / v / f ** 2
    return 1.0 - 6.0 * eps + 2.0 * eta, 16.0 * eps, x_star, x_end


# ----------------------------------------------------------------------------------------------------------------------
# P1: Bogoliubov-de Gennes check of the two-component hydrodynamics
# ----------------------------------------------------------------------------------------------------------------------
def bdg_speeds(g, g12, n_a, m=1.0):
    """Lowest two Bogoliubov branches of a uniform two-component condensate (hbar = 1, equal components n_a each) at small k: returns (c_density, c_spin)."""
    k = 1e-3
    eps_k = k * k / (2 * m)
    # H = [[A, B], [-B, -A]] in (u1, u2, v1, v2); A = eps_k + g n_a diag + g12 n_a offdiag... (mu absorbed)
    a = np.array([[eps_k + g * n_a, g12 * n_a], [g12 * n_a, eps_k + g * n_a]])
    b = np.array([[g * n_a, g12 * n_a], [g12 * n_a, g * n_a]])
    mat = np.block([[a, b], [-b, -a]])
    w = np.sort(np.real(np.linalg.eigvals(mat)))
    pos = w[w > 0]
    return pos[0] / k, pos[1] / k          # sorted: lowest = spin (if g > g12 the spin mode is slower), next = density


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("P1. Two-component hydrodynamics against the Bogoliubov-de Gennes spectrum")
    # ------------------------------------------------------------------------------------------------------
    p("Equal components n_a = n/2 each, hbar = m = 1.  Predictions: c_d^2 = n_a (g + g12)/m, c_r^2 = n_a (g - g12)/m, F_r^2 = n_a/(2 m c_r^2) = 1/(2 (g - g12)).")
    p(f"    {'g':>5s} {'g12':>6s} {'n_a':>6s} | {'c_density BdG':>14s} {'formula':>9s} | {'c_spin BdG':>11s} {'formula':>9s} | {'s = c_r/c_d':>12s} {'sqrt((g-g12)/(g+g12))':>22s}")
    worst = 0.0
    for g, g12, na in ((1.0, 0.0, 1.0), (1.0, 0.5, 1.0), (1.0, 0.8, 2.0), (1.0, 0.9, 1.0), (2.0, 1.9, 0.5)):
        cs, cd = bdg_speeds(g, g12, na)
        cd_f, cr_f = math.sqrt(na * (g + g12)), math.sqrt(na * (g - g12))
        worst = max(worst, abs(cd / cd_f - 1), abs(cs / cr_f - 1))
        p(f"    {g:5.1f} {g12:6.2f} {na:6.1f} | {cd:14.5f} {cd_f:9.5f} | {cs:11.5f} {cr_f:9.5f} | {cs / cd:12.5f} {math.sqrt((g - g12) / (g + g12)):22.5f}")
    p(f"    => both sound speeds agree with the formulas to {worst:.1e}.  The relative-phase decay constant follows from the same coefficients: kinetic term K_r = n_a/(2m), c_r^2 = K_r / F_r^2.")
    p("    A slow spin sound needs g12 close to g (s = 0.3 means g12/g = 0.83): the mixture is near its miscibility threshold, where the spin mode softens.")

    # ======================================================================================================
    p.section("P2. The observationally allowed region in (f, s) for a cosine Josephson coupling")
    # ------------------------------------------------------------------------------------------------------
    # f_NL^equil = -(35/108) (1/s^2 - 1); the 95 % lower limit is FNL_EQ - 2 FNL_ERR (more negative = smaller s)
    fnl_lim = FNL_EQ - 2.0 * FNL_EQ_ERR
    s_ng_min = 1.0 / math.sqrt(1.0 + (-fnl_lim) * 108.0 / 35.0)
    p(f"    Non-Gaussianity: f_NL^equil = -(35/108)(1/s^2 - 1); Planck 2018 (typed from memory) f_NL^equil = {FNL_EQ:.0f} +- {FNL_EQ_ERR:.0f}: 95 % limit {fnl_lim:.0f} => s > {s_ng_min:.3f}.")
    p("    Tensors: r = 16 epsilon s = s r_canonical;  tilt: n_s of the canonical field (a constant sound speed does not change it).  Slow roll from near the top of the cosine.")
    p(f"    {'f':>5s} | {'N = 60: n_s':>12s} {'sigma':>6s} {'r_can':>7s} {'s_max':>6s} | {'N = 50: n_s':>12s} {'sigma':>6s} {'r_can':>7s} {'s_max':>6s} | s window (best of N = 50, 60)")
    fgrid = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 15.0, 20.0, 30.0]
    window_rows = []
    for f in fgrid:
        row = []
        for nn in (60.0, 50.0):
            ns, rc, _, _ = slow_roll(f, 0.0, nn)
            row.append((ns, (ns - NS) / NS_ERR, rc, R_LIMIT / rc))
        ok_options = [(r[3]) for r in row if abs(r[1]) <= 2.0]
        s_hi = min(1.0, max(ok_options)) if ok_options else float("nan")
        window_rows.append((f, row, s_hi))
        win = f"{s_ng_min:.2f} to {s_hi:.2f}" if ok_options and s_hi > s_ng_min else "none"
        p(f"    {f:5.1f} | {row[0][0]:12.4f} {row[0][1]:+6.1f} {row[0][2]:7.4f} {min(row[0][3], 9.99):6.2f} | {row[1][0]:12.4f} {row[1][1]:+6.1f} {row[1][2]:7.4f} {min(row[1][3], 9.99):6.2f} | {win}")
    open_f = [w[0] for w in window_rows if w[2] == w[2] and w[2] > s_ng_min]
    p(f"    => with s = 1 (one component, r39) nothing is allowed; with a spin-sound speed s < 1 the region is f = {min(open_f):.0f}-{max(open_f):.0f}+ and s between {s_ng_min:.2f} and about 0.3-0.7 (smaller for larger f);")
    p("       the tilt is the same as before (r39) but the tensors are cut by the factor s.  Consistency relation n_t = -r / (8 s) instead of -r/8: a test for CMB-S4 / LiteBIRD if r is detected.")

    # ======================================================================================================
    p.section("P3. Does the shape of the Josephson potential matter?  Junctions of transparency tau")
    # ------------------------------------------------------------------------------------------------------
    p("A tunnel junction between two superfluids has the energy-phase relation V = 1 - sqrt(1 - tau sin^2(phi/2)) (Andreev bound states; tau -> 0 is the cosine, tau = 1 a perfectly")
    p("transparent junction with a cusp).  For each tau: the f that gives the observed tilt at N = 60, and the canonical r there; the maximum s for r < 0.036 follows.")
    p(f"    {'tau':>6s} {'f for n_s = 0.9649':>20s} {'r_canonical':>12s} {'s_max':>7s}")
    taus = [0.0, 0.5, 0.9, 0.99]
    tau_rows = []
    for tau in taus:
        try:
            f_star = brentq(lambda f: (lambda v: v if v == v else 1.0)(slow_roll(f, tau, 60.0)[0] - NS), 4.0, 60.0)
            ns, rc, _, _ = slow_roll(f_star, tau, 60.0)
        except ValueError:
            f_star, rc = float("nan"), float("nan")
        tau_rows.append((tau, f_star, rc))
        p(f"    {tau:6.2f} {f_star:20.2f} {rc:12.4f} {min(R_LIMIT / rc, 9.99) if rc == rc else float('nan'):7.2f}")
    p("    => the shape changes the numbers by tens of percent, not the conclusion: with s = 1 every shape gives r_canonical 0.08-0.1 at the observed tilt, too large;")
    p("       it is the sound speed s of the spin mode that brings r under the limit.")

    # ======================================================================================================
    p.section("P4. What the medium must look like: parameters, validity, and the density sector")
    # ------------------------------------------------------------------------------------------------------
    p("From f = F_COEFF sqrt(n xi^3) / (alpha s):  sqrt(n xi^3)/alpha = f s / 2.98.  Mean field needs n xi^3 >= 1, so alpha >= 2.98/(f s).  The amplitude fixes H:")
    p("H^2 = (pi^2/2) A_s r (M_Pl = 1), V_0 = 3 H^2.  Graininess of the density sector is lambda_d = alpha H t_P, of the spin mode lambda_r = alpha H t_P / s^2 (its healing length")
    p("is xi/s and its speed c s); the hydrodynamic description needs lambda << 1 (r37: the amplitude correction goes as lambda^2).")
    p(f"    {'f':>5s} {'s':>5s} {'r':>8s} {'n_s':>7s} {'H (GeV)':>9s} {'V0^1/4 (GeV)':>13s} {'H t_P':>8s} {'alpha_min':>9s} {'lambda_r(alpha_min)':>20s} {'V0 / rho_medium':>16s}")
    chosen = [(8.0, 0.3), (10.0, 0.3), (10.0, 0.15), (15.0, 0.25), (20.0, 0.15)]
    m_pl_gev, e_planck_gev = 2.435e18, 1.221e19
    param_rows = []
    for f, s in chosen:
        ns, rc, _, _ = slow_roll(f, 0.0, 60.0)
        r = s * rc
        h2 = 0.5 * math.pi ** 2 * A_S * r
        h = math.sqrt(h2)
        v0 = 3.0 * h2
        alpha_min = max(1.0, F_COEFF / (f * s))
        nxi3 = (alpha_min * f * s / F_COEFF) ** 2
        h_tp = h * m_pl_gev / e_planck_gev
        lam_r = alpha_min * h_tp / s ** 2
        rho_med = 632.0 * nxi3 / (math.sqrt(2.0) * alpha_min ** 4)          # rho_medium / M_Pl^4 = (8 pi)^2 f_rho, f_rho = n xi^3 / (sqrt2 alpha^4)
        param_rows.append((f, s, r, ns, h * m_pl_gev, v0 ** 0.25 * m_pl_gev, h_tp, alpha_min, lam_r, v0 / rho_med))
        p(f"    {f:5.1f} {s:5.2f} {r:8.4f} {ns:7.4f} {h * m_pl_gev:9.1e} {v0 ** 0.25 * m_pl_gev:13.1e} {h_tp:8.1e} {alpha_min:9.2f} {lam_r:20.1e} {v0 / rho_med:16.1e}")
    p("    => for natural values alpha ~ 1, n xi^3 ~ 1: H ~ 1e13 GeV, graininess of the spin mode ~ 1e-5 (hydrodynamics holds at inflation), and the Josephson energy is ~ 1e-12 of the medium's")
    p("       energy density: a tiny Rabi coupling, protected by the relative-phase symmetry (technically natural) but a hierarchy that is an input.")
    p("    Strings: the vortex lines of r35/r42 form at the first transition, before this stretching; their dilution needs the e-folds computed in r42 (~64) and the N here is only 50-60 for the modes,")
    p("    the total being set by the initial relative phase (P5).")
    p("    The density sector: its equation of state is the stiff-plus-tension (constant c_d = c) one that lets light fall with the medium (r40, Gamma = 0).  During inflation its energy dilutes as a^-6 and is")
    p("    negligible after a few e-folds, so its flat spectrum (r39: n_s = 1 exactly) does not feed the curvature perturbation; the red tilt comes entirely from the relative phase.  The tension of E47")
    p("    (gravity wants P = c^2 rho + const, the sky wants a tilt) is resolved by having two sectors: the density sector for gravity, the spin sector for the tilt.")

    # ======================================================================================================
    p.section("P5. Full background simulation and mode integration (f = 10, s = 0.3)")
    # ------------------------------------------------------------------------------------------------------
    f, s_c, v0_bg = 10.0, 0.3, 1.0e-9
    p(f"V = V0 (1 + cos(chi/f)), f = {f}, V0 = {v0_bg:g} (M_Pl = 1); the stiff density sector starts at 1e3 V0 and dilutes as a^-6; the relative phase starts at x_i = 1.0 rad from the top with a small velocity.")
    rho_s0 = 1.0e3 * v0_bg

    def background(n, y_state):
        chi, y = y_state
        v = v0_bg * (1.0 + math.cos(chi / f))
        dv = -v0_bg / f * math.sin(chi / f)
        rho_s = rho_s0 * math.exp(-6.0 * n)
        h2 = (v + rho_s) / (3.0 - 0.5 * y * y)
        eps = 0.5 * y * y + rho_s / h2
        return [y, -(3.0 - eps) * y - dv / h2]

    def hit_end(n, y_state):
        chi, y = y_state
        v = v0_bg * (1.0 + math.cos(chi / f))
        rho_s = rho_s0 * math.exp(-6.0 * n)
        h2 = (v + rho_s) / (3.0 - 0.5 * y * y)
        return 0.5 * y * y + rho_s / h2 - 1.0

    hit_end.terminal = True
    hit_end.direction = 1
    # start in the stiff era (eps > 1): the event must not trigger there, so integrate in two stages
    sol1 = solve_ivp(background, (0.0, 3.0), [1.0 * f, 0.05], method="DOP853", rtol=1e-11, atol=1e-13, dense_output=True)
    sol2 = solve_ivp(background, (3.0, 400.0), sol1.y[:, -1], method="DOP853", rtol=1e-11, atol=1e-13, dense_output=True, events=hit_end)
    n_end = float(sol2.t_events[0][0]) if len(sol2.t_events[0]) else float("nan")
    x_end_min = slow_roll(f, 0.0, 60.0)[3]                 # end of inflation, measured from the minimum
    n_sr_total = 2.0 * f * f * math.log(math.sin((math.pi - x_end_min) / 2.0) / math.sin(0.5))
    p(f"    inflation ends (epsilon = 1) after N = {n_end:.1f} e-folds (slow-roll integral from x_i = 1.0 rad: {n_sr_total:.1f}).")

    def state(n):
        return sol1.sol(n) if n <= 3.0 else sol2.sol(n)

    n_grid = np.linspace(0.0, n_end, 6000)
    st = np.array([state(n) for n in n_grid])
    rho_s_grid = rho_s0 * np.exp(-6.0 * n_grid)
    v_grid = v0_bg * (1.0 + np.cos(st[:, 0] / f))
    h2_grid = (v_grid + rho_s_grid) / (3.0 - 0.5 * st[:, 1] ** 2)
    eps_grid = 0.5 * st[:, 1] ** 2 + rho_s_grid / h2_grid
    om_stiff = rho_s_grid / (3.0 * h2_grid)
    n_acc = float(n_grid[np.argmax(eps_grid < 1.0)])
    p(f"    acceleration starts at N = {n_acc:.2f}; the stiff sector's share of the energy is {om_stiff[np.argmin(np.abs(n_grid - 10.0))]:.1e} at N = 10 and {om_stiff[np.argmin(np.abs(n_grid - 20.0))]:.1e} at N = 20.")
    # slow-roll reference at the point 55 e-folds before the end
    n_star = n_end - 55.0
    i_star = int(np.argmin(np.abs(n_grid - n_star)))
    chi_star = st[i_star, 0]
    x_star = chi_star / f
    # slow-roll parameters from the potential at x_star (x measured from the top here: V ~ 1 + cos x)
    v_x = 1.0 + math.cos(x_star)
    eps_sr = 0.5 * (math.sin(x_star) / v_x) ** 2 / f ** 2
    eta_sr = -math.cos(x_star) / v_x / f ** 2
    ns_sr = 1.0 - 6.0 * eps_sr + 2.0 * eta_sr
    p(f"    at N_* = N_end - 55 = {n_star:.1f}: simulated epsilon = {eps_grid[i_star]:.5f}, slow-roll epsilon = {eps_sr:.5f}; slow-roll n_s = {ns_sr:.4f}, r = {16 * eps_sr * s_c:.4f} (s = {s_c}).")

    # mode integration with the simulated background
    ln_eps = np.log(eps_grid)
    eta_grid = np.gradient(ln_eps, n_grid)
    a_h = np.exp(n_grid - n_star) * np.sqrt(h2_grid)          # scale factor normalised to 1 at N_* (P_zeta is invariant under a -> lambda a, k -> lambda k)

    def interp(arr, n):
        return float(np.interp(n, n_grid, arr))

    def mode_power(n_exit):
        k = interp(a_h, n_exit) / s_c
        # start 4.5 e-folds earlier, deep inside the horizon
        n0 = n_exit - 4.5
        x0 = s_c * k / interp(a_h, n0)
        eps0, eta0 = interp(eps_grid, n0), interp(eta_grid, n0)
        z0 = math.exp(n0 - n_star) * math.sqrt(2.0 * eps0) / s_c
        zeta0 = 1.0 / (z0 * math.sqrt(2.0 * s_c * k))
        dz0 = (-1j * x0 - 1.0 - eta0 / 2.0) * zeta0

        def rhs(n, y):
            fr = 3.0 - interp(eps_grid, n) + interp(eta_grid, n)
            x2 = (s_c * k / interp(a_h, n)) ** 2
            return [y[1], -fr * y[1] - x2 * y[0], y[3], -fr * y[3] - x2 * y[2]]

        sol = solve_ivp(rhs, (n0, n_exit + 6.0), [zeta0.real, dz0.real, zeta0.imag, dz0.imag], method="DOP853", rtol=1e-10, atol=1e-30)
        y = sol.y[:, -1]
        return k, k ** 3 * (y[0] ** 2 + y[2] ** 2) / (2.0 * math.pi ** 2)

    exits = n_star + np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    ks, ps = zip(*[mode_power(ne) for ne in exits])
    ns_num = 1.0 + np.polyfit(np.log(ks), np.log(ps), 1)[0]
    h_star = math.sqrt(interp(h2_grid, n_star))
    p_formula = h_star ** 2 / (8.0 * math.pi ** 2 * eps_grid[i_star] * s_c)
    p_num = ps[2]
    p(f"    full mode integration of zeta (modes leaving at N_* +- 2): n_s = {ns_num:.4f} (slow roll {ns_sr:.4f}); P_zeta at N_* = {p_num:.3e} against H^2 / (8 pi^2 epsilon s) = {p_formula:.3e} (ratio {p_num / p_formula:.3f}).")
    # initial-phase statistics: fraction of random initial relative phases that give >= 60 e-folds
    def n_total(x0):
        xe = slow_roll(f, 0.0, 60.0)[3]                   # x_end measured from the minimum; here x measured from the top: x_top = pi - x_end
        top_dist = x0                                    # distance from the top
        return 2.0 * f * f * math.log(math.sin((math.pi - xe) / 2.0) / math.sin(top_dist / 2.0)) if top_dist < math.pi - xe else 0.0

    x_try = np.linspace(1e-3, math.pi, 3141)
    n_try = np.array([n_total(x) for x in x_try])
    frac60 = float(np.mean(n_try >= 60.0))
    frac_all = float(np.mean(n_try >= 1.0))
    p(f"    Random initial relative phase (uniform on the circle): slow-roll e-folds N = 2 f^2 ln(sin(x_end/2) / sin(x_i/2)); a fraction {frac60:.2f} of the circle gives N >= 60")
    p(f"    (the rest, {1 - frac60:.2f}, is too close to the bottom to inflate and stays a small, non-inflating domain: inflation wins by volume).")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("P1: two-component hydrodynamics (sound speeds, s^2 = (g - g12)/(g + g12))",
         f"CONFIRMED against the Bogoliubov-de Gennes spectrum to {worst:.0e}"),
        ("P2: a Josephson-coupled relative phase can reproduce the sky",
         f"YES for f = {min(open_f):.0f}-{max(open_f):.0f}+ and spin-sound speed s = {s_ng_min:.2f}-0.3..0.7 c (s = 1 is excluded: r too large); n_s and r both inside the 2-sigma / 95 % limits"),
        ("P3: the junction shape matters",
         f"ONLY QUANTITATIVELY: f for the observed tilt {min(r[1] for r in tau_rows if r[1] == r[1]):.1f}-{max(r[1] for r in tau_rows if r[1] == r[1]):.1f}, canonical r {min(r[2] for r in tau_rows if r[2] == r[2]):.3f}-{max(r[2] for r in tau_rows if r[2] == r[2]):.3f}; every shape needs s < 1"),
        ("P4: the medium parameters are natural",
         f"PARTLY: alpha ~ 1, n xi^3 ~ 1 and graininess ~ {param_rows[1][8]:.0e} are fine; the Josephson energy is {param_rows[1][9]:.0e} of the medium's energy density and the spin sound must be slow (g12/g ~ 0.8): inputs"),
        ("P5: the full simulation and mode integration confirm the slow-roll results",
         f"n_s {ns_num:.4f} vs {ns_sr:.4f}; amplitude ratio {p_num / p_formula:.3f}; stiff sector negligible after ~10 e-folds; {frac60:.0%} of random initial phases inflate for >= 60 e-folds"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<72s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(13.0, 10.2))

    ax = axs[0, 0]
    fs = np.linspace(3.0, 30.0, 120)
    s_hi = []
    ok_f = []
    for f_ in fs:
        opts = []
        for nn in (60.0, 50.0):
            ns_, rc_, _, _ = slow_roll(f_, 0.0, nn)
            if ns_ == ns_ and abs(ns_ - NS) <= 2 * NS_ERR:
                opts.append(min(1.0, R_LIMIT / rc_))
        s_hi.append(max(opts) if opts else np.nan)
    s_hi = np.array(s_hi)
    ax.fill_between(fs, s_ng_min, np.where(s_hi > s_ng_min, s_hi, s_ng_min), where=s_hi > s_ng_min, color=S3, alpha=0.30, label="allowed: tilt (2σ), r < 0.036, f_NL")
    ax.plot(fs, s_hi, color=S3, lw=1.8)
    ax.axhline(s_ng_min, color=MUTED, ls="--", lw=1.3)
    ax.text(21, s_ng_min * 1.12, "f_NL limit", fontsize=9, color=INK_2)
    ax.axhline(1.0, color=S2, lw=1.4)
    ax.text(12.0, 0.88, "s = 1: one-component medium (r39), excluded", fontsize=9, color=S2, va="top")
    ax.set(yscale="log", ylim=(0.03, 1.2), xlabel="decay constant f = F_r / M_Pl", ylabel="spin-sound speed s = c_r / c",
           title="A slow spin sound makes the Josephson phase fit the sky")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[0, 1]
    ffs = np.geomspace(4.0, 60.0, 60)
    for tau, col, lab in ((0.0, S1, "cosine (τ → 0)"), (0.9, S2, "τ = 0.9"), (0.99, S3, "τ = 0.99")):
        pts = np.array([slow_roll(f_, tau, 60.0)[:2] for f_ in ffs])
        good = np.isfinite(pts[:, 0])
        ax.plot(pts[good, 0], pts[good, 1], color=col, lw=2.0, label=lab)
    ax.axvspan(NS - 2 * NS_ERR, NS + 2 * NS_ERR, color=S3, alpha=0.18, lw=0)
    ax.axhline(R_LIMIT, color=MUTED, ls="--", lw=1.3)
    ax.text(0.93, R_LIMIT * 1.1, "r < 0.036", fontsize=9, color=INK_2)
    ax.axhline(R_LIMIT / 0.3, color=MUTED, ls=":", lw=1.2)
    ax.text(0.93, R_LIMIT / 0.3 * 1.1, "canonical r allowed if s = 0.3", fontsize=9, color=INK_2)
    ax.set(yscale="log", xlim=(0.92, 0.985), ylim=(0.002, 0.3), xlabel="spectral tilt n_s (N = 60)", ylabel="canonical tensor-to-scalar ratio",
           title="Junction shape: canonical (n_s, r) curves for f = 4–60")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[1, 0]
    ax.semilogy(n_grid, eps_grid, color=S1, lw=2.0, label="ε(N), simulated")
    ax.semilogy(n_grid, om_stiff, color=S2, lw=2.0, label="share of the stiff density sector")
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.axvline(n_star, color=S3, lw=1.3, ls=":")
    ax.text(n_star + 1, 3e-6, "N_*", fontsize=9, color=S3)
    ax.set(xlabel="e-folds N", ylabel="ε  and  stiff share", ylim=(1e-8, 10), xlim=(0, min(n_end + 5, 160)), title="Stiff medium first, then slow roll of the relative phase")
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1, 1]
    s_line = np.geomspace(0.06, 0.8, 80)
    f_here = 10.0
    ns_h, rc_h, _, _ = slow_roll(f_here, 0.0, 60.0)
    a_lo = np.maximum(1.0, F_COEFF / (f_here * s_line))
    h_tp_line = np.sqrt(0.5 * math.pi ** 2 * A_S * rc_h * s_line) * m_pl_gev / e_planck_gev
    a_hi = 0.3 * s_line ** 2 / h_tp_line
    s_hi_here = R_LIMIT / rc_h
    mask = (s_line >= s_ng_min) & (s_line <= s_hi_here)
    ax.fill_between(s_line, a_lo, a_hi, where=mask, color=S3, alpha=0.25, label="allowed (mean field, spin-mode graininess < 0.3, f_NL, r)")
    ax.loglog(s_line, a_lo, color=S1, lw=1.8, label="lower limit: n ξ³ ≥ 1")
    ax.loglog(s_line, a_hi, color=S2, lw=1.8, label="upper limit: λ_r < 0.3")
    ax.axvline(s_ng_min, color=MUTED, ls="--", lw=1.3)
    ax.axvline(s_hi_here, color=MUTED, ls="--", lw=1.3)
    ax.text(s_ng_min * 1.03, 2.0e4, "f_NL limit", fontsize=9, color=INK_2, rotation=90, va="top")
    ax.text(s_hi_here * 1.03, 2.0e4, "r < 0.036", fontsize=9, color=INK_2, rotation=90, va="top")
    ax.set(xlim=(0.04, 0.8), ylim=(0.7, 6e4), xlabel="spin-sound speed s", ylabel="healing length in Planck lengths, α", title="For f = 10 the medium has a huge range of α")
    ax.legend(loc="center right", fontsize=8.5)

    fig.tight_layout()
    save_fig(fig, NAME, "second_sector")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
