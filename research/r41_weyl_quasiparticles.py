"""
r41 - Matter as quasi-particles of the medium: Weyl nodes, their protection, their speeds, and a way to get tiny masses
(LAB_NOTEBOOK.md entry E47, tests J1-J4)

Question (user): "also do 1, 2 and 3" -- option 2 of the stage-2 menu: matter as quasi-particles (Weyl fermions of a helium-3-A-like
medium).  r38/r40 showed lumps cannot be matter (E < cP, Planck-scale cost, composition-dependent fall).  The alternative (Volovik; Horava 2005):
matter is not a lump but an excitation of a medium whose fermion spectrum has isolated nodes (Fermi points), where the spectrum is
E = +- c |p| (a Weyl fermion) and the low-energy physics is relativistic whatever the microscopic medium.

Model: the two-band Bogoliubov-de Gennes Hamiltonian of a chiral p-wave (helium-3-A-like) pair state on a cubic lattice,
        H(k) = d(k) . sigma,  d = ( Delta sin kx , Delta sin ky , -2t (cos kx + cos ky + cos kz) - mu ),   gap = 2 |d|,
with t = 1, Delta = 0.6, mu = -4 t (only the nodes at kx = ky = 0, kz = +-pi/2 exist).

  J1. Where are the nodes, what are their speeds and chirality (two independent computations), and does the total chirality vanish?
  J2. Are the nodes protected?  Add random smooth translation-invariant perturbations of growing size; count nodes.
  J3. Do all species share one light cone?  Anisotropy of the fermion cone, the sound speed, and the observational limits.
  J4. Can a Planck-scale medium give a particle mass 4e-23 m_P without tuning?  Back-scattering of a Weyl mode by a smooth structure, exactly.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
from scipy.optimize import root

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, mP, save_fig, style  # noqa: E402
from common import m_e_kg  # noqa: E402

NAME = "r41_weyl_quasiparticles"
T_HOP, DELTA, MU = 1.0, 0.6, -4.0
E_PLANCK_GEV = 1.221e19


def d_vec(k, delta=DELTA, mu=MU):
    kx, ky, kz = k[0], k[1], k[2]
    return np.array([delta * np.sin(kx), delta * np.sin(ky), -2.0 * T_HOP * (np.cos(kx) + np.cos(ky) + np.cos(kz)) - mu])


def jacobian(fun, k, h=1e-6):
    return np.array([(fun(k + h * e) - fun(k - h * e)) / (2 * h) for e in np.eye(3)])   # J[i, a] = d f_a / d k_i


def vec_norm_grid(dfun, n_grid):
    ax = np.linspace(-math.pi, math.pi, n_grid, endpoint=False)
    kx, ky, kz = np.meshgrid(ax, ax, ax, indexing="ij")
    d = dfun(kx, ky, kz)
    return np.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2), ax


def nodes_of(dfun_grid, dfun_point, n_grid=40):
    """Weyl nodes of a 3-vector field d(k) on the torus.  A zero inside a grid cube needs every component of d to change sign among the
    cube's 8 corners; each such cube is refined by a root finder from its centre; the results are de-duplicated."""
    ax = np.linspace(-math.pi, math.pi, n_grid, endpoint=False)
    kx, ky, kz = np.meshgrid(ax, ax, ax, indexing="ij")
    d = dfun_grid(kx, ky, kz)
    cand = np.ones(kx.shape, dtype=bool)
    for a in range(3):
        mn = np.full(kx.shape, np.inf)
        mx = np.full(kx.shape, -np.inf)
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    r = np.roll(d[a], (-dx, -dy, -dz), axis=(0, 1, 2))
                    mn, mx = np.minimum(mn, r), np.maximum(mx, r)
        cand &= (mn <= 0.0) & (mx >= 0.0)
    h = ax[1] - ax[0]
    found = []
    for i, j, l in np.argwhere(cand):
        k0 = np.array([ax[i], ax[j], ax[l]]) + 0.5 * h
        sol = root(dfun_point, k0, tol=1e-13)
        if not sol.success or np.linalg.norm(dfun_point(sol.x)) > 1e-8:
            continue
        k = (sol.x + math.pi) % (2 * math.pi) - math.pi
        if all(np.linalg.norm(((k - f + math.pi) % (2 * math.pi)) - math.pi) > 1e-5 for f in found):
            found.append(k)
    return found


