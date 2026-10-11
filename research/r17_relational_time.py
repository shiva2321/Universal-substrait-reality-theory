"""
r17 - Time in the substrate: relational, relative to motion and to gravity  (LAB_NOTEBOOK.md entry E23)

Question (user): "Time is relational, but it is not absolute either. It can vary based on how fast
something is moving in relation to something else. But it is one way only, it can't go back. Even
at the substrate level. We also need tests and experiments on this, from the smallest to the
highest magnitudes."  (The one-way part is r18; causal sets are r19.)

  A. RELATIONAL: Page-Wootters.  A static universe (total constraint J|Psi> = 0) containing a clock
     and a system.  Conditioning on the clock reading gives exactly the Schroedinger evolution of
     the system: time exists only as a correlation.  Exact (finite-dimensional, machine precision).
  B. RELATIVE TO MOTION: a clock built from substrate waves (a sine-Gordon breather) moving at v
     ticks slower by exactly gamma in the continuum.  Measured on lattices of spacing h: the error
     falls as h^2.  On a COARSE lattice time dilation fails -- the lattice substrate's signature.
  C. RELATIVE TO GRAVITY: the same clock sitting in a well where the substrate's local rate N(x)
     is lower.  The covariant medium (every internal rate scales with N) gives the gravitational
     redshift exactly; r08's medium (only the wave speed changes) gives none -> confronted with
     GP-A / Galileo.
  D. GPS, computed: special- and general-relativistic clock shifts per day.
  E. The measured ladder of time-dilation tests, from a millimetre to the Hubble scale.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.linalg import expm, null_space  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, save_fig, style  # noqa: E402

NAME = "r17_relational_time"
W = 0.6                                     # breather internal frequency (units of the substrate's omega_0)
T_REST = 2 * math.pi / W
GALILEO_ALPHA = (0.19e-5, 2.48e-5)          # redshift violation, Delva et al. PRL 121, 231101 (2018)


# ---------------------------------------------------------------- A. Page-Wootters
def page_wootters(d=16):
    Ek = 2 * np.pi * np.arange(-d // 2, d // 2) / d          # clock: evenly spaced levels (tick = 1)
    HC = np.diag(Ek)
    U = expm(-1j * 0.4 * np.array([[0, 1], [1, 0]]))
    HS = U @ np.diag([2 * np.pi * 3 / d, -2 * np.pi * 2 / d]) @ U.conj().T   # system: a qubit
    J = np.kron(HC, np.eye(2)) + np.kron(np.eye(d), HS)       # total 'energy' = constraint
    psi0 = np.array([1, 0], complex)
    ev, V = np.linalg.eigh(HS)
    Psi = np.zeros(2 * d, complex)
    for e, vec in zip(ev, V.T):
        k = int(np.argmin(abs(Ek + e)))
        clock = np.zeros(d)
        clock[k] = 1
        Psi += np.kron(clock, vec) * (vec.conj() @ psi0)
    Psi /= np.linalg.norm(Psi)
    rows = []
    for t in range(d):
        tstate = np.exp(-1j * Ek * t) / np.sqrt(d)
        cond = (np.kron(tstate.conj()[None, :], np.eye(2)) @ Psi) * np.sqrt(d) * np.sqrt(2) / np.sqrt(2)
        cond = cond / np.linalg.norm(cond)
        target = expm(-1j * HS * t) @ psi0
        ov = abs(np.vdot(target, cond))
        sx = np.real(np.vdot(cond, np.array([[0, 1], [1, 0]]) @ cond))
        sx_t = np.real(np.vdot(target, np.array([[0, 1], [1, 0]]) @ target))
        rows.append((t, 1 - ov, sx, sx_t))
    stat = max(abs(abs(np.vdot(Psi, expm(-1j * J * s) @ Psi)) - 1) for s in (0.7, 3.1, 11.0))
    return null_space(J).shape[1], np.linalg.norm(J @ Psi), rows, stat, HS, psi0


# ---------------------------------------------------------------- B/C. breather clocks
def breather(x, t, w, v=0.0):
    g = 1 / math.sqrt(1 - v * v)
    s = math.sqrt(1 - w * w)
    return 4 * np.arctan((s / w) * np.sin(w * g * (t - v * x)) / np.cosh(s * g * (x - v * t)))


def period_from_zero_crossings(ts, vals):
    zc = [ts[i] - vals[i] * (ts[i + 1] - ts[i]) / (vals[i + 1] - vals[i])
          for i in range(len(vals) - 1) if vals[i] * vals[i + 1] < 0]
    zc = np.array(zc[1:-1])
    return 2 * (zc[-1] - zc[0]) / (len(zc) - 1)


def moving_clock(v, h, w=W, L=160.0, nper=6):
    """Leapfrog on a periodic lattice; the clock reading is the field at the breather's energy centre."""
    x = np.arange(-L / 2, L / 2, h)
    g = 1 / math.sqrt(1 - v * v)
    dt = 0.4 * h
    phi, phim = breather(x, 0, w, v), breather(x, -dt, w, v)
    th = 2 * np.pi * (x + L / 2) / L
    ts, vals = [], []
    for n in range(int(nper * 2 * math.pi * g / w / dt)):
        lap = (np.roll(phi, 1) - 2 * phi + np.roll(phi, -1)) / h ** 2
        phin = 2 * phi - phim + dt * dt * (lap - np.sin(phi))
        if n % 2 == 0:
            pt = (phin - phim) / (2 * dt)
            px = (np.roll(phi, -1) - np.roll(phi, 1)) / (2 * h)
            e = 0.5 * pt ** 2 + 0.5 * px ** 2 + (1 - np.cos(phi))
            xc = L / (2 * np.pi) * math.atan2(np.sum(e * np.sin(th)), np.sum(e * np.cos(th))) - L / 2
            xc = (xc + L / 2) % L - L / 2
            vals.append(np.interp(xc, x, phi, period=L))
            ts.append(n * dt)
        phim, phi = phi, phin
    return period_from_zero_crossings(np.array(ts), np.array(vals))


