"""
r47 - From the lattice first law toward Einstein's equation: the entanglement temperature near a cut  (LAB_NOTEBOOK.md entry E48, tests R1-R4)

Question (queue item from E47): "repeat the first-law test for a region with a horizon (a Rindler wedge on a lattice) where K is the boost energy, and compare delta S with
the energy change".  r43 verified delta S = delta<K> for a lattice scalar with a matter lump, but the step to Einstein's equation (Jacobson 1995) needs more: for a region
bounded by a Rindler horizon the modular Hamiltonian must be the boost generator K = 2 pi int x T_00 dx (Bisognano-Wichmann): the local 'entanglement temperature' at distance x from the
cut is T(x) = 1/(2 pi x) (the Unruh temperature of an observer at proper acceleration 1/x), so that  delta S = delta Q / T  with delta Q the energy of the matter.

Test on a free scalar chain H = (1/2) sum [pi_i^2 + (phi_{i+1} - phi_i)^2 + m^2 phi_i^2], m^2 = 1e-3 (correlation length 32 sites), region A = an interval of L = 24 sites; the right end is
the cut.  Near the cut an interval of length L has the exact conformal boost profile 2 pi x (1 - x/L).
  R1. The vacuum modular Hamiltonian K = (1/2) phi^T A phi + (1/2) pi^T B pi, computed in 110-digit arithmetic from the exact infinite-chain covariances.  (A first attempt in double precision
      gave B_ii = 2 pi x only within 1.5 sites and then flattened: 13 of the 24 entanglement-spectrum values nu - 1/2 are below 1e-12, and the near-cut elements turned out to depend on the
      precision floor.  That attempt is reported in E48 and replaced by this one.)
  R2. Locality: how close is K to the local boost form near the cut?
  R3. Clausius relation: a small matter lump (mass bump) at distance d inside A changes the entropy by delta S (computed with the exact first law, delta S = delta<K0> = (1/2) Tr(A dX) + (1/2) Tr(B dP),
      with dX, dP the exact covariance changes of the chain); its energy delta E in A is the change of the vacuum Hamiltonian density summed over A.  Is delta S / delta E = 2 pi d (1 - d/L)?
  R4. What this does and does not establish.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r47_entanglement_temperature_rindler"
N_SITES, M2, L_REG = 600, 1.0e-3, 24
CENTRE = N_SITES // 2
A_LO, A_HI = CENTRE - L_REG // 2, CENTRE + L_REG // 2          # region A = sites A_LO .. A_HI - 1 ; the cut is between sites A_HI - 1 and A_HI


def covariances(bump):
    k = np.zeros((N_SITES, N_SITES))
    idx = np.arange(N_SITES)
    k[idx, idx] = 2.0 + M2 + bump
    k[idx[:-1], idx[:-1] + 1] = -1.0
    k[idx[:-1] + 1, idx[:-1]] = -1.0
    w, v = np.linalg.eigh(k)
    return 0.5 * (v / np.sqrt(w)) @ v.T, 0.5 * (v * np.sqrt(w)) @ v.T


def sym_power(a, pw):
    w, v = np.linalg.eigh(a)
    return (v * w ** pw) @ v.T


def modular_double(x_a, p_a, floor):
    xh = sym_power(x_a, 0.5)
    nu2, o = np.linalg.eigh(xh @ p_a @ xh)
    nu = np.sqrt(np.maximum(nu2, 0.25 + floor))
    eps = np.log((nu + 0.5) / (nu - 0.5))
    xmh = sym_power(x_a, -0.5)
    f = (np.sqrt(nu)[:, None] * o.T) @ xmh
    g = ((1.0 / np.sqrt(nu))[:, None] * o.T) @ xh
    return f.T @ np.diag(eps) @ f, g.T @ np.diag(eps) @ g, nu, eps


def vacuum_modular_mp(dps=110, n_k=9000):
    """Vacuum modular Hamiltonian of an interval of L sites of the INFINITE chain with mass^2 = M2, in dps-digit arithmetic.  X_r = (1/2) int dk/2pi cos(kr)/w, P_r = (1/2) int dk/2pi cos(kr) w,
    w = sqrt(m^2 + 2 - 2 cos k): the trapezoid rule on the periodic analytic integrand converges like exp(-n_k * 0.0316) for m^2 = 1e-3 (n_k = 9000: ~ 1e-123).
    Returns (A, B as float arrays, S in nats, nu - 1/2 levels as mp numbers, eps levels as floats)."""
    mp.mp.dps = dps
    m2 = mp.mpf(M2)
    cs = [mp.cos(-mp.pi + 2 * mp.pi * n / n_k) for n in range(n_k)]
    wk = [mp.sqrt(m2 + 2 - 2 * c) for c in cs]
    vecs = [[mp.mpf(1)] * n_k, list(cs)]
    for r in range(2, L_REG):
        vecs.append([2 * cs[n] * vecs[-1][n] - vecs[-2][n] for n in range(n_k)])
    xr = [sum(v / w for v, w in zip(vecs[r], wk)) / (2 * n_k) for r in range(L_REG)]
    pr = [sum(v * w for v, w in zip(vecs[r], wk)) / (2 * n_k) for r in range(L_REG)]
    xa = mp.matrix(L_REG, L_REG)
    pa = mp.matrix(L_REG, L_REG)
    for i in range(L_REG):
        for j in range(L_REG):
            xa[i, j] = xr[abs(i - j)]
            pa[i, j] = pr[abs(i - j)]

    def mpower(mat, pw):
        e, q = mp.eigsy(mat)
        return q * mp.diag([e[i] ** pw for i in range(L_REG)]) * q.T

    xh, xmh = mpower(xa, mp.mpf(1) / 2), mpower(xa, -mp.mpf(1) / 2)
    e2, q2 = mp.eigsy(xh * pa * xh)
    nu = [mp.sqrt(e2[i]) for i in range(L_REG)]
    half = mp.mpf(1) / 2
    eps = [mp.log((n + half) / (n - half)) for n in nu]
    f = mp.diag([mp.sqrt(n) for n in nu]) * q2.T * xmh
    g = mp.diag([1 / mp.sqrt(n) for n in nu]) * q2.T * xh
    e_mat = mp.diag(eps)
    a_mat = f.T * e_mat * f
    b_mat = g.T * e_mat * g
    ent = sum((n + half) * mp.log(n + half) - (n - half) * mp.log(n - half) for n in nu)
    to_np = lambda m: np.array([[float(m[i, j]) for j in range(L_REG)] for i in range(L_REG)])
    order = sorted(range(L_REG), key=lambda i: eps[i])
    return to_np(a_mat), to_np(b_mat), float(ent), [nu[i] - half for i in order], [float(eps[i]) for i in order]


def energy_density(x, p):
    """<h_i> for the vacuum chain H0 (the bond (i, i+1) energy is split half-half between its two sites)."""
    n = x.shape[0]
    dens = 0.5 * np.diag(p) + 0.5 * M2 * np.diag(x)
    bond = np.zeros(n)
    for i in range(n - 1):
        e = 0.5 * (x[i, i] - 2.0 * x[i, i + 1] + x[i + 1, i + 1])
        bond[i] += 0.5 * e
        bond[i + 1] += 0.5 * e
    return dens + bond


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    p(f"Interval of {L_REG} sites in a chain with m^2 = {M2:g} (correlation length {1 / math.sqrt(M2):.0f} sites); the cut is the right end of the interval.  Finite chain for the lump responses: {N_SITES} sites.")

    # ======================================================================================================
    p.section("R1. Is the vacuum modular Hamiltonian a boost generator near the cut?")
    # ------------------------------------------------------------------------------------------------------
    a_mp, b_mp, ent_mp, nuhalf, eps_mp = vacuum_modular_mp()
    x0, p0 = covariances(np.zeros(N_SITES))
    region = slice(A_LO, A_HI)
    a_d, b_d, nu_d, eps_d = modular_double(x0[region, region], p0[region, region], 1e-14)
    p(f"    110-digit vacuum entropy of the interval S = {ent_mp:.6f} nats; entanglement-spectrum levels eps (lowest 10): " + ", ".join(f"{e:.1f}" for e in eps_mp[:10]) + f"; highest {eps_mp[-1]:.0f}.")
    p(f"    {sum(1 for v in nuhalf if v < mp.mpf('1e-12'))} of {L_REG} values nu - 1/2 are below 1e-12 (smallest {mp.nstr(min(nuhalf), 3)}): double precision cannot resolve them, 110 digits can.")
    d_idx = np.arange(1, 11)                         # site j = L - d (counting from the left end of A), distance d - 1/2 from the cut
    dist = d_idx - 0.5
    diag_mp = np.array([b_mp[L_REG - d, L_REG - d] for d in d_idx])
    diag_d = np.array([b_d[L_REG - d, L_REG - d] for d in d_idx])
    bw = 2 * math.pi * dist * (1 - dist / L_REG)
    p(f"    {'distance d - 1/2':>17s} {'B_ii (110 digits)':>18s} {'B_ii (double)':>14s} {'2 pi x (1 - x/L)':>17s} {'110-digit / BW':>15s} {'B_ii / (2 pi x)':>16s}")
    for dd, bb, bd_, bwv in zip(dist, diag_mp, diag_d, bw):
        p(f"    {dd:17.1f} {bb:18.5f} {bd_:14.5f} {bwv:17.5f} {bb / bwv:15.4f} {bb / (2 * math.pi * dd):16.4f}")
    slope_b, icpt_b = np.polyfit(dist[:6], diag_mp[:6], 1)
    p(f"    => against the exact interval profile the 110-digit B_ii deviates by at most {np.max(np.abs(diag_mp / bw - 1)):.1%} over distances 0.5 to 9.5 sites (lattice/mass corrections ~ few %).")
    p(f"       Linear fit over the first 6 sites: B_ii = {slope_b:.4f} x distance + {icpt_b:.4f}; Bisognano-Wichmann: slope 2 pi = {2 * math.pi:.4f} (slope is {slope_b / (2 * math.pi) - 1:+.1%} off, and the profile curves by the factor 1 - x/L).")
    p(f"       The double-precision attempt departs from the exact profile by up to {np.max(np.abs(diag_d / bw - 1)):.0%}: the precision floor, not the physics, limited it.")
    off_a = np.array([a_mp[L_REG - d - 1, L_REG - d] for d in d_idx[:-1]])
    bw_bond = 2 * math.pi * d_idx[:-1] * (1 - d_idx[:-1] / L_REG)
    p(f"    gradient bonds: -A_(i,i+1) / [2 pi x (1 - x/L)] = " + ", ".join(f"{-o / b:.3f}" for o, b in zip(off_a[:6], bw_bond[:6])) + f" (x = 1..6): the same boost profile for the gradient energy.")

    # ======================================================================================================
    p.section("R2. How local is K?")
    # ------------------------------------------------------------------------------------------------------
    def beta_site(jj):                               # site index jj inside the interval (0 .. L-1); distance to the cut = L - jj - 1/2
        x = L_REG - jj - 0.5
        return 2 * math.pi * x * (1 - x / L_REG)

    a_loc = np.zeros((L_REG, L_REG))
    b_loc = np.zeros((L_REG, L_REG))
    for jj in range(L_REG):
        b_loc[jj, jj] = beta_site(jj)
        a_loc[jj, jj] += M2 * beta_site(jj)
    for jj in range(L_REG - 1):
        bond_b = 2 * math.pi * (L_REG - jj - 1.0) * (1 - (L_REG - jj - 1.0) / L_REG)   # the bond lies at distance L - jj - 1 from the cut
        a_loc[jj, jj] += bond_b
        a_loc[jj + 1, jj + 1] += bond_b
        a_loc[jj, jj + 1] -= bond_b
        a_loc[jj + 1, jj] -= bond_b
    p(f"    {'window':>22s} {'kinetic part B':>16s} {'gradient part A':>17s} {'off-diagonal share of B':>25s}")
    for width in (4, 8, 12):
        near = slice(L_REG - width, L_REG)
        rel_b = np.linalg.norm((b_mp - b_loc)[near, near]) / np.linalg.norm(b_mp[near, near])
        rel_a = np.linalg.norm((a_mp - a_loc)[near, near]) / np.linalg.norm(a_mp[near, near])
        off_b = np.linalg.norm(b_mp[near, near] - np.diag(np.diag(b_mp[near, near]))) / np.linalg.norm(b_mp[near, near])
        p(f"    {'last ' + str(width) + ' sites':>22s} {rel_b:16.3f} {rel_a:17.3f} {off_b:25.3f}")
        if width == 8:
            rel_b8, rel_a8, off_b8 = rel_b, rel_a, off_b
    p("    (relative Frobenius deviation from the exact local conformal boost form 2 pi x (1 - x/L); the off-diagonal share of B vanishes for a strictly local generator.)")

    # ======================================================================================================
    p.section("R3. Clausius relation: delta S = delta Q / T(x), T(x) = 1 / (2 pi x (1 - x/L))")
    # ------------------------------------------------------------------------------------------------------
    p("  R3a. Localised heat.  Deposit energy as random kicks in a Gaussian profile v (width 1.2 sites) at distance d from the cut: kinetic heat dP = s^2 v v^T (energy s^2 |v|^2 / 2), or potential/gradient heat")
    p("       dX = s^2 v v^T (energy s^2 v^T K0 v / 2, K0 = -Laplacian + m^2).  These are valid mixed states, first order in s^2; delta S = (1/2) Tr(A dX) + (1/2) Tr(B dP) is the exact first law.")
    p(f"       {'d':>5s} {'T^-1 BW = 2 pi d (1-d/L)':>26s} | {'kinetic: dS/dE':>15s} {'ratio':>7s} | {'potential: dS/dE':>17s} {'ratio':>7s}")
    kmat = np.zeros((N_SITES, N_SITES))
    idx_all = np.arange(N_SITES)
    kmat[idx_all, idx_all] = 2.0 + M2
    kmat[idx_all[:-1], idx_all[:-1] + 1] = -1.0
    kmat[idx_all[:-1] + 1, idx_all[:-1]] = -1.0
    heat_rows = []
    for d in (1.5, 2.5, 3.5, 4.5, 5.5, 7.5, 9.5):
        i_c = A_HI - d - 0.5
        v_full = np.exp(-0.5 * ((np.arange(N_SITES) - i_c) / 1.2) ** 2)
        v_full /= np.linalg.norm(v_full)
        v = v_full[region]
        inv_t = 2 * math.pi * d * (1 - d / L_REG)
        ds_k = 0.5 * float(v @ b_mp @ v)                       # per unit s^2
        de_k = 0.5 * float(v @ v)
        ds_p = 0.5 * float(v @ a_mp @ v)
        de_p = 0.5 * float(v_full @ kmat @ v_full)
        heat_rows.append((d, inv_t, ds_k / de_k, ds_p / de_p))
        p(f"       {d:5.1f} {inv_t:26.3f} | {ds_k / de_k:15.3f} {ds_k / de_k / inv_t:7.3f} | {ds_p / de_p:17.3f} {ds_p / de_p / inv_t:7.3f}")
    hr = np.array(heat_rows)
    rk, rp = hr[:, 2] / hr[:, 1], hr[:, 3] / hr[:, 1]
    p(f"       => entropy per unit heat = 1/T(x) = 2 pi x (1 - x/L) to within {max(np.max(np.abs(rk - 1)), np.max(np.abs(rp - 1))):.0%} for kinetic and potential heat at all distances 1.5-9.5: Clausius with the Unruh/Rindler")
    p("          temperature profile (T = 1/(2 pi x) near a cut), for the exact first law and the exact 110-digit K0.")
    p("")
    p("  R3b. A change of the Hamiltonian: a matter lump (mass bump).")
    lam, sigma = 1.0e-4, 1.2
    p(f"    Matter lump: mass^2 raised by {lam:g} exp(-(i - i0)^2 / (2 sigma^2)), sigma = {sigma} sites, centre at distance d from the cut inside the interval.")
    p("    delta S = delta<K0> = (1/2) Tr(A dX) + (1/2) Tr(B dP): exact first law with the 110-digit K0 (the first law itself was verified to 0.2 % in r43, where the entropy can be computed directly).")
    p("    delta S_BW = sum_i beta(x_i) delta h_i (delta h_i = change of the vacuum-chain energy density in the new state); delta S_loc applies the local boost form of K to the exact covariance changes.")
    p(f"    {'d':>5s} {'delta S':>12s} {'delta S_loc':>12s} {'delta S_BW':>12s} {'S_loc/S':>8s} {'S_BW/S':>8s} {'net energy':>12s} {'sum |delta h|':>14s}")
    h0 = energy_density(x0, p0)
    rows = []
    xs_site = L_REG - np.arange(L_REG) - 0.5
    beta_vec = 2 * math.pi * xs_site * (1 - xs_site / L_REG)
    for d in (1.5, 2.5, 3.5, 4.5, 5.5, 7.5, 9.5):
        i0 = A_HI - d - 0.5
        bump = lam * np.exp(-0.5 * ((np.arange(N_SITES) - i0) / sigma) ** 2)
        x1, p1 = covariances(bump)
        dxa, dpa = x1[region, region] - x0[region, region], p1[region, region] - p0[region, region]
        dk = 0.5 * float(np.trace(a_mp @ dxa) + np.trace(b_mp @ dpa))
        dk_loc = 0.5 * float(np.trace(a_loc @ dxa) + np.trace(b_loc @ dpa))
        dh = (energy_density(x1, p1) - h0)[region]
        ds_bw = float(np.sum(beta_vec * dh))
        rows.append((d, dk, dk_loc, ds_bw, float(np.sum(dh)), float(np.sum(np.abs(dh)))))
        p(f"    {d:5.1f} {dk:12.3e} {dk_loc:12.3e} {ds_bw:12.3e} {dk_loc / dk:8.3f} {ds_bw / dk:8.3f} {np.sum(dh):12.3e} {np.sum(np.abs(dh)):14.3e}")
    arr = np.array(rows)
    r_loc = arr[:, 2] / arr[:, 1]
    r_bw = arr[:, 3] / arr[:, 1]
    p(f"    => for a mass bump the exact first-law entropy change ({arr[0, 1]:.1e} to {arr[-1, 1]:.1e}) hardly depends on where the lump is (correlation length {1 / math.sqrt(M2):.0f} sites > interval {L_REG} sites):")
    p("       it is carried by the lump's long-range vacuum-polarisation tail, which the local boost form (and the local energy density) do not see: S_loc/S and S_BW/S are far from 1.")
    p("       So the local Clausius relation holds for localised ENERGY (R3a), not for a change of the mass term in a nearly massless field: a matter source in a field with a long correlation length")
    p("       changes the entanglement through the field's nonlocal response.  (In r43, with a correlation length of 10 sites and an 8-site interval, the same effect was local over a few correlation lengths.)")
    p("    The Clausius half is therefore verified for heat; the geometric half (the area change of the horizon, Raychaudhuri) is not on this lattice.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    worst_b = float(np.max(np.abs(diag_mp / bw - 1)))
    verdict = [
        ("R1: the modular Hamiltonian near a cut is the conformal boost generator 2 pi x (1 - x/L)",
         f"{'CONFIRMED' if worst_b < 0.1 else 'NOT CONFIRMED'} in 110-digit arithmetic: B_ii within {worst_b:.1%} of the exact profile for distances 0.5-9.5; the double-precision attempt was off by up to {np.max(np.abs(diag_d / bw - 1)):.0%}"),
        ("R2: K is local near the cut",
         f"largely: within 8 sites the deviation from the local boost form is {rel_b8:.0%} (kinetic), {rel_a8:.0%} (gradient); off-diagonal share of B {off_b8:.0%}"),
        ("R3a: localised heat obeys delta S = delta Q / T with T = 1/(2 pi x (1 - x/L))",
         f"{'CONFIRMED' if max(np.max(np.abs(rk - 1)), np.max(np.abs(rp - 1))) < 0.2 else 'NOT CONFIRMED'} (tolerance 20 %, set after R1 showed the profile itself to be within 9.7 %, the rest being Gaussian smearing and off-diagonal terms): kinetic and potential heat within {max(np.max(np.abs(rk - 1)), np.max(np.abs(rp - 1))):.0%} of 2 pi x (1 - x/L) at d = 1.5-9.5 sites"),
        ("R3b: the same local relation for a mass lump in a nearly massless field",
         f"NO: exact delta S ({arr[0, 1]:.1e} to {arr[-1, 1]:.1e}) is nearly independent of position and the local forms give {r_loc.min():.2f} to {r_loc.max():.2f} of it: the response is nonlocal on scales of the correlation length"),
        ("R4: this derives Einstein's equation",
         "NO: it verifies the Clausius half (entropy per unit energy = 2 pi x distance) for a free scalar on a lattice; the geometric half (horizon area and Raychaudhuri) is not tested"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<80s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 10.0))
    ax = axs[0, 0]
    xx = np.linspace(0, 10, 100)
    ax.plot(dist, diag_mp, "o", color=S1, ms=8, label="B_ii, 110-digit arithmetic")
    ax.plot(dist, diag_d, "x", color=S2, ms=8, mew=2, label="B_ii, double precision")
    ax.plot(xx, 2 * math.pi * xx * (1 - xx / L_REG), color=MUTED, ls="--", lw=1.4, label="2π x (1 − x/L): boost generator of an interval")
    ax.plot(xx, 2 * math.pi * xx, color=MUTED, ls=":", lw=1.2, label="2π x: half-line")
    ax.set(xlabel="distance of the site from the cut (sites)", ylabel="coefficient of ½π² in K", title="The modular Hamiltonian is a boost generator near the cut")
    ax.legend(loc="upper left", fontsize=8.5)

    ax = axs[0, 1]
    ax.plot(hr[:, 0], hr[:, 2], "o", color=S1, ms=8, label="kinetic heat, δS / δE")
    ax.plot(hr[:, 0], hr[:, 3], "s", color=S2, ms=7, label="potential heat, δS / δE")
    ax.plot(xx[1:], 2 * math.pi * xx[1:] * (1 - xx[1:] / L_REG), color=MUTED, ls="--", lw=1.4, label="1/T = 2π d (1 − d/L)")
    ax.set(xlabel="distance d at which the heat is deposited (sites)", ylabel="entropy per unit heat, 1/T", title="Localised heat obeys δS = δQ / T with T = 1/(2π d)")
    ax.legend(loc="upper left", fontsize=8.5)

    ax = axs[1, 0]
    ax.plot(arr[:, 0], -arr[:, 1], "o", color=S1, ms=8, label="−δS (exact first law, 110-digit K₀)")
    ax.plot(arr[:, 0], -arr[:, 2], "s", color=S2, ms=7, label="−δS, local boost form of K")
    ax.plot(arr[:, 0], -arr[:, 3], "^", color=S3, ms=7, label="−Σ β δh (energy density × 1/T)")
    ax.set(xlabel="distance d of the matter lump from the cut (sites)", ylabel="entropy change (nats), sign flipped", title="A mass lump: the exact δS is not local")
    ax.legend(loc="lower left", fontsize=8.5)

    ax = axs[1, 1]
    jj = np.arange(L_REG)
    xs_ = L_REG - 0.5 - jj
    ax.plot(xs_, np.diag(b_mp), "o-", color=S1, ms=4, lw=1.2, label="B_ii, 110 digits (whole interval)")
    ax.plot(xs_, 2 * math.pi * xs_ * (1 - xs_ / L_REG), color=MUTED, ls="--", lw=1.4, label="2π x (1 − x/L)")
    ax.set(xlabel="distance from the right cut (sites)", ylabel="B_ii", ylim=(0, 55), title="Across the whole interval (symmetric about its centre)")
    ax.legend(loc="lower center", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "rindler")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