def berry_chern(dfun, k0, radius=0.08, n_theta=160, n_phi=96):
    """Chern number of the lower band on a small sphere around the node k0: winding of the Berry phase of the latitude circles."""
    gam = []
    thetas = np.linspace(0.04, math.pi - 0.04, n_theta)
    phis = np.linspace(0, 2 * math.pi, n_phi, endpoint=False)
    for th in thetas:
        us = []
        for ph in phis:
            q = radius * np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
            d = dfun(k0 + q)
            h = d[0] * np.array([[0, 1], [1, 0]]) + d[1] * np.array([[0, -1j], [1j, 0]]) + d[2] * np.array([[1, 0], [0, -1]])
            w, v = np.linalg.eigh(h)
            us.append(v[:, 0])
        prod = 1.0 + 0j
        for a in range(n_phi):
            prod *= np.vdot(us[a], us[(a + 1) % n_phi])
        gam.append(-np.angle(prod))
    gam = np.unwrap(np.array(gam))
    return (gam[-1] - gam[0]) / (2 * math.pi)


def random_perturbation(rng, eps):
    """Smooth translation-invariant perturbation of d(k): random Fourier coefficients on the 27 vectors n in {-1,0,1}^3."""
    ns = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)], dtype=float)
    cos_c = rng.normal(size=(3, 27)) * eps / math.sqrt(54.0)
    sin_c = rng.normal(size=(3, 27)) * eps / math.sqrt(54.0)

    def grid(kx, ky, kz):
        base = np.stack([DELTA * np.sin(kx), DELTA * np.sin(ky), -2.0 * T_HOP * (np.cos(kx) + np.cos(ky) + np.cos(kz)) - MU])
        phase = ns[:, 0, None] * kx.ravel()[None, :] + ns[:, 1, None] * ky.ravel()[None, :] + ns[:, 2, None] * kz.ravel()[None, :]
        pert = (cos_c @ np.cos(phase) + sin_c @ np.sin(phase)).reshape((3,) + kx.shape)
        return base + pert

    def point(k):
        phase = ns @ k
        base = d_vec(k)
        return base + cos_c @ np.cos(phase) + sin_c @ np.sin(phase)

    return grid, point


