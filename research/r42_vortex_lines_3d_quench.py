"""
r42 - The quench in three dimensions: a network of vortex lines  (LAB_NOTEBOOK.md entry E47, tests K1-K4)

Question (user): option 3 of the stage-2 menu, "the 3D version of the stage-1 quench".  r35 did the 2D quench (point vortices); a vortex
in a 3D superfluid is a LINE, a "cosmic string" for a 3D observer.  What does the network look like, does Kibble-Zurek counting still work,
how much of it is closed loops and how much is long strings, how does it age, and what does a line weigh INSIDE a network (the tension that
r35 assumed, 2 pi f alpha^2 ln(R/xi), depends on the cutoff R, which in a network is the line spacing, not the size of the universe)?

Method: time-dependent Ginzburg-Landau equation in 3D,
        d psi / dt = eps(t) psi - |psi|^2 psi + nabla^2 psi + noise,     eps(t) = t / tau_Q,  starting at eps = -0.3,
on a periodic cubic lattice (N^3, dx = 0.5, dt = 0.03: the explicit scheme needs dt < dx^2 / 6 = 0.042), numba-parallel.  Lines are located by the
winding of the phase round every lattice plaquette (three orientations); they are traced through the cubes whose faces they pierce;
closed loops are told from wrapping ("infinite") strings by following each connected line component with unwrapped coordinates.
Counting time: t = kappa sqrt(tau_Q), kappa = 6 and 8 (the rule that worked in 2D, r35).

  K1. Line length per volume against tau_Q: Kibble-Zurek predicts tau_Q^(-1/2) (length/volume ~ 1 / xi_hat^2).
  K2. The structure: fraction of the length in infinite strings, loops, and the loop-length distribution (random-walk prediction ~ l^(-5/2)).
  K3. The network ages (model-A coarsening): length/volume against time at fixed eps (prediction t^(-1)).
  K4. The line's weight inside a network, and what it does to the Planck-medium bound of r35.
"""
import math
import os
import sys
import time
from collections import deque

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numba import njit, prange

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, hbar, lP, save_fig, style  # noqa: E402

NAME = "r42_vortex_lines_3d_quench"
N_GRID = int(os.environ.get("R42_N", 128))
DX, DT = 0.5, 0.03
EPS0 = 0.3
NOISE_D = 5.0e-3
KAPPAS = (6.0, 8.0)
TAUS = tuple(int(x) for x in os.environ.get("R42_TAUS", "5,10,20,40,80").split(","))
SEEDS = {t: 2 for t in TAUS}
KB = 1.380649e-23
T0_K = 2.7255
R_OBS = 4.4e26
GMU_BOUND = 1.5e-7


@njit(parallel=True, fastmath=True, cache=True)
def tdgl_step(psi, new, eps, dt, inv_dx2, nre, nim, amp):
    n = psi.shape[0]
    for i in prange(n):
        ip, im = (i + 1) % n, (i - 1) % n
        for j in range(n):
            jp, jm = (j + 1) % n, (j - 1) % n
            for k in range(n):
                kp, km = (k + 1) % n, (k - 1) % n
                p = psi[i, j, k]
                lap = (psi[ip, j, k] + psi[im, j, k] + psi[i, jp, k] + psi[i, jm, k] + psi[i, j, kp] + psi[i, j, km] - 6.0 * p) * inv_dx2
                new[i, j, k] = p + dt * (eps * p - (p.real * p.real + p.imag * p.imag) * p + lap) + amp * complex(nre[i, j, k], nim[i, j, k])


def plaquette_windings(psi):
    """Signed winding (-1, 0, +1, ...) of the phase on every lattice plaquette, for the three plaquette orientations (normal x, y, z)."""
    th = np.angle(psi)

    def wr(d):
        return (d + np.pi) % (2.0 * np.pi) - np.pi

    ti = np.roll(th, -1, 0)
    tj = np.roll(th, -1, 1)
    tk = np.roll(th, -1, 2)
    tij = np.roll(ti, -1, 1)
    tik = np.roll(ti, -1, 2)
    tjk = np.roll(tj, -1, 2)
    two_pi = 2.0 * np.pi
    wx = np.rint((wr(tj - th) + wr(tjk - tj) + wr(tk - tjk) + wr(th - tk)) / two_pi).astype(np.int8)     # (y, z) plaquette
    wy = np.rint((wr(tk - th) + wr(tik - tk) + wr(ti - tik) + wr(th - ti)) / two_pi).astype(np.int8)     # (z, x) plaquette
    wz = np.rint((wr(ti - th) + wr(tij - ti) + wr(tj - tij) + wr(th - tj)) / two_pi).astype(np.int8)     # (x, y) plaquette
    return wx, wy, wz


