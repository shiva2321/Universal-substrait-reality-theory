"""
r18 - The one-way arrow of time, at the substrate level  (LAB_NOTEBOOK.md entry E24)

Question (user): "... but it is one way only, it can't go back either -- even at the substrate
level too. We also need tests and experiments on this, from the smallest to the highest magnitudes."

Three candidate sources of 'one way' are tested, with exact (integer / combinatorial) computations:
  A. Reversible micro-laws + a low-entropy start (Boltzmann, the Past Hypothesis).  An exactly
     reversible substrate (HPP lattice gas, bit arithmetic): entropy rises; reversing every velocity
     brings it back BIT-EXACTLY; flipping one bit at the turn-around does not come back.
     The fraction of states that would 'un-mix' is exp(-Delta S).
  B. A growing substrate (causal-set sequential growth, Rideout & Sorkin 2000): the order relation
     itself is one-way (acyclic), while the order in which elements are born is NOT observable
     (many equally valid birth orders -> no universal 'now').  Counted exactly.
  C. Measured arrows, from the smallest to the largest scale: T violation in kaons and B mesons,
     the electron EDM, the black-hole area theorem, the low-entropy early universe.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.special import gammaln  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r18_arrow_of_time"
L, B, T = 128, 8, 600


# ---------------------------------------------------------------- A. exactly reversible lattice gas
def collide(g):
    E, N, W, S = g
    ew = E & W & ~N & ~S
    ns = N & S & ~E & ~W
    return np.array([(E & ~ew) | ns, (N & ~ns) | ew, (W & ~ew) | ns, (S & ~ns) | ew])


def stream(g):
    E, N, W, S = g
    return np.array([np.roll(E, 1, 1), np.roll(N, 1, 0), np.roll(W, -1, 1), np.roll(S, -1, 0)])


def reverse(g):
    return g[[2, 3, 0, 1]]


def coarse_entropy(g):
    """Boltzmann entropy of the coarse-grained state: sum over 8x8 blocks of ln C(4*64, n)."""
    n = g.sum(0).reshape(L // B, B, L // B, B).sum((1, 3))
    M = 4 * B * B
    return float(np.sum(gammaln(M + 1) - gammaln(n + 1) - gammaln(M - n + 1)))


def lattice_gas():
    rng = np.random.default_rng(7)
    g0 = np.zeros((4, L, L), bool)
    g0[:, :, :L // 2] = rng.random((4, L, L // 2)) < 0.5
    g, Sf, snaps = g0.copy(), [coarse_entropy(g0)], {0: g0.sum(0)}
    for t in range(1, T + 1):
        g = stream(collide(g))
        Sf.append(coarse_entropy(g))
        if t in (60, T):
            snaps[t] = g.sum(0)
    gT = g.copy()
    # exact reversal: (stream o collide)^-1 = R (collide o stream) R, since R C R = C, R S R = S^-1, C^2 = 1
    out = {}
    for label, flip in (("exact", False), ("one bit flipped", True)):
        y = reverse(gT)
        if flip:
            y[0, 5, 5] ^= True
        Sr = [coarse_entropy(y)]
        for _ in range(T):
            y = collide(stream(y))
            Sr.append(coarse_entropy(y))
        y = reverse(y)
        out[label] = (Sr, y)
    return g0, gT, Sf, out, snaps


# ---------------------------------------------------------------- B. growth arrow (causal sets)
def transitive_percolation(n, p, rng):
    rel = np.zeros((n, n), bool)
    for j in range(n):
        for i in range(j):
            if rng.random() < p:
                rel[i, j] = True
    for k in range(n):                       # transitive closure (Warshall), exact
        rel |= rel[:, k:k + 1] & rel[k:k + 1, :]
    return rel


def count_linear_extensions(rel):
    """Exact number of birth orders compatible with the causal order (DP over down-sets)."""
    n = len(rel)
    pred = [sum(1 << i for i in range(n) if rel[i, j]) for j in range(n)]
    f = {0: 1}
    for mask in range(1 << n):
        if mask not in f:
            continue
        for j in range(n):
            if not mask >> j & 1 and pred[j] & ~mask == 0:
                f[mask | 1 << j] = f.get(mask | 1 << j, 0) + f[mask]
    return f[(1 << n) - 1]


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Reversible substrate + low-entropy start (exact bit arithmetic, HPP lattice gas)")
    g0, gT, Sf, out, snaps = lattice_gas()
    p(f"{L}x{L} lattice, 4 velocity channels, {int(g0.sum())} particles, all in the left half at t = 0")
    p("micro-rule: head-on pairs scatter by 90 degrees, then everything streams -- a BIJECTION (reversible)")
    p(f"coarse-grained entropy (8x8 blocks): t = 0: {Sf[0]:.1f}   t = {T}: {Sf[-1]:.1f}   (maximum for this"
      f" density ~ {(L // B) ** 2 * (gammaln(257) - gammaln(g0.sum() / (L // B) ** 2 + 1) - gammaln(257 - g0.sum() / (L // B) ** 2)):.0f}) nats")
    ex_S, ex_y = out["exact"]
    pt_S, pt_y = out["one bit flipped"]
    p(f"reverse every velocity at t = {T} and run the SAME law {T} more steps:")
    p(f"   returns bit-for-bit to the initial state: {np.array_equal(ex_y, g0)};  entropy back to {ex_S[-1]:.1f}")
    p(f"   with ONE of the {g0.size} bits flipped at the turn-around: {int(np.sum(pt_y != g0))} bits differ at the end;"
      f" entropy ends at {pt_S[-1]:.1f}")
    dS = Sf[-1] - Sf[0]
    p(f"entropy rise Delta S = {dS:.0f} nats: of all microstates looking like the mixed state, a fraction")
    p(f"   exp(-Delta S) = 10^({-dS / math.log(10):.0f}) would un-mix by themselves.")
    p("=> the substrate's LAW has no arrow (exact reversal works). The arrow comes from the START (low")
    p("   entropy) plus coarse-graining, and 'going back' needs control of every bit: one wrong bit fails.")
    p("   (HPP is only weakly chaotic, so the flipped run partly un-mixes; a fully chaotic law is worse.)")

    p.section("B. A growing substrate: one-way order, but no universal 'now' (causal-set growth)")
    rng = np.random.default_rng(3)
    n = 14
    rel = transitive_percolation(n, 0.18, rng)
    acyclic = not np.any(np.diag(rel)) and not np.any(rel & rel.T)
    n_rel = int(rel.sum())
    lin = count_linear_extensions(rel)
    p(f"transitive percolation (Rideout & Sorkin, PRD 61, 024002 (2000)), {n} elements, p = 0.18:")
    p(f"   {n_rel} causal relations; acyclic (nothing precedes itself, no loops): {acyclic}")
    p(f"   number of birth orders that produce exactly this causal set: {lin} (out of {math.factorial(n)} orderings)")
    p("=> 'one way' is built into the substrate: the relation 'is to the past of' has no loops, so no")
    p("   chain of influences can return to its start. Yet the order of birth is not physical --")
    p(f"   {lin} different sequences give the same universe (discrete general covariance). There is a")
    p("   direction of becoming, but no global moment 'now': simultaneity is relative, as in relativity.")
    n_ext_chain = count_linear_extensions(np.triu(np.ones((6, 6), bool), 1))
    n_ext_anti = count_linear_extensions(np.zeros((6, 6), bool))
    p(f"   checks: a 6-chain has {n_ext_chain} birth order (fully ordered); a 6-antichain has {n_ext_anti} = 6!")

    p.section("C. Measured arrows of time, smallest to largest")
    cpl = 6.6e-3 / math.hypot(1.3e-3, 1.0e-3)
    rows = [
        ("1e-15 m", "kaon T violation (CPLEAR 1998)", f"A_T = (6.6 +- 1.3 +- 1.0)e-3 -> {cpl:.1f} sigma", "Phys. Lett. B 444, 43"),
        ("1e-15 m", "B-meson T violation (BaBar 2012)", "observed directly at 14 sigma", "PRL 109, 211801"),
        ("1e-13 m", "electron EDM (T-odd), JILA 2023", "|d_e| < 4.1e-30 e cm: no new T violation", "Science 381, 46"),
        ("0.1 m", "quantum switch (indefinite causal order)", "order of two operations put in superposition, never a loop",
         "Procopio et al., Nat. Commun. 6, 7913 (2015)"),
        ("1 m", "thermodynamics, radiation, records", "no exception ever observed", "second law"),
        ("2e5 m", "black-hole area theorem (GW150914)", "area increase at 97% credibility", "Isi et al., PRL 127, 011103 (2021)"),
        ("1e26 m", "low-entropy early universe", "S_now ~ 3e104 k_B vs maximum ~ 2.6e122 k_B", "Egan & Lineweaver, ApJ 710, 1825 (2010)"),
    ]
    for sc, what, res, ref in rows:
        p(f"   {sc:>7s}  {what:44s} {res}  [{ref}]")
    p("=> nature has ONE microscopic arrow (the weak interaction's T violation, tiny but 14 sigma; CPT")
    p("   holds, so it is not a 'flow') and one huge macroscopic arrow (the low-entropy beginning). Every")
    p("   everyday arrow follows from the second. No closed causal loop (time travel to the past) has ever")
    p("   been seen; quantum experiments can make the ORDER of two events indefinite, but not circular.")

    p.section("D. What this means for the substrate")
    for line in (
        "* If the substrate's law is reversible (a unitary quantum network, USRT v2), the arrow must come",
        "  from its initial state (as in A): the substrate started extremely ordered. That is an INPUT.",
        "* If the substrate GROWS (causal-set substrate, r19), 'one way' is fundamental: the past is",
        "  fixed, the future is being added, no loops are possible -- exactly the user's 'cannot go back'.",
        "  It still does not explain the low-entropy start; both ingredients are needed.",
        "* The tiny weak-interaction arrow must be a property of how matter-knots sit in the substrate",
        "  (it distinguishes matter from antimatter); its origin is open in every theory.",
    ):
        p(line)

    # ---------- figures
    fig = plt.figure(figsize=(12.5, 7.6))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.15])
    titles = {0: "t = 0: all in the left half", 60: "t = 60", T: f"t = {T}: mixed"}
    for i, t in enumerate((0, 60, T)):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(snaps[t], cmap="Blues", vmin=0, vmax=3, interpolation="nearest")
        ax.set(title=titles[t], xticks=[], yticks=[])
        ax.grid(False)
    ax = fig.add_subplot(gs[0, 3])
    ax.imshow(out["one bit flipped"][1].sum(0), cmap="Blues", vmin=0, vmax=3, interpolation="nearest")
    ax.set(title="reversed, ONE bit flipped:\ncomes back only partly", xticks=[], yticks=[])
    ax.grid(False)
    ax = fig.add_subplot(gs[1, :])
    tt = np.arange(T + 1)
    ax.plot(tt, Sf, color=S1, lw=2, label="forward: entropy rises")
    ax.plot(T + tt, ex_S, color=S3, lw=2, label="all velocities reversed: exact return (bit-for-bit)")
    ax.plot(T + tt, pt_S, color=S2, lw=2, ls="--", label=f"reversed with one bit flipped: never returns exactly ({int(np.sum(pt_y != g0)):,} bits wrong)")
    ax.axvline(T, color=MUTED, ls=":", lw=1.2)
    ax.text(T + 8, 27500, "velocities reversed", color=INK_2, fontsize=9)
    ax.set(xlabel="time step", ylabel="coarse-grained entropy (nats)",
           title="An exactly reversible substrate still shows an arrow: it comes from the low-entropy start")
    ax.legend(loc="lower center", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "reversible_gas")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]
    # Hasse diagram (links only) of the grown causal set; height = longest chain below
    height = np.zeros(n)
    for j in range(n):
        below = np.where(rel[:, j])[0]
        height[j] = 0 if len(below) == 0 else height[below].max() + 1
    xs = np.zeros(n)
    for h in np.unique(height):
        idx = np.where(height == h)[0]
        xs[idx] = np.linspace(-1, 1, len(idx) + 2)[1:-1] if len(idx) > 1 else 0
    link = rel & ~((rel.astype(int) @ rel.astype(int)) > 0)
    for i in range(n):
        for j in range(n):
            if link[i, j]:
                ax.plot([xs[i], xs[j]], [height[i], height[j]], color=MUTED, lw=1)
    ax.plot(xs, height, "o", color=S1, ms=9)
    for i in range(n):
        ax.text(xs[i] + 0.06, height[i] + 0.08, str(i), fontsize=7.5, color=INK_2)
    ax.annotate("", xy=(1.25, height.max()), xytext=(1.25, 0), arrowprops=dict(arrowstyle="->", color=S2, lw=1.8))
    ax.text(1.3, height.max() / 2, "one way\n(no loops)", color=S2, fontsize=9, va="center")
    ax.set(xlim=(-1.3, 1.8), xticks=[], ylabel="longest chain below (a clock's count)",
           title=f"A grown causal set: {lin} birth orders,\none and the same universe")
    ax.grid(False)
    ax = axs[1]
    pts = [(1e-15, 4.0, "kaon T violation\n(4σ, CPLEAR)", S2), (1e-15, 14.0, "B-meson T violation\n(14σ, BaBar)", S2),
           (2e5, 2.2, "black-hole area\ntheorem (97%)", S3)]
    for x_, y_, lab, col in pts:
        ax.plot(x_, y_, "o", color=col, ms=9)
        ax.text(x_ * 3, y_, lab, fontsize=8.5, color=INK_2, va="center")
    ax.axhspan(0, 1, color="#ebeae6", lw=0)
    ax.text(1e-14, 0.45, "electron EDM: no extra T violation (< 4×10⁻³⁰ e·cm)", fontsize=8.5, color=INK_2)
    ax.annotate("second law: no exception\nfrom atoms to galaxies", xy=(1e3, 8), fontsize=9, color=S1, ha="center")
    ax.annotate("low-entropy beginning:\nS ≈ 10¹⁰⁴ k now, max ≈ 10¹²² k", xy=(3e20, 11), fontsize=9, color=S3, ha="center")
    ax.set_xscale("log")
    ax.set(xlim=(1e-17, 1e28), ylim=(0, 16), xlabel="length scale (m)", ylabel="significance of the arrow (σ)",
           title="Measured arrows of time, from mesons to the cosmos")
    fig.tight_layout()
    save_fig(fig, NAME, "growth_and_measured")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