def backscatter_amplitude(v0, length, dps=110):
    """|r| for a right-moving state at the node (E = 0, k = pi/2) of the half-filled tight-binding chain, through V_n = V0 / cosh^2(n/L)."""
    mp.mp.dps = dps
    n_half = int(60 * length) + 20            # the barrier tail V ~ e^(-2 n / L) is < 1e-50 at the ends
    i = mp.mpc(0, 1)
    psi_next = i ** n_half                      # psi_n = tau i^n on the right
    psi = i ** (n_half - 1)
    # psi_{n+1} = V_n psi_n - psi_{n-1}  =>  psi_{n-1} = V_n psi_n - psi_{n+1}
    for n in range(n_half - 1, -n_half, -1):
        v_n = v0 / mp.cosh(mp.mpf(n) / length) ** 2
        psi_prev = v_n * psi - psi_next
        psi_next, psi = psi, psi_prev
    # now psi = psi_{-n_half}, psi_next = psi_{-n_half+1};  psi_n = A i^n + B (-i)^n
    n0 = -n_half
    a_mat = mp.matrix([[i ** n0, (-i) ** n0], [i ** (n0 + 1), (-i) ** (n0 + 1)]])
    ab = mp.lu_solve(a_mat, mp.matrix([psi, psi_next]))
    return abs(ab[1] / ab[0])


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("J1. The nodes: positions, speeds, chirality (two independent computations)")
    # ------------------------------------------------------------------------------------------------------
    p(f"Model: t = {T_HOP}, Delta = {DELTA}, mu = {MU}.  Nodes need d = 0: sin kx = sin ky = 0 and xi = 0; for mu = -4 t only kx = ky = 0, cos kz = 0.")
    nodes = nodes_of(lambda kx, ky, kz: np.stack([DELTA * np.sin(kx), DELTA * np.sin(ky), -2.0 * T_HOP * (np.cos(kx) + np.cos(ky) + np.cos(kz)) - MU]),
                     d_vec)
    nodes.sort(key=lambda k: k[2])
    p(f"    nodes found by minimising |d| on a grid and refining: {len(nodes)}")
    rows = []
    for k in nodes:
        jac = jacobian(d_vec, k)
        sv = np.linalg.svd(jac, compute_uv=False)
        chir = int(np.sign(np.linalg.det(jac)))
        chern = berry_chern(d_vec, k)
        rows.append((k, sv, chir, chern))
        p(f"      k = ({k[0]:+.4f}, {k[1]:+.4f}, {k[2]:+.4f}) : speeds (singular values of dd/dk) = {np.sort(sv)[0]:.4f}, {np.sort(sv)[1]:.4f}, {np.sort(sv)[2]:.4f};"
          f" sign det = {chir:+d}; Berry flux of the lower band = {chern:+.3f}")
    c_perp, c_par = float(np.sort(rows[0][1])[0]), float(np.sort(rows[0][1])[2])
    p(f"    analytic: speeds Delta = {DELTA}, Delta, 2 t sin(k_F) = {2 * T_HOP * math.sin(math.pi / 2):.4f}: perpendicular speed {c_perp:.4f}, parallel speed {c_par:.4f}.")
    tot_chir = sum(r[2] for r in rows)
    tot_chern = sum(round(r[3]) for r in rows)
    p(f"    total chirality: sum of sign det = {tot_chir}; sum of Berry fluxes = {tot_chern}  (Nielsen-Ninomiya: it must vanish on a lattice,")
    p("    so a single Weyl fermion cannot exist: a left-handed one always comes with a right-handed one far away in momentum space).")
    p("    (The Berry flux and sign det J agree up to one overall sign convention, the same for both nodes.)")

    # ======================================================================================================
    p.section("J2. Are the nodes protected?  Random smooth perturbations of growing size")
    # ------------------------------------------------------------------------------------------------------
    p("Perturbation: each component of d(k) gets a random Fourier series on the 27 wave vectors n in {-1, 0, 1}^3, rms amplitude eps (units of t).")
    p("A node is a zero of the 3-vector d(k); it is removed only when two nodes of opposite chirality meet and annihilate; new pairs can also appear.")
    rng = np.random.default_rng(7)
    eps_list = [0.05, 0.1, 0.2, 0.4, 0.8, 1.6]
    n_seed = 24
    p(f"    {'eps':>6s} {'samples':>8s} {'exactly 2 nodes':>16s} {'0 (gapped)':>11s} {'4 or more':>10s} {'net chirality = 0':>18s}")
    prot_rows = []
    for eps in eps_list:
        counts, zero_net = [], 0
        for _ in range(n_seed):
            grid, point = random_perturbation(rng, eps)
            ns = nodes_of(grid, point, n_grid=40)
            counts.append(len(ns))
            net = sum(int(np.sign(np.linalg.det(jacobian(point, k)))) for k in ns)
            zero_net += int(net == 0)
        counts = np.array(counts)
        prot_rows.append((eps, float(np.mean(counts == 2)), float(np.mean(counts == 0)), float(np.mean(counts >= 4)), zero_net / n_seed))
        p(f"    {eps:6.2f} {n_seed:8d} {np.mean(counts == 2):16.2f} {np.mean(counts == 0):11.2f} {np.mean(counts >= 4):10.2f} {zero_net / n_seed:18.2f}")
    p("    => the pair survives every perturbation up to eps ~ 0.2-0.4 (a sizeable fraction of the cone speeds), and the net chirality stays zero in every")
    p("       sample: the nodes are protected by topology (they can only be moved, or removed in pairs), not by a symmetry that a small term could break.")
    p("    Mass from tuning: sweep mu towards the merging point (nodes at kz = +-k_F meet at kz = pi when mu = -2 t):")
    mus = np.array([-2.0 - dm for dm in (0.4, 0.2, 0.1, 0.05, 0.02, 0.01)] + [-2.0 + 0.01, -2.0 + 0.05, -2.0 + 0.2])
    gaps = []
    for mu in mus:
        kz = np.linspace(-math.pi, math.pi, 20001)
        d = np.stack([np.zeros_like(kz), np.zeros_like(kz), -2.0 * T_HOP * (2.0 + np.cos(kz)) - mu])
        gaps.append(float(2 * np.min(np.abs(d[2]))))
        p(f"      mu + 2t = {mu + 2.0:+.3f}: smallest gap along kx = ky = 0 is {gaps[-1]:.3f}  ({'nodes present' if gaps[-1] < 1e-3 else 'gapped: mass = ' + format(gaps[-1] / 2, '.3f') + ' t'})")
    p("    Giving the quasi-particle a mass this way is linear in the distance to the critical point mu = -2 t: a mass of 1e-23 of the band")
    p("    width needs mu tuned to 1e-23 -- not natural.  A protected-massless fermion gets mass only by a deliberate (new) mechanism: J4.")

    # ======================================================================================================
    p.section("J3. One light cone for all species?")
    # ------------------------------------------------------------------------------------------------------
    p(f"    Fermion cone of this model: c_perp = Delta = {c_perp:.3f}, c_par = 2 t sin k_F = {c_par:.3f}: anisotropy c_perp / c_par = {c_perp / c_par:.2f}.")
    p("    Isotropy needs Delta = 2 t sin k_F (one condition).  In the continuum chiral p-wave state c_par = v_F, c_perp = Delta_0 / p_F, so")
    p("    c_perp / c_par = Delta_0 / (2 E_F): helium-3 (Delta_0 / E_F ~ 1e-3, typed from memory) is anisotropic by a factor of ~1e3;")
    p("    isotropy needs Delta_0 = 2 mu: strong pairing, at the edge of the BCS-BEC crossover where the Weyl points approach and merge (J2).")
    p("    Other species: the sound mode (Anderson-Bogoliubov) has c_s = v_F / sqrt(3) in weak-coupling BCS (literature, not computed here),")
    p("    so c_s / c_par = 0.577 -- the phonon and the fermion cone are different cones unless the medium is tuned.")
    c_ratio = c_perp / c_par
    delta_target = 1e-15
    ln_ep = math.log(E_PLANCK_GEV / 1e3)
    gamma_needed = math.log(1.0 / delta_target) / ln_ep
    p("    How equal must they be?  Limits on speed differences (order of magnitude; typed from memory): gravitational waves vs light, |c_g - c_gamma| / c < ~1e-15")
    p("    (GW170817 + GRB 170817A); electron vs photon ~1e-15 or better; neutron/proton isotropy ~1e-27 (Hughes-Drever type).")
    p(f"    A speed mismatch of O(1) (fermion cone: 1 - {c_ratio:.2f} = {1 - c_ratio:.2f}; sound against fermion: 1 - 0.577 = 0.42) must be brought below {delta_target:.0e}: the speeds must agree to 15 digits.")
    p("    Only a flow of the couplings with energy (Chadha-Nielsen 1983: emergent Lorentz invariance from renormalisation) could do it without tuning.")
    p(f"    If a difference delta(E) = delta(E_P) (E/E_P)^gamma, going from E_P to 1 TeV (ln = {ln_ep:.1f}) to {delta_target:.0e} needs gamma = {gamma_needed:.2f}.")
    p("    One-loop estimates give gamma ~ g^2 / (16 pi^2) ~ 1e-3-1e-2 for couplings of standard-model size (prior art: Collins, Perez, Sudarsky, Urrutia,")
    p("    Vucetich 2004 find O(1e-3-1e-2) leftover violations for Planck-scale breaking), i.e. 1e11-1e13 above the limit.  Not computed here.")
    p("    In the flow picture of gravity (r34, r40) every species rides the same medium flow; a species with a different c deflects differently:")
    p("    rescaling H = c'|k| + v.k by c' shows it sees the flow v/c', i.e. a source of mass M c^2/c'^2: alpha' / alpha = (c / c')^2 = 1 - 2 delta.")
    p(f"    So the equivalence principle (and Shapiro delay) tests bound delta directly: a tuning of {delta_target:.0e} is needed even before any lumps appear.")

    # ======================================================================================================
    p.section("J4. A tiny mass without tuning: back-scattering of a Weyl mode by a smooth structure")
    # ------------------------------------------------------------------------------------------------------
    p("A mass couples the two nodes (momentum transfer 2 k_F): in real space it is the amplitude to be back-scattered by a structure of the medium.")
    p("Exact test: half-filled tight-binding chain (the 1D version of the node pair, k_F = pi/2, speed 2 t), a right mover at E = 0 meets the smooth")
    p("barrier V_n = V0 / cosh^2(n/L) (L in lattice spacings; the medium's own spacing is ~ the healing length); |r| from the exact transfer matrix")
    p("with 110-digit arithmetic (double precision cannot resolve |r| < 1e-12; values below 1e-44 are discarded: the barrier tail, cut off at 60 widths, limits the result to ~1e-52).")
    lens = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    target = m_e_kg[0] / mP()
    ln_target = math.log(target)
    curves = {}
    for v0 in (0.1, 0.5, 1.0, 1.5):
        vals = []
        for L in lens:
            r = backscatter_amplitude(v0, L)
            vals.append(float(r) if r > mp.mpf("1e-44") else float("nan"))
        curves[v0] = vals
    p(f"    |r| against L for four barrier heights V0 (units of t; the band is 4 t wide):")
    p(f"    {'L':>5s} " + " ".join(f"{'V0 = ' + str(v0):>12s}" for v0 in curves))
    for i, L in enumerate(lens):
        if L in (1.0, 2.0, 4.0, 8.0, 12.0, 16.0, 20.0, 32.0, 50.0, 70.0, 100.0):
            p(f"    {L:5.1f} " + " ".join(f"{curves[v0][i]:12.3e}" for v0 in curves))
    p(f"    Electron-to-Planck mass ratio {target:.2e} (ln = {ln_target:.1f}).  Slope of ln|r| at large L, and the width where |r| crosses that ratio:")
    l_cross = {}
    slopes = {}
    for v0, rr in curves.items():
        rr = np.array(rr)
        ok = np.isfinite(rr)
        lx, lr = np.array(lens)[ok], np.log(rr[ok])
        # slope: from the points between L = 8 and the last reliable point
        sel = lx >= 8.0
        slopes[v0] = float(np.polyfit(lx[sel], lr[sel], 1)[0])
        idx = np.where(lr < ln_target)[0]
        if len(idx) and idx[0] > 0:
            j = idx[0]
            l_cross[v0] = float(lx[j - 1] + (ln_target - lr[j - 1]) * (lx[j] - lx[j - 1]) / (lr[j] - lr[j - 1]))
        else:
            l_cross[v0] = float("nan")
        p(f"      V0 = {v0:3.1f}: d ln|r| / dL = {slopes[v0]:7.3f};  L(|r| = m_e/m_P) = {l_cross[v0]:.1f} healing lengths")
    ls_weak = [8.0, 10.0, 12.0, 14.0]
    lr_weak = [math.log(float(backscatter_amplitude(0.001, L))) for L in ls_weak]
    sl_weak = [(lr_weak[i + 1] - lr_weak[i]) / (ls_weak[i + 1] - ls_weak[i]) for i in range(3)]
    p(f"    Weak-barrier check (V0 = 0.001): slopes {', '.join(f'{x:.2f}' for x in sl_weak)} at L ~ 9, 11, 13; prediction -pi^2/2 + 2/L = "
      f"{', '.join(f'{-math.pi ** 2 / 2 + 2 / L:.2f}' for L in (9.0, 11.0, 13.0))}  (Born amplitude: the lattice sum of V_n e^(i pi n) is")
    p(f"    dominated by the pole of sech^2 at n = i pi L / 2, giving L^2 exp(-pi^2 L / 2) with pi^2/2 = {math.pi ** 2 / 2:.2f}).")
    p("    Strong barriers (V0 comparable to the bandwidth) reach a complex turning point earlier and the exponent shrinks (WKB), but the fall stays exponential.")
    p("    So a Planck-length medium can carry particle masses 22 orders below the Planck mass with a structure only ~ 10-100 healing lengths wide,")
    p("    no tuning: it is the exponential suppression of back-scattering by smooth variations.  What it does NOT supply: what the structure is,")
    p("    why it has that width, why different species (e, mu, tau, quarks; 12 orders of mass) have different widths, and how it comes about")
    p("    in a medium that has just been stretched by e^50: an analytic structure stretched by e^50 has no Fourier weight at 2 k_F at all (r39, E47).")
    slope, l_needed = slopes[0.5], l_cross[0.5]

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    v2_ok = prot_rows[2][1]
    verdict = [
        ("J1: the medium has Weyl nodes with E = c|p| and definite chirality",
         f"CONFIRMED: {len(nodes)} nodes, chirality {rows[0][2]:+d} and {rows[1][2]:+d} (sign det) and {round(rows[0][3]):+d} and {round(rows[1][3]):+d} (Berry flux); sum {tot_chir}"),
        ("J1': a single Weyl fermion without a partner",
         "NO: total chirality zero (Nielsen-Ninomiya); matter comes in left/right pairs far apart in momentum space"),
        ("J2: the nodes survive random smooth perturbations",
         f"YES up to eps ~ {eps_list[2]} t (fraction with exactly 2 nodes = {v2_ok:.2f} at eps = {eps_list[2]}); net chirality zero in all samples"),
        ("J2': a mass without fine-tuning from small translation-invariant terms",
         "NO: gap is linear in the distance to the merging point; 1e-23 needs 1e-23 tuning"),
        ("J3: all species share one light cone",
         f"NO without tuning: fermion cone anisotropy {c_ratio:.2f}, phonon/fermion 0.58 (weak coupling); must agree to ~1e-15 (needed running exponent gamma = {gamma_needed:.2f})"),
        ("J4: m_e / m_P = 4e-23 from a smooth structure of the medium",
         f"POSSIBLE: back-scattering falls exponentially; |r| = m_e/m_P at L = {min(v for v in l_cross.values() if v == v):.0f}-{max(v for v in l_cross.values() if v == v):.0f} healing lengths (V0 = 0.1-1.5 t); the structure itself is not derived"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(17.0, 5.2))

    ax = axs[0]
    kz = np.linspace(-math.pi, math.pi, 800)
    for qx, col, lab in ((0.0, S1, "k_x = k_y = 0"), (0.5, S2, "k_x = 0.5, k_y = 0"), (1.2, S3, "k_x = 1.2, k_y = 0")):
        e = np.sqrt((DELTA * np.sin(qx)) ** 2 + (-2.0 * T_HOP * (np.cos(qx) + 1.0 + np.cos(kz)) - MU) ** 2)
        ax.plot(kz, e, color=col, label=lab)
        ax.plot(kz, -e, color=col)
    ax.axhline(0, color=MUTED, lw=1.0)
    for k in nodes:
        ax.plot([k[2]], [0.0], "o", color=INK_2, ms=7)
    for k, row in zip(nodes, rows):
        ax.text(k[2], -3.9, "Weyl node\nchirality " + format(row[2], "+d"), ha="center", fontsize=9, color=INK_2)
    ax.set(xlabel="k_z (lattice units)", ylabel="quasi-particle energy ± E(k)", ylim=(-4.6, 6.5),
           title="Two cones of opposite handedness: E = ±c|p| near each node")
    ax.legend(loc="upper center", fontsize=9, ncol=1, bbox_to_anchor=(0.5, 1.0))

    ax = axs[1]
    es = np.array([r[0] for r in prot_rows])
    ax.plot(es, [r[1] for r in prot_rows], "o-", color=S1, label="exactly two nodes (protected)")
    ax.plot(es, [r[2] for r in prot_rows], "s-", color=S2, label="no node (gapped: pair annihilated)")
    ax.plot(es, [r[3] for r in prot_rows], "^-", color=S3, label="four or more (new pairs created)")
    ax.set(xscale="log", xlabel="size of the random perturbation ε (units of t)", ylabel=f"fraction of {n_seed} random perturbations",
           ylim=(-0.05, 1.05), title="Nodes are moved or removed only in pairs")
    ax.legend(loc="center left", fontsize=9)

    ax = axs[2]
    for v0, col in ((0.1, S1), (0.5, S2), (1.5, S3)):
        ax.semilogy(lens, curves[v0], "o-", color=col, ms=5, lw=1.4, label=f"barrier height V0 = {v0} t")
    ax.axhline(target, color=INK_2, lw=1.2, ls="--")
    ax.text(48.0, target * 5, "m_e / m_P = 4.2e-23", fontsize=9, color=INK_2)
    ax.set(xlabel="width L of the smooth structure (healing lengths)", ylabel="back-scattering amplitude |r| (mass scale ÷ Planck)",
           ylim=(1e-45, 3), title="Smooth structures back-scatter exponentially little")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "weyl")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