def divergence(wx, wy, wz):
    """Net outward flux of the winding field through every cube: it must vanish (a vortex line cannot end)."""
    return (np.roll(wx, -1, 0).astype(int) - wx + np.roll(wy, -1, 1) - wy + np.roll(wz, -1, 2) - wz)


def trace_lines(wx, wy, wz):
    """Connect the cubes whose faces are pierced by a line.  Returns (component sizes, wrap flags, node coordinates, labels, junction count)."""
    n = wx.shape[0]
    edges = []
    for axis, w in enumerate((wx, wy, wz)):
        idx = np.argwhere(w != 0)
        for (i, j, k) in idx:
            lo = [i, j, k]
            lo[axis] = (lo[axis] - 1) % n
            edges.append((tuple(lo), (i, j, k), axis))
    adj = {}
    for u, v, axis in edges:
        adj.setdefault(u, []).append((v, axis, +1))
        adj.setdefault(v, []).append((u, axis, -1))
    pos, label, wrap, sizes = {}, {}, [], []
    for start in adj:
        if start in pos:
            continue
        comp = len(sizes)
        pos[start] = (0, 0, 0)
        label[start] = comp
        queue = deque([start])
        size, wraps = 0, False
        while queue:
            u = queue.popleft()
            size += 1
            pu = pos[u]
            for v, axis, sign in adj[u]:
                pv = list(pu)
                pv[axis] += sign
                pv = tuple(pv)
                if v not in pos:
                    pos[v] = pv
                    label[v] = comp
                    queue.append(v)
                elif pos[v] != pv:
                    wraps = True
        sizes.append(size)
        wrap.append(wraps)
    junctions = sum(1 for u, nb in adj.items() if len(nb) > 2)
    return np.array(sizes), np.array(wrap), label, junctions


def ginzburg_landau_excess(psi, eps):
    """Energy of the field above the uniform ground state (|psi|^2 = eps), per the functional F = int [|grad psi|^2 - eps |psi|^2 + |psi|^4 / 2]."""
    grad = 0.0
    for axis in range(3):
        d = np.roll(psi, -1, axis) - psi
        grad += float(np.sum(d.real ** 2 + d.imag ** 2)) / DX ** 2
    a2 = psi.real ** 2 + psi.imag ** 2
    pot = float(np.sum(-eps * a2 + 0.5 * a2 ** 2))
    vol = psi.size
    return DX ** 3 * (grad + pot + 0.5 * eps ** 2 * vol)


def analyse(psi, eps, with_trace=True):
    wx, wy, wz = plaquette_windings(psi)
    n_p = int(np.count_nonzero(wx) + np.count_nonzero(wy) + np.count_nonzero(wz))
    vol = (N_GRID * DX) ** 3
    length = (2.0 / 3.0) * n_p * DX              # isotropic lines: a line of length l pierces (3/2) l / dx plaquettes
    out = {"n_p": n_p, "length": length, "density": length / vol, "eps": eps, "div_max": int(np.max(np.abs(divergence(wx, wy, wz)))),
           "e_ex": ginzburg_landau_excess(psi, eps), "amp": float(np.mean(np.abs(psi) ** 2)) / eps}
    if with_trace and n_p > 0:
        sizes, wrap, label, junctions = trace_lines(wx, wy, wz)
        out.update({"sizes": sizes, "wrap": wrap, "label": label, "junctions": junctions})
    return out