def clock_in_well(A, form, w=W, h=0.05, Lw=40.0, Lbox=300.0, nper=8):
    """Breather at rest at the bottom of a well N(x) = 1 - A exp(-x^2/2Lw^2).
    'covariant': phi_tt = N d(N d phi) - N^2 sin phi   (every internal rate scales with N)
    'r08':       phi_tt = d(N^2 d phi) - sin phi        (only the wave speed changes, as in r08)"""
    x = np.arange(-Lbox / 2, Lbox / 2, h)
    N = 1 - A * np.exp(-x ** 2 / (2 * Lw ** 2))
    Nh = 1 - A * np.exp(-((x + h / 2) ** 2) / (2 * Lw ** 2))
    i0 = int(np.argmin(abs(x)))
    N0 = N[i0]
    dt = 0.4 * h
    if form == "covariant":
        phi, phim = breather(x, 0, w), breather(x, -N0 * dt, w)
    else:
        phi, phim = breather(x / N0, 0, w), breather(x / N0, -dt, w)
    ts, vals = [], []
    for n in range(int(nper * 2 * math.pi / (w * (N0 if form == "covariant" else 1)) / dt)):
        dp = (np.roll(phi, -1) - phi) / h
        if form == "covariant":
            flux = Nh * dp
            acc = N * (flux - np.roll(flux, 1)) / h - N ** 2 * np.sin(phi)
        else:
            flux = Nh ** 2 * dp
            acc = (flux - np.roll(flux, 1)) / h - np.sin(phi)
        phin = 2 * phi - phim + dt * dt * acc
        phim, phi = phi, phin
        ts.append((n + 1) * dt)
        vals.append(phi[i0])
    return T_REST / period_from_zero_crossings(np.array(ts), np.array(vals)), N0


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Relational time (Page-Wootters): a static universe whose parts see time pass")
    nd, jres, rows, stat, HS, psi0 = page_wootters()
    p(f"clock: 16 evenly spaced levels; system: a qubit; constraint J = H_clock + H_system")
    p(f"physical states (J Psi = 0): {nd}-dimensional;  |J Psi| = {jres:.1e}")
    p(f"the WHOLE universe does not change: max | |<Psi|exp(-iJs)|Psi>| - 1 | = {stat:.1e}")
    p(f"but the system, read relative to the clock, evolves exactly by Schroedinger's equation:")
    p(f"   max infidelity over 16 clock readings = {max(r[1] for r in rows):.1e}")
    p("=> time is a RELATION between parts (clock reading <-> system state), not an external")
    p("   parameter. Realised with entangled photons: Moreva et al., PRA 89, 052122 (2014).")

    p.section("B. Relative to motion: a clock made of substrate waves (sine-Gordon breather)")
    p(f"breather internal frequency {W} (rest period {T_REST:.4f}); continuum prediction T(v) = gamma T_rest")
    vs = [0.0, 0.3, 0.5, 0.7, 0.8]
    fine = {}
    for v in vs:
        g = 1 / math.sqrt(1 - v * v)
        devs = [moving_clock(v, h) / T_REST / g - 1 for h in (0.1, 0.05, 0.025)]
        rich = (4 * devs[2] - devs[1]) / 3
        fine[v] = devs[2]
        p(f"   v = {v:.1f} (gamma {g:.4f}): T/(gamma T_rest) - 1 = {devs[0]:+.2e} (h=0.1), {devs[1]:+.2e} (h=0.05),"
          f" {devs[2]:+.2e} (h=0.025); h->0 extrapolation {rich:+.1e}")
    p("=> the deviation falls as h^2: in the continuum the substrate clock obeys time dilation EXACTLY")
    p("   (the wave equation is Lorentz invariant). Nobody tells the clock to slow down: moving costs")
    p("   the internal oscillation part of its fixed budget of signal speed.")
    coarse_rest = moving_clock(0.0, 0.5)
    coarse = {}
    for v in vs:
        g = 1 / math.sqrt(1 - v * v)
        coarse[v] = moving_clock(v, 0.5) / coarse_rest / g - 1
        p(f"   COARSE lattice (h = 0.5): v = {v:.1f}: T(v)/(gamma T(0)) - 1 = {coarse[v]:+.3e}")
    p("=> on a lattice whose cells are not small compared with the clock, time dilation is broken")
    p("   (here 22% at v = 0.8). A real lattice substrate shows this at momenta ~ hbar/a: tested by")
    p("   the highest-gamma particles (cosmic rays, gamma ~ 1e11), which see no such effect")
    p("   (Coleman & Glashow, PRD 59, 116008 (1999): speed differences < ~1e-23).")

    p.section("C. Relative to gravity: the same clock at the bottom of a substrate well")
    well = {}
    for A in (0.0, 0.1, 0.2, 0.3):
        rc, N0 = clock_in_well(A, "covariant")
        rr, _ = clock_in_well(A, "r08")
        well[A] = (N0, rc, rr)
        p(f"   well depth A = {A:.1f} (local rate N0 = {N0:.3f}): tick rate seen from far away:"
          f" covariant medium {rc:.5f}, r08 medium {rr:.5f}")
    p("=> covariant medium: clocks deep in the well tick slower by exactly N0 (residual ~3e-4 from the")
    p("   well's curvature over the clock's size) = the gravitational redshift. r08's medium (only")
    p("   the wave speed lowered): NO redshift. Measurement (Galileo 5 & 6, Delva et al. 2018):")
    p(f"   redshift violation alpha = ({GALILEO_ALPHA[0]:.2e} +- {GALILEO_ALPHA[1]:.2e})")
    p(f"   covariant medium alpha = 0: {abs(0 - GALILEO_ALPHA[0]) / GALILEO_ALPHA[1]:.2f} sigma;"
      f" r08 medium alpha = -1: {abs(-1 - GALILEO_ALPHA[0]) / GALILEO_ALPHA[1]:.1e} sigma -> EXCLUDED")
    p("   Correction to r08/E12: trapped energy must lower the wave speed AND every internal rate by the")
    p("   same factor N(x) (the lapse). Free fall stays universal (Killing energy 8 m N(x)), and now")
    p("   clocks redshift correctly. 'Time runs at the local rate of the substrate.'")

    p.section("D. GPS: both effects in daily life (computed)")
    GM, RE, a_gps = 3.986004418e14, 6.378137e6, 2.6561750e7
    v_gps = math.sqrt(GM / a_gps)
    day = 86400.0
    sr = -v_gps ** 2 / (2 * c ** 2) * day * 1e6
    gr = GM / c ** 2 * (1 / RE - 1 / a_gps) * day * 1e6
    p(f"orbit radius {a_gps / 1e3:.0f} km, speed {v_gps / 1e3:.3f} km/s")
    p(f"   motion (special relativity): {sr:+.2f} us/day;  height (gravity): {gr:+.2f} us/day;  net {sr + gr:+.2f} us/day")
    p(f"   uncorrected, that is {abs(sr + gr) * 1e-6 * c / 1e3:.1f} km of ranging error per day: GPS corrects for it.")

    p.section("E. The measured ladder of time dilation, smallest to largest scale")
    ladder = [
        ("Bothwell et al. 2022 (Sr lattice clock)", 1e-3, "gravity", None, None,
         "redshift resolved inside a 1 mm atomic sample (Nature 602, 420)"),
        ("Chou et al. 2010 (Al+ clocks, 33 cm)", 0.33, "gravity", 4.1 / (9.80 * 0.33 / c ** 2 * 1e17), 1.6 / (9.80 * 0.33 / c ** 2 * 1e17),
         "(4.1 +- 1.6)e-17 measured vs 3.6e-17 predicted (Science 329, 1630)"),
        ("Pound & Snider 1965 (22.5 m tower)", 22.5, "gravity", 0.9990, 0.0076, "Phys. Rev. 140, B788"),
        ("Hafele & Keating 1971 (westward flight)", 4e7, "motion+gravity", 273 / 275, math.hypot(7 / 275, 21 * 273 / 275 ** 2),
         "+273 +- 7 ns measured vs +275 +- 21 ns predicted (Science 177, 168)"),
        ("Gravity Probe A 1976 (10,000 km)", 1e7, "gravity", None, 7e-5, "agreement to 7e-5 (Vessot et al., PRL 45, 2081)"),
        ("Galileo 5 & 6 (eccentric orbits)", 2.8e7, "gravity", 1 + GALILEO_ALPHA[0], GALILEO_ALPHA[1], "Delva et al., PRL 121, 231101 (2018)"),
        ("Ives-Stilwell, Li+ at 0.34c (storage ring)", 1e2, "motion", None, 2e-8, "Botermann et al., PRL 113, 120405 (2014)"),
        ("S2 star at the Galactic Centre", 1.8e13, "gravity", 0.90, math.hypot(0.09, 0.15), "GRAVITY Collab., A&A 615, L15 (2018)"),
        ("Type Ia supernovae (DES), z to 1.2", 1e26, "cosmic", 1.003, 0.005, "light curves stretched by (1+z)^b (White et al. 2024)"),
        ("Quasar variability, z to 4.3", 2e26, "cosmic", 1.28, 0.285, "Lewis & Brewer, Nature Astron. 7, 1265 (2023)"),
    ]
    for name, L, kind, val, err, note in sorted(ladder, key=lambda r: r[1]):
        if val is None and err is None:
            p(f"   {L:8.0e} m  {name:44s} {note}")
        elif val is None:
            p(f"   {L:8.0e} m  {name:44s} consistent at the {err:.0e} level  [{note}]")
        else:
            p(f"   {L:8.0e} m  {name:44s} measured/predicted = {val:.6g} +- {err:.2g}  ({abs(val - 1) / err:.1f} sigma)  [{note}]")
    p("=> every test, from a millimetre to across the universe, agrees with relativistic time")
    p("   dilation. Any substrate must reproduce all of them: the covariant medium (B, C) does.")

    # ---------- figure
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    ax = axs[0, 0]
    tt = np.linspace(0, 15, 300)
    sx = [np.real(np.vdot(expm(-1j * HS * t) @ psi0, np.array([[0, 1], [1, 0]]) @ (expm(-1j * HS * t) @ psi0))) for t in tt]
    ax.plot(tt, sx, color=MUTED, lw=1.5, ls="--", label="Schrödinger evolution (external time)")
    ax.plot([r[0] for r in rows], [r[2] for r in rows], "o", color=S1, ms=7, label="system read relative to the clock")
    ax.axhline(1.02, color=S2, lw=2)
    ax.text(0.2, 1.06, "whole universe: static (J Ψ = 0)", color=S2, fontsize=9)
    ax.set(xlabel="clock reading", ylabel="system observable ⟨σx⟩", ylim=(-1.15, 1.25),
           title="Relational time: a static universe whose parts\nsee each other change")
    ax.legend(loc="lower left", fontsize=8.5)

    ax = axs[0, 1]
    vv = np.linspace(0, 0.85, 200)
    ax.plot(vv, 1 / np.sqrt(1 - vv ** 2), color=MUTED, ls="--", lw=1.5, label="relativity: γ")
    ax.plot(vs, [(1 + fine[v]) / math.sqrt(1 - v * v) for v in vs], "o", color=S1, ms=8,
            label="substrate clock, fine lattice (h = 0.025)")
    ax.plot(vs, [(1 + coarse[v]) / math.sqrt(1 - v * v) for v in vs], "s", color=S2, ms=7,
            label="substrate clock, coarse lattice (h = 0.5)")
    ax.set(xlabel="clock speed v / c", ylabel="period, relative to the same clock at rest",
           title="Moving clocks made of substrate waves tick slower:\nexactly γ, unless the cells are coarse")
    ax.legend(loc="upper left", fontsize=8.5)

    ax = axs[1, 0]
    Ns = [well[A][0] for A in well]
    ax.plot([0.65, 1.02], [0.65, 1.02], color=MUTED, ls="--", lw=1.4, label="gravitational redshift (GR)")
    ax.plot(Ns, [well[A][1] for A in well], "o", color=S1, ms=8, label="covariant medium (all rates ∝ N)")
    ax.plot(Ns, [well[A][2] for A in well], "s", color=S2, ms=7, label="r08 medium (only wave speed ∝ N)")
    ax.set(xlabel="local substrate rate N at the clock", ylabel="tick rate seen from far away",
           xlim=(0.65, 1.02), ylim=(0.65, 1.05),
           title="Clocks deep in a substrate well tick slower\nonly if every internal rate scales with N")
    ax.legend(loc="lower right", fontsize=8.5)

    ax = axs[1, 1]
    col = {"gravity": S1, "motion": S2, "motion+gravity": S2, "cosmic": S3}
    labpos = {"Chou et al. 2010 (Al+ clocks, 33 cm)": (2.0, 0.06, "left", "Chou et al. 2010"),
              "Pound & Snider 1965 (22.5 m tower)": (0.5, -0.09, "left", "Pound & Snider"),
              "Hafele & Keating 1971 (westward flight)": (1.0, 0.12, "center", "Hafele & Keating"),
              "S2 star at the Galactic Centre": (2.0, -0.05, "left", "S2 star (Galactic Centre)"),
              "Type Ia supernovae (DES), z to 1.2": (0.4, -0.09, "right", "supernovae"),
              "Quasar variability, z to 4.3": (0.4, 0.0, "right", "quasars")}
    seen = set()
    for name, L, kind, val, err, note in ladder:
        if val is None or err < 0.004:
            continue
        k = "motion" if kind.startswith("motion") else kind
        lab = None if k in seen else {"gravity": "gravity (height)", "motion": "motion (speed)", "cosmic": "cosmic expansion"}[k]
        seen.add(k)
        ax.errorbar(L, val, yerr=err, fmt="o", color=col[kind], ms=6, capsize=3, label=lab)
        fx, dy, ha, short = labpos[name]
        ax.text(L * fx, val + dy, short, fontsize=8, color=INK_2, ha=ha)
    ax.axhline(1, color=MUTED, ls="--", lw=1.2)
    ax.text(3e9, 0.47, "too precise to show here: Galileo ±2.5×10⁻⁵,\nGravity Probe A 7×10⁻⁵, Ives–Stilwell 2×10⁻⁸",
            fontsize=8, color=INK_2)
    ax.set_xscale("log")
    ax.set(xlabel="size of the experiment (m)", ylabel="measured / predicted time dilation",
           ylim=(0.4, 1.9), xlim=(1e-2, 1e28),
           title="Time-dilation tests from 33 cm to the Hubble scale\nall agree with relativity")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "relational_time")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
