"""
r32 - Is the lumpiness in the light or in the detector?  And the energy numbers behind "10^19", the vase and the black hole
(LAB_NOTEBOOK.md entry E44)

Question (user): "it could be that one is light's property and the other is its causality because it interacts with the
surrounding space and matter..."  (light's wave and particle sides), and, on space and time: "a broken vase cant be undone
... unless the vase is converted to pure energy ... the required energy would be astronomical", "breaking it ... like in
black hole .... which requires 10^19 magnitude of energy".

Method:
  A. Test the idea that light is a smooth wave and only its *interaction with matter* is lumpy (the semiclassical picture of
     Lamb & Scully 1969).  Heralded beam-splitter experiment (Grangier, Roger & Aspect 1986): a gate event opens a window, the
     light in the window meets a 50:50 mirror, and two detectors T and R count clicks.  With N_G gates and counts N_T, N_R,
     N_TR (both clicked), alpha = N_G N_TR / (N_T N_R).  If light is a classical wave of intensity I and each detector clicks
     with probability proportional to the intensity it receives, then alpha = <I^2> / <I>^2 >= 1 for ANY intensity pattern.
     If each window holds one single photon, the photon goes to T or R as a whole and alpha is close to 0.
     Simulate both with the same average click rates and the same dark counts.
  B. Plain-unit arithmetic for the replies: the rest energy of a 1 kg vase, the Planck energy in joules and in litres of
     petrol, the LHC energy, the Schwarzschild radius of a vase, the Earth and the Sun, the stiffness of space c^4 / 8 pi G
     and the bending of starlight at the Sun's edge.
Inputs typed from the literature (not computed here): the 1986 violation of the classical bound by about 13 standard
deviations, and a teaching-laboratory value alpha = 0.0188 +- 0.0067 (both from search summaries, not from the papers).
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
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, save_fig, style  # noqa: E402

NAME = "r32_light_lumps_and_energy_scales"
RNG = np.random.default_rng(32)

N_GATES = 4_000_000
ETA = 0.10                  # detection efficiency of the single-photon model
P_CLICK = ETA / 2.0         # mean click probability per detector, the same in every model
DARK = 1.0e-3               # dark-count probability per detector per window, the same in every model

ALPHA_TEACHING_LAB = (0.0188, 0.0067)     # modern spontaneous-down-conversion value (Reed College page; not re-checked)
SIGMA_1986 = 13.0                         # violation of alpha >= 1 in the 1986 experiment, in sigma (secondary account)

MT_TNT, HIROSHIMA = 4.184e15, 6.276e13    # joules per megaton and per 15 kt
PETROL_J_PER_L = 34.0e6
M_EARTH, M_SUN, R_SUN = 5.9722e24, 1.98847e30, 6.957e8


def alpha_from_clicks(t, r):
    """alpha = N_G N_TR / (N_T N_R) and its approximate Poisson error."""
    n_t, n_r, n_tr = int(t.sum()), int(r.sum()), int((t & r).sum())
    alpha = len(t) * n_tr / (n_t * n_r)
    return alpha, alpha * math.sqrt(1.0 / n_tr + 1.0 / n_t + 1.0 / n_r)


def classical_wave(intensity):
    """Smooth classical wave of relative intensity I (mean 1) per window; each detector, behind a 50:50 mirror, clicks
    independently with probability proportional to I (plus dark counts).  Matter is lumpy, light is not."""
    p = np.minimum(1.0, P_CLICK * intensity)
    t = (RNG.random(N_GATES) < p) | (RNG.random(N_GATES) < DARK)
    r = (RNG.random(N_GATES) < p) | (RNG.random(N_GATES) < DARK)
    return alpha_from_clicks(t, r)


def single_photons():
    """One photon per window, sent to T or R as a whole, detected with probability ETA (plus dark counts)."""
    to_t = RNG.random(N_GATES) < 0.5
    seen = RNG.random(N_GATES) < ETA
    t = (to_t & seen) | (RNG.random(N_GATES) < DARK)
    r = (~to_t & seen) | (RNG.random(N_GATES) < DARK)
    return alpha_from_clicks(t, r)


def alpha_single_photon_exact():
    p_photon_click = ETA + DARK - ETA * DARK
    p_t = 0.5 * p_photon_click + 0.5 * DARK
    return p_photon_click * DARK / p_t ** 2


def schwarzschild_radius(mass):
    return 2.0 * G0 * mass / c ** 2


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. Is the lumpiness in the light, or only in the detector?")
    # ------------------------------------------------------------------------------------------------------
    p("Setup: heralded beam-splitter experiment (Grangier, Roger & Aspect 1986).  alpha = N_G N_TR / (N_T N_R);")
    p("alpha = 1 means the two detectors click independently, alpha < 1 means they avoid clicking together.")
    p(f"Every model below has the same mean click probability per detector ({P_CLICK:.3f}) and dark counts ({DARK:g});")
    p(f"{N_GATES:,d} gate windows each.")
    p("Classical wave of intensity I per window, clicks proportional to I: alpha = <I^2> / <I>^2 >= 1 (Cauchy-Schwarz),")
    p("whatever the intensity pattern; a smooth wave can never make the detectors avoid each other.")
    p("")
    models = []
    a, e_ = classical_wave(np.ones(N_GATES))
    models.append(("smooth wave, constant intensity", a, e_, 1.0))
    a, e_ = classical_wave(RNG.gamma(4.0, 0.25, N_GATES))
    models.append(("smooth wave, gamma-fluctuating (k = 4)", a, e_, 1.0 + 1.0 / 4.0))
    a, e_ = classical_wave(RNG.exponential(1.0, N_GATES))
    models.append(("smooth wave, thermal light (k = 1)", a, e_, 2.0))
    a, e_ = single_photons()
    models.append(("single photons, one per window", a, e_, alpha_single_photon_exact()))
    p(f"    {'model':<42s} {'alpha simulated':>18s} {'alpha expected':>15s}")
    for name, a, e_, expected in models:
        p(f"    {name:<42s} {a:12.3f} +- {e_:5.3f} {expected:15.3f}")
    classical_min = min(m[1] for m in models[:3])
    single = models[3][1]
    p("")
    p("Real experiments (typed in, from search summaries, not re-checked against the papers):")
    p(f"    1986 atomic cascade: classical bound alpha >= 1 violated by about {SIGMA_1986:.0f} standard deviations;")
    p(f"    a modern teaching-laboratory down-conversion source: alpha = {ALPHA_TEACHING_LAB[0]} +- {ALPHA_TEACHING_LAB[1]}")
    p("    (alpha equals the second-order coherence g2(0) of the light).")
    p("What the toy shows: the 'smooth wave + lumpy detector' picture explains the photoelectric effect (Lamb & Scully 1969:")
    p("a classical wave acting on quantum matter) but cannot make two detectors avoid clicking together; single photons can.")
    p("So the lumpiness is in the light itself.  Lamb and Scully's own claim was narrower: other effects, such as blackbody")
    p("radiation, Compton scattering and spontaneous emission, do need the quantised field (per search summaries).")
    p("A pilot-wave reading (de Broglie-Bohm) keeps a real wave AND a real particle riding on it: the closest standing")
    p("version of 'one is the light's property, the other what we meet when it interacts'; its predictions equal quantum theory's.")

    # ======================================================================================================
    p.section("B. Numbers behind the vase, the Planck energy and the black hole")
    # ------------------------------------------------------------------------------------------------------
    e_vase = 1.0 * c ** 2
    e_planck = math.sqrt(hbar * c ** 5 / G0)
    e_lhc = 13.6e12 * eV
    e_photon = 2.4 * eV
    stiffness = c ** 4 / (8.0 * math.pi * G0)
    p("Vase (1 kg) turned entirely into energy, E = m c^2:")
    p(f"    {e_vase:.3e} J = {e_vase / MT_TNT:.1f} megatons of TNT = {e_vase / HIROSHIMA:,.0f} Hiroshima-size bombs.")
    p("    Turning pure energy back into matter makes equal amounts of matter and antimatter, not an ordinary vase, and the")
    p("    exact atom-by-atom arrangement is gone; gluing the pieces needs no such energy but cannot undo the heat and scatter.")
    p("Planck energy ('10^19'):")
    p(f"    E_P = sqrt(hbar c^5 / G) = {e_planck:.3e} J = {e_planck / eV / 1e9:.2e} GeV = {e_planck / PETROL_J_PER_L:.0f} litres of petrol,")
    p(f"    {e_planck / e_lhc:.1e} times one LHC collision ({e_lhc:.2e} J).  It is large per particle, not in joules:")
    p(f"    a 1 kg vase holds {e_vase / e_planck:.1e} Planck energies, spread over about 1e26 atoms.")
    p("Black holes form by squeezing, not by a special energy: r_s = 2 G M / c^2.")
    for name, mass in (("1 kg vase", 1.0), ("Earth", M_EARTH), ("Sun", M_SUN), ("Planck mass", math.sqrt(hbar * c / G0))):
        rs = schwarzschild_radius(mass)
        nice = f" ({rs * 1e3:.2f} mm)" if 1e-3 < rs < 1.0 else (f" ({rs / 1e3:.2f} km)" if rs > 1e3 else "")
        p(f"    {name:<12s} M = {mass:.3e} kg  ->  squeeze to r_s = {rs:.3e} m{nice}")
    bend = 4.0 * G0 * M_SUN / (c ** 2 * R_SUN) * 206264.806
    p("Stiffness of space:")
    p(f"    c^4 / (8 pi G) = {stiffness:.2e} N (r03); the whole Sun bends starlight at its edge by only {bend:.3f} arcseconds.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("Light's lumpiness is only in the detector (smooth wave + quantum matter)",
         f"NOT ENOUGH: any smooth wave gives alpha >= 1 (simulated minimum {classical_min:.2f}); single photons give "
         f"{single:.2f}; real experiments find alpha far below 1"),
        ("The photoelectric effect needs photons",
         "NOT BY ITSELF (Lamb & Scully 1969 reproduce it with a classical wave and quantum matter); other effects do"),
        ("Un-breaking a vase needs it turned into energy",
         f"NOT NEEDED, and not sufficient: {e_vase / MT_TNT:.1f} Mt TNT per kg, and energy alone returns matter plus antimatter"),
        ("'10^19' is the energy that breaks space",
         f"IT IS A PER-PARTICLE SCALE: {e_planck:.2e} J ({e_planck / PETROL_J_PER_L:.0f} litres of petrol); black holes form by squeezing"),
        ("Space is extremely stiff but not infinitely",
         f"c^4 / 8 pi G = {stiffness:.1e} N; the Sun bends starlight by {bend:.2f} arcseconds"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<74s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(13.0, 5.4))

    ax = axs[0]
    names = ["smooth wave\nconstant", "smooth wave\nk = 4", "smooth wave\nthermal", "single\nphotons", "measured\n(teaching lab)"]
    vals = [models[0][1], models[1][1], models[2][1], models[3][1], ALPHA_TEACHING_LAB[0]]
    errs = [models[0][2], models[1][2], models[2][2], models[3][2], ALPHA_TEACHING_LAB[1]]
    cols = [S1, S1, S1, S2, S3]
    ax.bar(range(5), vals, color=cols, width=0.62, yerr=errs, capsize=4, ecolor=INK_2)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    for xpos, v in enumerate(vals):
        ax.text(xpos, v + max(errs[xpos], 0.02) + 0.05, f"{v:.2f}", ha="center", fontsize=9.5, color=INK_2)
    ax.set_xticks(range(5), names, fontsize=9)
    ax.set(ylim=(0, 2.5), ylabel="α: do the two detectors click together?  (1 = independent)",
           title="Beam-splitter test: smooth wave + lumpy detector vs single photons")
    ax.text(4.35, 1.06, "classical bound α ≥ 1", fontsize=9, color=INK_2, ha="right")

    ax = axs[1]
    labels = ["one visible photon", "one LHC collision (two protons)", "a car's fuel tank (58 L of petrol)",
              "Planck energy (one particle)", "1 kg vase, E = mc²"]
    energies = [e_photon, e_lhc, 58.0 * PETROL_J_PER_L, e_planck, e_vase]
    ax.plot(energies, range(5), "o", color=S1, ms=9)
    ax.set_xscale("log")
    for ypos, en in enumerate(energies):
        ax.text(en * 3.0, ypos, f"{en:.1e} J", va="center", fontsize=9.5, color=INK_2)
    ax.set_yticks(range(5), labels, fontsize=9.5)
    ax.set(xlim=(1e-21, 1e26), ylim=(-0.6, 4.6), xlabel="energy (joules, log scale)",
           title="Energy scales: the Planck energy is a car's tank of petrol")

    fig.tight_layout()
    save_fig(fig, NAME, "lumps_and_scales")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
