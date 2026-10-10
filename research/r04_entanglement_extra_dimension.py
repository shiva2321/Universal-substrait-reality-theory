"""
r04 - Can a higher dimension explain entanglement?  (2026-10-10, LAB_NOTEBOOK.md entry E7)

Idea under test: an entangled pair is ONE object in a higher-dimensional bulk, seen
from two places in our 3D membrane, so information only *seems* to travel faster
than light.  (This is David Bohm's 'fish tank' analogy: one fish filmed by two
cameras looks like two fish whose motions are mysteriously correlated.)

  A. 'One object seen twice': the outcome at each place is fixed by the object's
     state plus the local detector setting.  Monte-Carlo CHSH for a 3D object.
  B. 'Object that reacts to the far detector through the bulk at speed v': the
     later measurement can follow the quantum rule only if the bulk signal has
     arrived.  CHSH vs v for a real experiment geometry (18 km, Salart et al. 2008).
  C. Does the Randall-Sundrum bulk even offer a shortcut?  Travel time of bulk
     paths in a warped 5D geometry, symmetric (RS2) vs asymmetrically warped.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import quad  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, save_fig, style  # noqa: E402

NAME = "r04_entanglement_extra_dimension"
A_SET = (0.0, math.pi / 2)
B_SET = (math.pi / 4, 3 * math.pi / 4)


def chsh(E, a=A_SET, b=B_SET):
    return abs(E(a[0], b[0]) - E(a[0], b[1]) + E(a[1], b[0]) + E(a[1], b[1]))


def main():
    p = Report(NAME)
    style(plt)
    rng = np.random.default_rng(11)

    p.section("A. One higher-dimensional object seen from two places (local, shared state)")
    lam = rng.normal(size=(400_000, 3))
    lam /= np.linalg.norm(lam, axis=1)[:, None]

    def E_obj(a, b):
        ua = np.array([math.cos(a), math.sin(a), 0.0])
        ub = np.array([math.cos(b), math.sin(b), 0.0])
        return float(np.mean(np.sign(lam @ ua) * -np.sign(lam @ ub)))
    S_std = chsh(E_obj)
    best = 0.0
    for _ in range(300):
        ang = rng.uniform(0, 2 * math.pi, 4)
        best = max(best, chsh(E_obj, ang[:2], ang[2:]))
    p(f"CHSH at the standard settings: S = {S_std:.3f};  best over 300 random settings: S = {best:.3f}")
    p("=> however the object is shaped or oriented, if each outcome depends only on the object's state")
    p("   and the LOCAL setting, S <= 2 (Bell's theorem). Experiments give 2.4-2.8. 'Seen twice' alone fails.")

    p.section("B. The object reacts to the far detector via the bulk at finite speed v")
    d = 18e3                       # m, Geneva experiment (Salart et al., Nature 454, 861 (2008))
    S_q, S_l = 2 * math.sqrt(2), 2.0
    vv = np.logspace(0, 6, 400)    # v / c
    curves = {}
    for tau in (5e-9, 0.5e-9):     # how simultaneous the two measurements are (s)
        frac = np.clip(1 - d / (vv * c * tau), 0, 1)     # pairs whose bulk signal arrived in time
        curves[tau] = S_l + frac * (S_q - S_l)
        p(f"simultaneity {tau * 1e9:.1f} ns over {d / 1e3:.0f} km: quantum correlations need v > d/(c tau) = "
          f"{d / (c * tau):.1e} c")
    p("published lower bounds on such a 'speed of spooky action': > 1e4 c (Salart et al. 2008),")
    p("> 1.38e4 c (Yin et al., PRL 110, 260407 (2013)), in the frames those experiments test.")
    p("Bancal et al. (Nature Physics 8, 867 (2012)): ANY finite-speed hidden influence that reproduces")
    p("quantum correlations would also allow faster-than-light messaging, which is never seen.")
    p("=> a bulk channel must act effectively instantaneously and must never let a message through.")
    p("   ER = EPR (Maldacena & Susskind 2013) has exactly this property: its wormholes are NON-traversable.")
    p("   The same cord picture with another rule gives S = 4 (audit/a03): the bulk must also explain why")
    p("   nature stops at 2*sqrt(2) (Tsirelson's bound). That part is still missing.")

    p.section("C. Is the 5D bulk a shortcut?  Null paths in warped geometries")
    k, L = 1.0, 2000.0             # warp scale and brane distance (units 1/k; real distances are >> 1/k)

    def t_path(Y, n_over_a, n):
        """Go up to height Y, travel L along x, come back down; coordinate time."""
        up = quad(lambda y: 1.0 / n(y), 0, Y)[0]
        return 2 * up + L / n_over_a(Y)
    Ys = np.linspace(0, 3, 121)
    rs2 = [t_path(Y, lambda y: 1.0, lambda y: math.exp(-k * y)) / L for Y in Ys]
    eps = 0.05
    asym = [t_path(Y, lambda y: 1 + eps * math.tanh(k * y) ** 2,
                   lambda y: math.exp(-k * y) * (1 + eps * math.tanh(k * y) ** 2)) / L for Y in Ys]
    p(f"RS2 (same warp for space and time): best bulk path / brane path = {min(rs2):.4f} (never < 1: no shortcut)")
    p(f"asymmetric toy warp (bulk light speed up to {1 + eps:.2f}): best ratio = {min(asym):.4f} "
      f"at height {Ys[int(np.argmin(asym))]:.2f}/k -> shortcut")
    p("Asymmetrically warped brane-worlds do allow shortcuts (Csaki, Erlich & Grojean 2001), but GW170817:")
    p("gravity and light from 130 million light years arrived within 1.7 s -> bulk speed-up for gravity")
    p("< ~1e-15. And a shortcut is still a finite speed, so part B applies to it.")

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2))
    axs[0].semilogx(vv, curves[5e-9], color=S1, label="measurements simultaneous to 5 ns")
    axs[0].semilogx(vv, curves[0.5e-9], color=S2, label="simultaneous to 0.5 ns")
    axs[0].axhline(S_q, color=MUTED, ls="--", lw=1)
    axs[0].axhline(S_l, color=MUTED, ls="--", lw=1)
    axs[0].text(1.2, S_q + 0.03, "quantum value 2.83", color=INK_2, fontsize=9)
    axs[0].text(1.2, S_l - 0.09, "local limit 2", color=INK_2, fontsize=9)
    axs[0].axvline(1.38e4, color=S3, lw=1.5)
    axs[0].text(1.1e4, 2.45, "experiments\nrequire\nv > 1.4e4 c", color=INK_2, fontsize=9, ha="right")
    axs[0].set(xlabel="speed of the bulk signal (multiples of c)", ylabel="CHSH S over 18 km",
               ylim=(1.85, 3.0), title="A bulk link must be (near-)instant")
    axs[0].legend(loc="center left", fontsize=8.5)
    axs[1].plot(Ys, rs2, color=S1, label="RS2 warp (symmetric)")
    axs[1].plot(Ys, asym, color=S2, label=f"asymmetric warp (bulk speed up to {1 + eps:.2f}c)")
    axs[1].axhline(1.0, color=MUTED, ls="--", lw=1)
    axs[1].text(0.05, 1.005, "path along our 3D membrane", color=INK_2, fontsize=9, va="bottom")
    axs[1].set(xlabel="how far the path dips into the 5th dimension (1/k)",
               ylabel="travel time / membrane travel time", ylim=(0.94, 1.12),
               title="Only an asymmetric bulk gives a shortcut")
    axs[1].legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "bulk_channel")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
