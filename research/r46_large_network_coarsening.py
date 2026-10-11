"""
r46 - A larger 3D vortex network: coarsening, loops and long strings  (LAB_NOTEBOOK.md entry E48, test N1)

Question (queue item from E47): "A larger 3D network: a box several times larger (256^3 or more, several runs) for the loop-length exponent
(>= 200 loops), the coarsening exponent, and the network under expansion."  r42 (128^3, box 64, two long strings left in a periodic box) could not
test the coarsening law or give a loop distribution.  Here:

  * 256^3 lattice with dx = 1.0 (box 256 healing-length units, 4 times the r42 box side, 64 times its volume), dt = 0.1 (< dx^2/6 = 0.167);
  * the instantaneous quench (tau_Q -> 0): a random complex field, then d psi / dt = eps psi - |psi|^2 psi + nabla^2 psi at fixed eps = 0.3
    (healing length 1/sqrt(eps) = 1.8 lattice spacings; no noise afterwards, so the evolution is pure coarsening of the random-phase network);
  * line tracing with a vectorised weighted union-find (numba) so that millions of plaquettes can be handled;
  * measured: line length per volume against time (model-A coarsening predicts t^-1: length/volume ~ 1/xi(t)^2 with xi ~ t^(1/2));
    the fraction of the length in box-wrapping ("infinite") strings; the loop-length distribution (random-phase prediction ~ l^(-5/2),
    Vachaspati & Vilenkin 1984; ~80 % of the length in infinite strings).
The expanding-box version (Hubble friction) is not done here (see E48, open).
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402
from r42_vortex_lines_3d_quench import plaquette_windings, tdgl_step  # noqa: E402

NAME = "r46_large_network_coarsening"
N_GRID = int(os.environ.get("R46_N", 256))
DX, DT, EPS = 1.0, 0.1, 0.3
T_MARKS = tuple(float(x) for x in os.environ.get("R46_T", "10,20,40,80,160,320,640").split(","))
SEEDS = tuple(int(x) for x in os.environ.get("R46_SEEDS", "1,2").split(","))
MAX_TRACE_PLAQ = 4_000_000


@njit(cache=True)
def _find(parent, off, x):
    """Root of x and the offset of x relative to the root (path compression)."""
    path = []
    cur = x
    while parent[cur] != cur:
        path.append(cur)
        cur = parent[cur]
    root = cur
    # accumulate offsets from the top of the path down
    acc0, acc1, acc2 = 0, 0, 0
    for idx in range(len(path) - 1, -1, -1):
        node = path[idx]
        acc0 += off[node, 0]
        acc1 += off[node, 1]
        acc2 += off[node, 2]
        off[node, 0], off[node, 1], off[node, 2] = acc0, acc1, acc2
        parent[node] = root
    return root


@njit(cache=True)
def union_find_wrap(n_nodes, eu, ev, ed):
    """Weighted union-find over the edges (u -> v, displacement unit vector ed).  Returns (root of every node, wrap flag per root, junction degree)."""
    parent = np.arange(n_nodes)
    off = np.zeros((n_nodes, 3), dtype=np.int64)     # position of node minus position of its parent, in the covering space
    wrap = np.zeros(n_nodes, dtype=np.bool_)
    for e in range(len(eu)):
        u, v = eu[e], ev[e]
        ru = _find(parent, off, u)
        rv = _find(parent, off, v)
        ou0, ou1, ou2 = off[u, 0], off[u, 1], off[u, 2]
        ov0, ov1, ov2 = off[v, 0], off[v, 1], off[v, 2]
        if u == ru:
            ou0 = ou1 = ou2 = 0
        if v == rv:
            ov0 = ov1 = ov2 = 0
        # want pos[v] = pos[u] + ed:  (pos[rv] + ov) = (pos[ru] + ou) + ed
        d0, d1, d2 = ed[e, 0], ed[e, 1], ed[e, 2]
        if ru == rv:
            if ov0 != ou0 + d0 or ov1 != ou1 + d1 or ov2 != ou2 + d2:
                wrap[ru] = True
        else:
            parent[rv] = ru
            off[rv, 0] = ou0 + d0 - ov0
            off[rv, 1] = ou1 + d1 - ov1
            off[rv, 2] = ou2 + d2 - ov2
            if wrap[rv]:
                wrap[ru] = True
    roots = np.empty(n_nodes, dtype=np.int64)
    for x in range(n_nodes):
        roots[x] = _find(parent, off, x)
    return roots, wrap


def trace(wx, wy, wz):
    """Components of the line network: (sizes in cubes, wrap flags, number of junction cubes with > 2 pierced faces)."""
    n = wx.shape[0]
    us, vs, ds = [], [], []
    for axis, w in enumerate((wx, wy, wz)):
        i, j, k = np.nonzero(w)
        lo = [i.copy(), j.copy(), k.copy()]
        lo[axis] = (lo[axis] - 1) % n
        us.append((lo[0] * n + lo[1]) * n + lo[2])
        vs.append((i * n + j) * n + k)
        d = np.zeros((len(i), 3), dtype=np.int64)
        d[:, axis] = 1
        ds.append(d)
    eu, ev, ed = np.concatenate(us), np.concatenate(vs), np.concatenate(ds)
    ids, inv = np.unique(np.concatenate([eu, ev]), return_inverse=True)
    m = len(eu)
    eu_i, ev_i = inv[:m].astype(np.int64), inv[m:].astype(np.int64)
    roots, wrap = union_find_wrap(len(ids), eu_i, ev_i, ed)
    uniq, comp = np.unique(roots, return_inverse=True)
    sizes = np.bincount(comp)
    wr = wrap[uniq]
    deg = np.bincount(np.concatenate([eu_i, ev_i]), minlength=len(ids))
    return sizes, wr, int((deg > 2).sum())


def evolve(seed, marks):
    """Random initial field, evolve at fixed eps; returns {t: dict(length density, plaquettes, trace results)}."""
    rng = np.random.default_rng(seed)
    n = N_GRID
    psi = (0.3 * (rng.standard_normal((n, n, n), dtype=np.float32) + 1j * rng.standard_normal((n, n, n), dtype=np.float32))).astype(np.complex64)
    new = np.empty_like(psi)
    zero = np.zeros((n, n, n), dtype=np.float32)
    t = 0.0
    out = {}
    vol = (n * DX) ** 3
    t0 = time.time()
    for mark in marks:
        while t < mark - 1e-9:
            tdgl_step(psi, new, np.float32(EPS), np.float32(DT), np.float32(1.0 / DX ** 2), zero, zero, np.float32(0.0))
            psi, new = new, psi
            t += DT
        wx, wy, wz = plaquette_windings(psi)
        n_p = int(np.count_nonzero(wx) + np.count_nonzero(wy) + np.count_nonzero(wz))
        rec = {"n_p": n_p, "length": (2.0 / 3.0) * n_p * DX, "density": (2.0 / 3.0) * n_p * DX / vol, "amp": float(np.mean(np.abs(psi) ** 2)) / EPS}
        if 0 < n_p <= MAX_TRACE_PLAQ:
            sizes, wr, junc = trace(wx, wy, wz)
            rec.update({"sizes": sizes, "wrap": wr, "junctions": junc})
        out[mark] = rec
        print(f"    seed {seed}: t = {mark:6.0f} done ({time.time() - t0:.0f} s): plaquettes {n_p}, length/volume {rec['density']:.5f}", flush=True)
    return out


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    p(f"Lattice {N_GRID}^3, dx = {DX}, dt = {DT}, eps = {EPS} (healing length {1 / math.sqrt(EPS):.2f} lattice spacings), box {N_GRID * DX:g}; seeds {SEEDS}; times {T_MARKS}.")
    p("Random initial field (amplitude 0.3), no noise afterwards: coarsening of the random-phase network (an instantaneous quench).")

    # ======================================================================================================
    p.section("N1a. Self-test of the line tracer on a known configuration")
    # ------------------------------------------------------------------------------------------------------
    # a straight line wrapping the box in z, a small closed square loop: expect 2 components, 1 wrapping
    nt = 24
    wx = np.zeros((nt, nt, nt), dtype=np.int8)
    wy = np.zeros_like(wx)
    wz = np.zeros_like(wx)
    wz[3, 3, :] = 1                      # a line along z through the cubes (3, 3, k): it pierces the face normal to z between every pair of consecutive cubes
    # a closed ring of 8 cubes at z = 10: (10,10) (11,10) (12,10) (12,11) (12,12) (11,12) (10,12) (10,11); each step pierces the face between the two cubes
    wx[11, 10, 10] = wx[12, 10, 10] = 1      # +x steps along b = 10
    wy[12, 11, 10] = wy[12, 12, 10] = 1      # +y steps along a = 12
    wx[12, 12, 10] = wx[11, 12, 10] = 1      # -x steps along b = 12
    wy[10, 12, 10] = wy[10, 11, 10] = 1      # -y steps along a = 10
    sizes_t, wrap_t, _ = trace(wx, wy, wz)
    order_t = np.argsort(sizes_t)
    p(f"    synthetic network: components {len(sizes_t)}, sizes {sizes_t[order_t].tolist()}, wrapping flags {wrap_t[order_t].tolist()}  (expected: a closed ring of 8 cubes and a wrapping line of {nt} cubes)")
    ok_trace = (len(sizes_t) == 2) and sizes_t[order_t].tolist() == [8, nt] and wrap_t[order_t].tolist() == [False, True]
    p(f"    self-test {'PASSED' if ok_trace else 'FAILED'}.")

    # ======================================================================================================
    p.section("N1b. Coarsening of the random-phase network")
    # ------------------------------------------------------------------------------------------------------
    runs = [evolve(s, T_MARKS) for s in SEEDS]
    p(f"    {'t':>6s} {'plaquettes (mean)':>18s} {'length/volume':>14s} {'L_v * t':>10s} {'|psi|^2/eps':>12s} {'wrapping fraction':>18s} {'loops':>7s} {'wrapping strings':>17s}")
    ts = np.array(T_MARKS)
    dens = np.array([np.mean([r[t]["density"] for r in runs]) for t in T_MARKS])
    npl = np.array([np.mean([r[t]["n_p"] for r in runs]) for t in T_MARKS])
    wfrac, nloops, nwrap = {}, {}, {}
    for t in T_MARKS:
        f_, l_, w_ = [], 0, 0
        for r in runs:
            rec = r[t]
            if "sizes" in rec:
                f_.append(rec["sizes"][rec["wrap"]].sum() / rec["sizes"].sum())
                l_ += int((~rec["wrap"]).sum())
                w_ += int(rec["wrap"].sum())
        wfrac[t], nloops[t], nwrap[t] = (float(np.mean(f_)) if f_ else float("nan")), l_, w_
    for t, d, n_p in zip(ts, dens, npl):
        amp = np.mean([r[t]["amp"] for r in runs])
        p(f"    {t:6.0f} {n_p:18.0f} {d:14.6f} {d * t:10.4f} {amp:12.2f} {wfrac[t]:18.2f} {nloops[t]:7d} {nwrap[t]:17d}")
    # exponent from the late window
    def slope(mask):
        return float(np.polyfit(np.log(ts[mask]), np.log(dens[mask]), 1)[0])
    late = ts >= 40
    s_late = slope(late)
    mid = (ts >= 40) & (ts <= 320)
    s_mid = slope(mid) if mid.sum() >= 3 else float("nan")
    s_pairs = [(ts[i], ts[i + 1], math.log(dens[i + 1] / dens[i]) / math.log(ts[i + 1] / ts[i])) for i in range(len(ts) - 1)]
    p("    Local exponents d ln(L_v) / d ln t between neighbouring times: " + ", ".join(f"{a:.0f}-{b:.0f}: {s:.2f}" for a, b, s in s_pairs))
    p(f"    Fit over 40 <= t <= 320 (before the box matters): length/volume ~ t^({s_mid:.2f});  over all t >= 40: t^({s_late:.2f}).")
    p("    Model-A coarsening (xi ~ t^(1/2), L_v ~ xi^-2): -1.  The ordering of the field is complete only at t ~ 20-40 (|psi|^2/eps = 0.6 at t = 20), so the earliest point is still formation.")
    # logarithmic correction: the line tension of a global vortex carries ln(L/xi_core), so L_v t = a + b ln t is expected rather than a pure power law
    lv_t = dens * ts
    b_log, a_log = np.polyfit(np.log(ts[late]), lv_t[late], 1)
    res_log = lv_t[late] - (a_log + b_log * np.log(ts[late]))
    rel_dev_log = float(np.max(np.abs(res_log) / lv_t[late]))
    eff_first = -1 + b_log / (a_log + b_log * math.log(ts[late][0]))
    eff_last = -1 + b_log / (a_log + b_log * math.log(ts[late][-1]))
    p(f"    Log-corrected form: L_v t = a + b ln t with a = {a_log:.4f}, b = {b_log:.4f} fits the points t >= 40 to {rel_dev_log:.1%} (worst relative residual); the implied local exponent")
    p(f"    d ln L_v / d ln t = -1 + b / (a + b ln t) is {eff_first:.2f} at t = {ts[late][0]:.0f} and {eff_last:.2f} at t = {ts[late][-1]:.0f}.")
    p(f"    A pure power law t^-1 would have constant L_v t; it rises by {lv_t[late][-1] / lv_t[late][0] - 1:.0%} between the first and last point: t^-1 holds up to a logarithm (the tension of a global vortex line carries ln(L / core); Bray 1994).")

    # ======================================================================================================
    p.section("N1c. Structure: loops and infinite strings")
    # ------------------------------------------------------------------------------------------------------
    tcs = [t for t in T_MARKS if nloops[t] + nwrap[t] > 0]
    p("    (tracing is done only where the number of pierced plaquettes is below 4 million)")
    p(f"    {'t':>6s} {'components':>11s} {'wrapping':>9s} {'length in wrapping':>19s} {'loops':>6s} {'longest loop / box':>19s} {'junction cubes / cubes':>23s}")
    for t in tcs:
        comps = sum(len(r[t]["sizes"]) for r in runs if "sizes" in r[t])
        jun = sum(r[t]["junctions"] for r in runs if "sizes" in r[t])
        cub = sum(r[t]["sizes"].sum() for r in runs if "sizes" in r[t])
        longest = np.mean([r[t]["sizes"][~r[t]["wrap"]].max() * DX / (N_GRID * DX) if (~r[t]["wrap"]).any() else 0.0 for r in runs if "sizes" in r[t]])
        p(f"    {t:6.0f} {comps:11d} {nwrap[t]:9d} {wfrac[t]:19.2f} {nloops[t]:6d} {longest:19.2f} {jun / cub:23.4f}")
    p("    Loop-length slope at single times (lengths in units of the line spacing at that time; bins with >= 3 loops; shown only where there are >= 40 loops):")
    for t in tcs:
        ls_ = []
        for r in runs:
            rec = r[t]
            if "sizes" in rec:
                ls_ += list(rec["sizes"][~rec["wrap"]] / (rec["density"] ** -0.5 / DX))
        ls_ = np.array(ls_)
        if len(ls_) < 40:
            continue
        cnt_t, edg_t = np.histogram(ls_, bins=np.geomspace(max(ls_.min(), 0.05), ls_.max(), 11))
        cen_t = np.sqrt(edg_t[1:] * edg_t[:-1])
        okt = cnt_t >= 3
        if okt.sum() >= 3:
            wts = cnt_t[okt].astype(float)
            xx, yy = np.log(cen_t[okt]), np.log(cnt_t[okt] / np.diff(edg_t)[okt])
            xm_, ym_ = np.sum(wts * xx) / wts.sum(), np.sum(wts * yy) / wts.sum()
            sl_ = np.sum(wts * (xx - xm_) * (yy - ym_)) / np.sum(wts * (xx - xm_) ** 2)
            p(f"      t = {t:5.0f}: {len(ls_):4d} loops, dn/dl ~ l^({sl_:.2f} +- {1 / math.sqrt(np.sum(wts * (xx - xm_) ** 2)):.2f}); lengths span {ls_.min():.2f} to {ls_.max():.1f} spacings")
    # loop length distribution: pool all loops at times where the network is in the scaling regime, lengths in units of the line spacing at that time
    pool = []
    for t in T_MARKS:
        if t < 40:
            continue
        for r in runs:
            rec = r[t]
            if "sizes" not in rec:
                continue
            spacing = rec["density"] ** -0.5 / DX      # in cells
            pool += list(rec["sizes"][~rec["wrap"]] / spacing)
    pool = np.array(pool)
    loop_slope, loop_err = float("nan"), float("nan")
    centres = dens_l = cnt = None
    if len(pool) >= 20:
        lo, hi = max(pool.min(), 0.2), pool.max()
        bins = np.geomspace(lo, hi, 11)
        cnt, edges = np.histogram(pool, bins=bins)
        centres = np.sqrt(edges[1:] * edges[:-1])
        dens_l = cnt / np.diff(edges)
        ok = cnt >= 3
        if ok.sum() >= 3:
            wts = cnt[ok].astype(float)                        # Poisson weights on ln(count)
            x, y = np.log(centres[ok]), np.log(dens_l[ok])
            xm, ym = np.sum(wts * x) / wts.sum(), np.sum(wts * y) / wts.sum()
            loop_slope = float(np.sum(wts * (x - xm) * (y - ym)) / np.sum(wts * (x - xm) ** 2))
            loop_err = float(1.0 / math.sqrt(np.sum(wts * (x - xm) ** 2)))
    p(f"    Loop-length distribution pooled over t >= 40 (lengths in line-spacing units): {len(pool)} loops; dn/dl ~ l^({loop_slope:.2f} +- {loop_err:.2f})  (random-phase network: -2.5)")
    p(f"    Average fraction of the length in box-wrapping strings over the traced times: {np.nanmean([wfrac[t] for t in tcs]) if tcs else float('nan'):.0%}  (random-phase estimate ~ 80 %).")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("N1a: the union-find line tracer is correct on a known network", "PASSED" if ok_trace else "FAILED"),
        ("N1b: model-A coarsening, length/volume ~ t^-1",
         f"{'CONFIRMED' if abs(s_mid + 1) < 0.1 else 'NOT CONFIRMED'} as a pure power law: t^({s_mid:.2f}) over 40-320 (local exponents {s_pairs[1][2]:.2f} to {s_pairs[-2][2]:.2f}); but L_v t = a + b ln t fits to {rel_dev_log:.1%} (a = {a_log:.3f}, b = {b_log:.4f}): t^-1 with a logarithmic correction"),
        ("N1c: loops follow dn/dl ~ l^-5/2",
         f"{'CONSISTENT' if abs(loop_slope + 2.5) < 2 * loop_err + 0.3 else 'NOT CONSISTENT'}: {loop_slope:.2f} +- {loop_err:.2f} from {len(pool)} loops"),
        ("N1d: most of the length is in infinite strings",
         f"{np.nanmean([wfrac[t] for t in tcs]):.0%} in box-wrapping strings (random-phase estimate ~ 80 %)" if tcs else "not traced"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<62s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(16.4, 5.2))
    ax = axs[0]
    ax.loglog(ts, dens, "o", color=S1, ms=8, label=f"length per volume ({len(SEEDS)} runs)")
    ref = dens[late][0] * (ts / ts[late][0]) ** -1.0
    ax.loglog(ts, ref, color=MUTED, ls="--", lw=1.4, label="coarsening law t⁻¹")
    ax.set(xlabel="time t", ylabel="vortex-line length per volume", title=f"Network ageing: t^({s_mid:.2f}) for 40 ≤ t ≤ 320")
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1]
    tt = [t for t in tcs]
    ax.plot(tt, [wfrac[t] for t in tt], "o-", color=S1, ms=7, label="length in box-wrapping strings")
    ax.axhline(0.8, color=MUTED, ls="--", lw=1.3)
    ax.text(tt[0], 0.82, "random-phase estimate ≈ 80 %", fontsize=9, color=INK_2)
    ax.set(xscale="log", ylim=(0, 1.05), xlabel="time t", ylabel="fraction of the line length", title="Most of the length is in long strings")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[2]
    if centres is not None and cnt is not None and (cnt >= 3).sum() >= 3:
        okm = cnt >= 3
        ax.loglog(centres[okm], dens_l[okm], "o", color=S1, ms=8, label=f"loops (pooled, {len(pool)})")
        ll = np.geomspace(centres[okm].min(), centres[okm].max(), 40)
        ax.loglog(ll, dens_l[okm][0] * (ll / centres[okm][0]) ** -2.5, color=MUTED, ls="--", lw=1.4, label="random-phase network: ℓ^(−5/2)")
        ax.legend(loc="lower left", fontsize=9)
    ax.set(xlabel="loop length ÷ line spacing", ylabel="loops per unit length (counts per bin width)", title="Loop lengths")
    fig.tight_layout()
    save_fig(fig, NAME, "coarsening")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