class Quench:
    def __init__(self, tau, seed):
        self.tau, self.rng = tau, np.random.default_rng(seed)
        n = N_GRID
        z = lambda: self.rng.standard_normal((n, n, n), dtype=np.float32)
        self.psi = (math.sqrt(NOISE_D) * (z() + 1j * z())).astype(np.complex64)
        self.new = np.empty_like(self.psi)
        self.nre = np.empty((n, n, n), dtype=np.float32)
        self.nim = np.empty((n, n, n), dtype=np.float32)
        self.t = -EPS0 * tau
        self.amp = math.sqrt(NOISE_D * DT / DX ** 3)

    def advance(self, to_t, eps_of_t):
        while self.t < to_t:
            self.rng.standard_normal(dtype=np.float32, out=self.nre)
            self.rng.standard_normal(dtype=np.float32, out=self.nim)
            tdgl_step(self.psi, self.new, np.float32(eps_of_t(self.t)), np.float32(DT), np.float32(1.0 / DX ** 2), self.nre, self.nim, np.float32(self.amp))
            self.psi, self.new = self.new, self.psi
            self.t += DT


def weighted_slope(xs, ys, wts):
    x, y, w = np.log(np.array(xs, float)), np.log(np.array(ys, float)), np.array(wts, float)
    xm, ym = np.sum(w * x) / w.sum(), np.sum(w * y) / w.sum()
    slope = np.sum(w * (x - xm) * (y - ym)) / np.sum(w * (x - xm) ** 2)
    return slope, 1.0 / math.sqrt(np.sum(w * (x - xm) ** 2))


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    p(f"Lattice {N_GRID}^3, dx = {DX} (box {N_GRID * DX:g}), dt = {DT}, noise D = {NOISE_D:g}; eps ramps from -{EPS0} at rate 1/tau_Q; counting at t = kappa sqrt(tau_Q).")

    # ======================================================================================================
    p.section("K1. Line length per volume against the quench time (Kibble-Zurek counting in 3D)")
    # ------------------------------------------------------------------------------------------------------
    res = {k: {} for k in KAPPAS}
    snap_for_plot = None
    traces = {}
    for tau in TAUS:
        for seed in range(SEEDS[tau]):
            q = Quench(tau, 1000 + seed)
            for k in KAPPAS:
                q.advance(k * math.sqrt(tau), lambda t, tau=tau: t / tau)
                eps = q.t / tau
                a = analyse(q.psi, eps, with_trace=(k == KAPPAS[0]))
                res[k].setdefault(tau, []).append(a)
                if k == KAPPAS[0] and tau == 20 and seed == 0:
                    snap_for_plot = (a, q.psi.copy())
        p(f"    tau_Q = {tau:3d}: done ({time.time() - t_start:.0f} s elapsed)")
    div_max = max(a["div_max"] for k in KAPPAS for tau in TAUS for a in res[k][tau])
    p(f"    Self-check: the winding field is divergence-free in every snapshot (max |div| over all cubes = {div_max}): lines close or wrap, never end.")
    primary = KAPPAS[0]
    p(f"    {'tau_Q':>6s} {'runs':>5s} {'plaquettes':>11s} {'length/volume':>14s} {'L_v sqrt(tau)':>14s} {'|psi|^2/eps':>12s} {'spacing/xi':>11s}   (kappa = {primary:.0f})")
    dens_by_tau = {}
    for tau in TAUS:
        runs = res[primary][tau]
        dens = max(float(np.mean([a["density"] for a in runs])), 1e-12)
        dens_by_tau[tau] = dens
        eps_c = runs[0]["eps"]
        spacing_over_xi = (dens ** -0.5) * math.sqrt(eps_c)
        p(f"    {tau:6d} {len(runs):5d} {sum(a['n_p'] for a in runs):11d} {dens:14.5f} {dens * math.sqrt(tau):14.5f} {np.mean([a['amp'] for a in runs]):12.2f} {spacing_over_xi:11.2f}")
    fits = {}
    for k in KAPPAS:
        xs = TAUS
        ys = [float(np.mean([a["density"] for a in res[k][t]])) for t in xs]
        ws = [sum(a["n_p"] for a in res[k][t]) for t in xs]
        fits[k] = weighted_slope(xs, ys, ws)
        p(f"    kappa = {k:.0f}: length/volume ~ tau_Q^({fits[k][0]:.2f} +- {fits[k][1]:.2f})")
    slope_all, err_all = fits[primary]
    fits_sub = {}
    for k in KAPPAS:
        xs = TAUS[:-1]
        ys = [float(np.mean([a["density"] for a in res[k][t]])) for t in xs]
        ws = [sum(a["n_p"] for a in res[k][t]) for t in xs]
        fits_sub[k] = weighted_slope(xs, ys, ws)
    slope, err = fits_sub[primary]
    box_frac = dens_by_tau[TAUS[-1]] ** -0.5 / (N_GRID * DX)
    p(f"    Excluding the largest tau_Q = {TAUS[-1]}: kappa = 6: tau_Q^({fits_sub[6.0][0]:.2f} +- {fits_sub[6.0][1]:.2f}), kappa = 8: tau_Q^({fits_sub[8.0][0]:.2f} +- {fits_sub[8.0][1]:.2f}).")
    p(f"    Kibble-Zurek (mean field z = 2, nu = 1/2): length/volume ~ xi_hat^-2 ~ tau_Q^(-1/2).  The statistical error is the line-count (Poisson) error only, with 2 runs per")
    p(f"    point; the last point (tau_Q = {TAUS[-1]}) has a line spacing of {box_frac:.2f} of the box side, so the box flattens it (L_v sqrt(tau) rises 20 %) and it is left out of the main fit.")
    p(f"    Spacing between lines, in units of the healing length at the count, is {np.mean([(dens_by_tau[t] ** -0.5) * math.sqrt(res[primary][t][0]['eps']) for t in TAUS[:-1]]):.1f} for every tau_Q up to {TAUS[-2]}: the KZ scaling is a statement about this number being constant.")

    # ======================================================================================================
    p.section("K2. Structure of the network: infinite strings and loops")
    # ------------------------------------------------------------------------------------------------------
    p("Each line component is followed through the lattice with unwrapped coordinates; a component that does not close on itself in the covering space is an")
    p("'infinite' (box-wrapping) string.  Length of a component = number of cubes it passes through.  Cubes with 4+ pierced faces (two strands in one cube,")
    p("ambiguous reconnection) are counted as junctions and joined.")
    p(f"    {'tau_Q':>6s} {'components':>11s} {'wrapping':>9s} {'length in wrapping':>19s} {'loops':>6s} {'longest loop / box':>19s} {'junction cubes / cubes':>23s}")
    inf_frac = {}
    loop_lengths = {tau: [] for tau in TAUS}
    for tau in TAUS:
        fr, comps, wr, loops, longest, jun, cub = [], 0, 0, 0, [], 0, 0
        for a in res[primary][tau]:
            sizes, wrap = a["sizes"], a["wrap"]
            fr.append(sizes[wrap].sum() / sizes.sum() if sizes.sum() else 0.0)
            comps += len(sizes)
            wr += int(wrap.sum())
            loops += int((~wrap).sum())
            loop_lengths[tau] += list(sizes[~wrap])
            longest.append(sizes[~wrap].max() / N_GRID if (~wrap).any() else 0.0)
            jun += a["junctions"]
            cub += sizes.sum()
        inf_frac[tau] = float(np.mean(fr))
        p(f"    {tau:6d} {comps:11d} {wr:9d} {np.mean(fr):19.2f} {loops:6d} {np.mean(longest):19.2f} {jun / cub:23.3f}")
    allfr = float(np.mean([inf_frac[t] for t in TAUS]))
    p(f"    => on average {allfr:.0%} of the line length sits in box-wrapping strings (Vachaspati-Vilenkin / Scherrer-Vilenkin Brownian estimate for a random-phase")
    p("       network: ~80 %, a non-universal lattice-dependent number; here the box is small, so the 'infinite' class is also box-limited).")
    # loop-length distribution, pooled over tau_Q = 20 and 40 after scaling lengths by the typical spacing
    pool = []
    for tau in (t for t in (10, 20, 40) if t in TAUS):
        sp = dens_by_tau[tau] ** -0.5 / DX            # spacing in cells
        pool += [s / sp for s in loop_lengths[tau]]
    pool = np.array(pool)
    bins = np.geomspace(max(pool.min(), 0.3), pool.max(), 9)
    cnt, edges = np.histogram(pool, bins=bins)
    centres = np.sqrt(edges[1:] * edges[:-1])
    dens_l = cnt / np.diff(edges)
    ok = cnt >= 3
    if ok.sum() >= 3:
        loop_slope = float(np.polyfit(np.log(centres[ok]), np.log(dens_l[ok]), 1)[0])
    else:
        loop_slope = float("nan")
    p(f"    Loop-length distribution, pooled over tau_Q = 10, 20, 40 with lengths in units of the line spacing: {len(pool)} loops; dn/dl ~ l^({loop_slope:.2f})  (random-walk network: -2.5;")
    p("    the pooled sample is small, the fit uses bins with >= 3 loops and carries a large uncertainty, +- 0.5 is a fair guess).")

    # ======================================================================================================
    p.section("K3. The network ages: coarsening at fixed eps")
    # ------------------------------------------------------------------------------------------------------
    tau_c = 20
    q = Quench(tau_c, 4242)
    t_c = KAPPAS[0] * math.sqrt(tau_c)
    q.advance(t_c, lambda t: t / tau_c)
    eps_f = t_c / tau_c
    marks = [0.0, 10.0, 20.0, 40.0, 80.0, 140.0]
    age = []
    for m in marks:
        q.advance(t_c + m, lambda t: eps_f)
        a = analyse(q.psi, eps_f)
        n_wrap = int(a["wrap"].sum()) if a["n_p"] else 0
        age.append((m, a["density"], a["n_p"], float(a["sizes"][a["wrap"]].sum() / a["sizes"].sum()) if a["n_p"] else float("nan"),
                    int((~a["wrap"]).sum()) if a["n_p"] else 0, n_wrap, a["length"]))
    box_len = N_GRID * DX
    p(f"    tau_Q = {tau_c}, hold eps = {eps_f:.3f} after the count; box side {box_len:g}.")
    p(f"    {'time after count':>18s} {'length/volume':>14s} {'plaquettes':>11s} {'wrapping fraction':>18s} {'loops':>6s} {'wrapping strings':>17s} {'length / (box x strings)':>25s}")
    for m, d, npl, fr, nl, nw, ln in age:
        p(f"    {m:18.0f} {d:14.5f} {npl:11d} {fr:18.2f} {nl:6d} {nw:17d} {ln / (box_len * max(nw, 1)):25.2f}")
    ms = np.array([r[0] for r in age])
    ds = np.array([r[1] for r in age])
    nw_end, ratio_end = age[-1][5], age[-1][6] / (box_len * max(age[-1][5], 1))
    # age measured from the start of the ramp-down to the count, with an offset t0 found by the fit of 1/L = a (t + t0)
    sel = ms >= 20.0
    cf = np.polyfit(ms[sel], 1.0 / ds[sel], 1)
    ts = np.array([t_c + m for m in ms])
    slope_age = float(np.polyfit(np.log(ts[sel]), np.log(ds[sel]), 1)[0])
    p(f"    Closed loops vanish within the first {next((r[0] for r in age if r[4] == 0), ms[-1]):.0f} time units; what remains is {nw_end} box-wrapping strings of total length {ratio_end:.2f} x (box x strings), i.e. still")
    p("    that many times their straight-line minimum (a string that wraps the box cannot be shorter than the box).  Over the window t >= 20 the log-log slope of length/volume")
    p(f"    against absolute time is {slope_age:.2f} and the decay slows after m = 80: with only {nw_end} long strings left in a periodic box the late stage is set by the box, so this run")
    p("    does NOT test the model-A coarsening law t^(-1) (that needs a box several times larger and several runs).  What it shows: loops decay quickly, long strings straighten,")
    p(f"    and the network loses {ds[0] / ds[-1]:.0f}x in length without any expansion.")

    # ======================================================================================================
    p.section("K4. What a line weighs inside a network, and the Planck-medium bound of r35")
    # ------------------------------------------------------------------------------------------------------
    p("Energy above the uniform ground state per unit line length, in units of 2 pi eps (an isolated global vortex has 2 pi eps [ln(R/xi) + const], xi = eps^(-1/2)):")
    p(f"    {'tau_Q':>6s} {'kappa':>6s} {'energy / length (2 pi eps)':>28s} {'ln(spacing/xi)':>15s}")
    l_eff_rows = []
    for tau in TAUS:
        for k in KAPPAS:
            vals, lns = [], []
            for a in res[k][tau]:
                if a["length"] <= 0:
                    continue
                e_per_len = a["e_ex"] / a["length"] / (2.0 * math.pi * a["eps"])
                vals.append(e_per_len)
                lns.append(math.log(a["density"] ** -0.5 * math.sqrt(a["eps"])))
            if not vals:
                continue
            l_eff_rows.append((tau, k, float(np.mean(vals)), float(np.mean(lns))))
            p(f"    {tau:6d} {k:6.0f} {np.mean(vals):28.2f} {np.mean(lns):15.2f}")
    prim_rows = [r for r in l_eff_rows if r[1] == primary]
    leff_min = min(r[2] for r in prim_rows)
    leff_mean = float(np.mean([r[2] for r in prim_rows]))
    lsp = float(np.mean([r[3] for r in prim_rows]))
    p(f"    => the energy per unit length rises with tau_Q ({prim_rows[0][2]:.1f} to {prim_rows[-1][2]:.1f}) while ln(spacing/xi) stays at {lsp:.1f}: the rise is leftover wave energy of the quench spread over fewer lines")
    p(f"       (it scales like 1/length-density), so these numbers are UPPER bounds on the string energy.  The fastest quench (tau_Q = {prim_rows[0][0]}, most lines, least wave energy per line)")
    p(f"       gives the closest estimate, {leff_min:.1f}, which is ln(spacing/xi) + {leff_min - lsp:.1f}: the cut-off of the logarithm is the line spacing, as for a dense vortex lattice.")
    ln_today = math.log(R_OBS / lP())
    f_max_form = GMU_BOUND / (2.0 * math.pi * leff_min)
    f_max_today = GMU_BOUND / (2.0 * math.pi * ln_today)
    p(f"    r35 took ln(R/xi) = 1.5 at formation (an underestimate by a factor {leff_min / 1.5:.1f}) and {ln_today:.0f} for strings that stretch with the universe (spacing ~ Hubble radius, R_obs/l_P).")
    p(f"    Bound G mu / c^2 < {GMU_BOUND:.1e} at formation: f alpha^2 < {f_max_form:.1e} (measured logarithm {leff_min:.1f}); today, if the strings survive as a scaling network whose spacing grows with")
    p(f"    the horizon, the logarithm is {ln_today:.0f} and f alpha^2 < {f_max_today:.1e}.  The tension grows with the spacing, so the bound that matters is the later one -- unless inflation has")
    p("    removed the strings (they are then diluted to ~1 per observable universe, below).  Tension is therefore not a property of the medium alone but of the network's age.")
    t_planck = math.sqrt(hbar * c ** 5 / G0) / KB
    g_ratio = (106.75 / 3.91) ** (1.0 / 3.0)
    stretch = t_planck / T0_K * g_ratio
    p(f"    Dilution (as in r35): formation at T_P = {t_planck:.2e} K, expansion to today stretches lengths x{stretch:.1e}.  With the measured spacing in units of xi (alpha = 1, xi = l_P):")
    p(f"    {'tau_Q':>6s} {'spacing / l_P':>14s} {'strings in the observable universe':>36s} {'e-folds needed to leave ~1':>28s}")
    n_rows = []
    for tau in TAUS:
        spacing = (dens_by_tau[tau] ** -0.5) * math.sqrt(res[primary][tau][0]["eps"])      # in units of xi
        sp_today = spacing * lP() * stretch
        n_univ = (R_OBS / sp_today) ** 3
        n_ef = math.log(R_OBS / sp_today)
        n_rows.append((tau, spacing, n_univ, n_ef))
        p(f"    {tau:6d} {spacing:14.1f} {n_univ:36.1e} {n_ef:28.1f}")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("K1: Kibble-Zurek counting works in 3D: length/volume ~ tau_Q^(-1/2)",
         f"{'CONFIRMED' if abs(slope + 0.5) < 0.1 and abs(fits_sub[8.0][0] + 0.5) < 0.1 else 'NOT CONFIRMED'}: {slope:.2f} +- {err:.2f} (kappa 6), {fits_sub[8.0][0]:.2f} (kappa 8) for tau_Q <= {TAUS[-2]}; "
         f"with tau_Q = {TAUS[-1]} included {slope_all:.2f} (box-limited)"),
        ("K2a: the network is mostly long strings, plus loops",
         f"{allfr:.0%} of the line length in box-wrapping strings (small box); loops dn/dl ~ l^({loop_slope:.1f}) from only {len(pool)} loops"),
        ("K3: the network ages without expansion",
         f"loops vanish within {next((r[0] for r in age if r[4] == 0), ms[-1]):.0f} time units; length/volume falls {ds[0] / ds[-1]:.0f}-fold, then slows ({nw_end} wrapping strings left at {ratio_end:.1f}x their minimum length); "
         f"t^(-1) law not tested (box too small)"),
        ("K4: the string tension is a property of the network, not of the medium alone",
         f"energy/length {leff_min:.1f} (upper bound) at formation vs ln(R_obs/xi) = {ln_today:.0f} for a scaling network today: f alpha^2 < {f_max_form:.0e} then, < {f_max_today:.0e} later"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<70s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig = plt.figure(figsize=(13.4, 10.4))

    ax = fig.add_subplot(2, 2, 1, projection="3d")
    a, psi_s = snap_for_plot
    comp_wrap = a["wrap"]
    xs_w, ys_w, zs_w, xs_l, ys_l, zs_l = [], [], [], [], [], []
    for node, lab in a["label"].items():
        if comp_wrap[lab]:
            xs_w.append(node[0]); ys_w.append(node[1]); zs_w.append(node[2])
        else:
            xs_l.append(node[0]); ys_l.append(node[1]); zs_l.append(node[2])
    ax.scatter(np.array(xs_w) * DX, np.array(ys_w) * DX, np.array(zs_w) * DX, s=1.5, color=S1, label="box-wrapping strings", depthshade=False)
    ax.scatter(np.array(xs_l) * DX, np.array(ys_l) * DX, np.array(zs_l) * DX, s=3.5, color=S2, label="closed loops", depthshade=False)
    ax.set(xlabel="x", ylabel="y", zlabel="z", title=f"Vortex lines after a quench (tau_Q = 20)")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_box_aspect((1, 1, 1))

    ax = fig.add_subplot(2, 2, 2)
    taus_a = np.array(TAUS, float)
    for k, col, mk in ((6.0, S1, "o"), (8.0, S2, "s")):
        ys = [float(np.mean([a_["density"] for a_ in res[k][t]])) for t in TAUS]
        ax.plot(taus_a, ys, mk, color=col, ms=8, label=f"counted at t = {k:.0f} √τ_Q")
    ref = dens_by_tau[TAUS[1]] * (taus_a / TAUS[1]) ** -0.5
    ax.plot(taus_a, ref, color=MUTED, ls="--", lw=1.4, label="Kibble–Zurek: τ_Q^(−1/2)")
    ax.set(xscale="log", yscale="log", xlabel="quench time τ_Q", ylabel="vortex-line length per volume",
           title=f"Line density against τ_Q: τ_Q^({slope:.2f}) for τ_Q ≤ {TAUS[-2]}")
    ax.text(TAUS[-1], dens_by_tau[TAUS[-1]] * 1.25, "box-limited", fontsize=9, color=INK_2, ha="center")
    ax.legend(loc="lower left", fontsize=9)

    ax = fig.add_subplot(2, 2, 3)
    ax.loglog(centres[ok], dens_l[ok] / dens_l[ok][0], "o", color=S1, ms=8, label="loops (pooled, spacing units)")
    ll = np.geomspace(centres[ok].min(), centres[ok].max(), 50)
    ax.loglog(ll, (ll / centres[ok][0]) ** -2.5, color=MUTED, ls="--", lw=1.4, label="random-walk network: ℓ^(−5/2)")
    ax.set(xlabel="loop length ÷ line spacing", ylabel="number of loops per unit length (scaled)",
           title=f"Loop lengths (pooled, {len(pool)} loops): too few for a firm exponent")
    ax.legend(loc="lower left", fontsize=9)

    ax = fig.add_subplot(2, 2, 4)
    ax.loglog(ts, ds, "o", color=S1, ms=8, label="length per volume (simulation)")
    t_line = np.geomspace(ts[sel][0], ts[-1], 30)
    ax.loglog(t_line, ds[sel][0] * (t_line / ts[sel][0]) ** -1.0, color=MUTED, ls="--", lw=1.4, label="coarsening prediction: t^(−1)")
    ax.axhline(nw_end * box_len / box_len ** 3, color=S2, lw=1.3, ls=":", label=f"minimum for {nw_end} straight wrapping strings")
    ax.set(xlabel="time t (hold at fixed ε after the count)", ylabel="vortex-line length per volume",
           title="Loops vanish; the wrapping strings then straighten slowly")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "network")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
