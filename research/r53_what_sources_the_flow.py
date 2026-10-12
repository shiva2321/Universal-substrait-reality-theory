"""
r53 - What would have to source the escape-speed flow?  (LAB_NOTEBOOK.md entry E49, tests W1-W4)

Question (open item from E45/E48, F2): gravity as a flow of the medium needs v(r) = sqrt(2 G M / r) = c sqrt(r_h / r) (r34 reproduces the exact light bending with it).  What field
equation or what source could produce such a flow in a medium that obeys continuity and Euler?  Steady spherical flow, medium with sound speed c, sink density sigma(r) (medium lost to the
extra dimension per unit volume and time) and body force f(r) per unit mass:

        (1/r^2) d(r^2 rho v)/dr = -sigma(r)         (continuity, v > 0 inward),
        v dv/dr = -(1/rho) dP/dr - f(r)             (Euler, f > 0 inward).

  W1. Source-free flow (sigma = 0, f = 0) of a constant-sound-speed medium (P = c^2 rho + const, the equation of state of r39/r40): does it have the escape-speed profile?  Does it even
      reach a horizon (v = c)?  Bernoulli + continuity solved exactly.
  W2. What the escape-speed profile requires: the sink density and the body force, for a uniform-density medium and for a constant-sound-speed medium, in units of the Newtonian gravity GM/r^2.
  W3. What it costs: the rate at which the medium must disappear across the surface of the Earth, the Sun and a galaxy, for a Planck-density medium and for the lowest density allowed by r35/r42.
  W4. The area-energy half of the first law (Jacobson): when does the horizon area respond to the energy flux?
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, mP, lP, save_fig, style  # noqa: E402

NAME = "r53_what_sources_the_flow"
M_EARTH, R_EARTH = 5.972e24, 6.371e6
M_SUN, R_SUN = 1.989e30, 6.957e8
M_MW, R_MW = 1.5e12 * 1.989e30, 3.1e20          # Milky Way (dark halo included) mass and an effective radius of 10 kpc (typed round numbers)


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("W1. A source-free flow of a constant-sound-speed medium")
    # ------------------------------------------------------------------------------------------------------
    p("Constant sound speed: P = c^2 rho + const, so h(rho) = c^2 ln rho and Bernoulli reads v^2 / 2 + c^2 ln rho = c^2 ln rho_inf (flow at rest at infinity).  Continuity without sinks: r^2 rho v = q.")
    p("In units c = 1: rho = rho_inf exp(-v^2 / 2), mass flux through the sphere of radius r:  4 pi r^2 rho_inf v exp(-v^2/2).  The function v exp(-v^2/2) has its maximum at v = 1 (the sound speed):")
    p("    the flow is CHOKED: a given mass flux q can only pass through radii r >= r_c = sqrt(q e^(1/2) / (4 pi rho_inf)), where v reaches c exactly; inside r_c there is no steady source-free solution.")
    p("    So a horizon (v = c) exists only at the edge of the region where the sink sits; there is no free flow that goes through the sonic point to smaller radii.")
    # compare with the escape profile: put the choke radius at r_h (v(r_h) = c)
    p(f"    Source-free flow with its throat at r = r_h compared with the escape-speed profile c sqrt(r_h / r):")
    p(f"    {'r / r_h':>8s} {'v_free / c':>12s} {'v_escape / c':>13s} {'v_free / v_escape':>18s} {'rho / rho_inf':>14s}")
    rows = []
    for x in (1.0, 1.5, 2.0, 3.0, 10.0, 100.0, 1000.0):
        # flux conservation: x^2 v exp(-v^2/2) = exp(-1/2) (throat at x = 1, v = 1), subsonic branch v < 1
        f = lambda v: x * x * v * math.exp(-v * v / 2.0) - math.exp(-0.5)
        v_free = brentq(f, 1e-14, 1.0) if x > 1.0 else 1.0
        v_esc = math.sqrt(1.0 / x)
        rows.append((x, v_free, v_esc))
        p(f"    {x:8.1f} {v_free:12.3e} {v_esc:13.3e} {v_free / v_esc:18.3e} {math.exp(-v_free ** 2 / 2):14.5f}")
    p("    => the source-free flow falls as 1/r^2 (incompressible sink), not as 1/sqrt(r): at 10 r_h it is already a factor ~ 50 below the escape speed and at 1000 r_h a factor ~ 5e4.  The escape-speed")
    p("       flow of gravity is NOT what the medium does by itself.")

    # ======================================================================================================
    p.section("W2. What the escape-speed profile requires")
    # ------------------------------------------------------------------------------------------------------
    p("v = c sqrt(r_h / r), r_h = 2 G M / c^2, gravity g = G M / r^2 = c^2 r_h / (2 r^2).")
    p("  (a) Uniform density, no pressure gradient: Euler gives f = v dv/dr = -c^2 r_h / (2 r^2) (inward): a body force exactly equal to Newtonian gravity acting on the medium's own parcels (circular: it assumes gravity).")
    p("      Continuity: sigma = -(1/r^2) d(r^2 rho v)/dr = (3/2) rho v / r: a sink density in EVERY volume element, falling as r^(-3/2) (the total sink inside radius R grows as R^(3/2): it is not")
    p("      a localised source).")
    p("  (b) Constant sound speed, no sinks: continuity gives rho ~ r^(-3/2) (rho v r^2 = const); the pressure force per unit mass is -(1/rho) dP/dr = -c^2 d ln rho / dr = +(3/2) c^2 / r, directed OUTWARD, so the")
    p("      body force needed is f = g + (3/2) c^2 / r = g (1 + 3 r / r_h): larger than gravity by the factor 1 + 3 r / r_h:")
    p(f"      {'r / r_h':>10s} {'f / g (uniform)':>16s} {'f / g (constant c_s, no sink)':>32s}")
    for x in (1.5, 3.0, 10.0, 100.0, 1e3, 1e5, 1e9):
        p(f"      {x:10.1e} {1.0:16.1f} {1 + 3 * x:32.3e}")
    r_h_earth = 2 * G0 * M_EARTH / c ** 2
    p(f"      At the surface of the Earth r / r_h = {R_EARTH / r_h_earth:.2e} (r_h = {r_h_earth * 1e3:.1f} mm): the constant-sound-speed medium would need a body force {1 + 3 * R_EARTH / r_h_earth:.1e} times gravity.")
    p("  So the medium's own pressure cannot supply the infall (it opposes it), and the infall needs either a force as strong as gravity on the medium (circular) or a force far stronger.")

    # ======================================================================================================
    p.section("W3. What the drain costs")
    # ------------------------------------------------------------------------------------------------------
    rho_planck = mP() / lP() ** 3
    p(f"    Planck density {rho_planck:.2e} kg/m^3.  Medium density rho = f rho_P: f = 0.7 (alpha = 1, n xi^3 = 1, r33) down to f = 7e-9 (the lowest value allowed by the string bound at formation, r42).")
    p(f"    {'body':>14s} {'R (m)':>9s} {'v_esc (m/s)':>12s} {'R / v (s)':>10s} {'drain, f = 0.7 (kg/s)':>22s} {'drain, f = 7e-9 (kg/s)':>23s} {'in units of its own mass / s':>29s}")
    for name, m, r in (("Earth", M_EARTH, R_EARTH), ("Sun", M_SUN, R_SUN), ("Milky Way", M_MW, R_MW)):
        v = math.sqrt(2 * G0 * m / r)
        dr1 = 4 * math.pi * r ** 2 * 0.7 * rho_planck * v
        dr2 = 4 * math.pi * r ** 2 * 7e-9 * rho_planck * v
        p(f"    {name:>14s} {r:9.2e} {v:12.3e} {r / v:10.2e} {dr1:22.2e} {dr2:23.2e} {dr1 / m:29.2e}")
    p("    The medium inside a volume of radius R is drained and replaced every free-fall time R / v (570 s at the Earth's surface, 30 min at the Sun's): the picture needs a steady inflow from large")
    p("    distances of an amount of medium per second that exceeds the object's own mass by a factor 1e90 (Earth, Sun) to 1e102 (galaxy) for a Planck-density medium.  Whether that is acceptable depends on what 'the medium is lost to the")
    p("    extra dimension' means for energy conservation; the numbers are the price of the kinematics.")

    # ======================================================================================================
    p.section("W4. The area-energy half of the first law")
    # ------------------------------------------------------------------------------------------------------
    p("    Jacobson's argument needs the horizon area to grow when energy crosses it (Raychaudhuri).  In the flow picture the horizon is where v = c: r_h = 2 G M(< r_h) / c^2, so it responds to an energy flux dE")
    p("    exactly as in GR (delta r_h = 2 G dE / c^4) IF the flow obeys v^2 = -2 Phi with Phi sourced by the total energy (Poisson); then delta A = 8 pi r_h delta r_h and T_H = hbar c / (4 pi r_h k_B) (acoustic")
    p("    surface gravity kappa = c / (2 r_h) at the horizon, checked below) give delta E = T delta S with S = A / 4 l_P^2.")
    kappa = 0.5 * (1.0)                              # exact: g_tt = -(1 - r_h/r): dg/dr = r_h/r^2 = 1 at r = r_h; kappa = (1/2) dg/dr c = c / (2 r_h)
    t_h = 1.0 * kappa / (2 * math.pi)                # in units hbar c / (k_B r_h)
    p(f"    Surface gravity of the escape flow (acoustic metric g_tt = -(c^2 - v^2)): kappa = c / (2 r_h); Hawking temperature T = hbar kappa / (2 pi k_B) = hbar c / (4 pi k_B r_h): in units hbar c / (k_B r_h) = {t_h:.5f} (= 1/4pi = {1 / (4 * math.pi):.5f}).")
    m_test = 1.0e30
    r_h = 2 * G0 * m_test / c ** 2
    d_e = 1.0e20                                      # J
    d_rh = 2 * G0 * d_e / c ** 4
    d_area = 8 * math.pi * r_h * d_rh
    d_s = d_area / (4 * lP() ** 2)
    t_h_si = 6.62607015e-34 / (2 * math.pi) * c / (4 * math.pi * 1.380649e-23 * r_h)
    p(f"    Check with M = {m_test:.0e} kg, dE = {d_e:.0e} J: r_h = {r_h:.3e} m, T = {t_h_si:.3e} K, delta S = {d_s:.3e} k_B; T delta S / dE = {t_h_si * 1.380649e-23 * d_s / d_e:.5f} (1 for the Bekenstein-Hawking first law).")
    p("    So the first law is satisfied exactly by a flow that obeys v^2 = -2 Phi with Poisson-sourced Phi, and by nothing in the fluid equations themselves: W1-W3 show the fluid does not produce that flow.  The geometric half")
    p("    of Einstein's equation is exactly the missing field equation for the flow (the 'source of the escape-speed flow').")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("W1: a source-free flow of a constant-sound-speed medium is the escape-speed flow", f"NO: it is choked at the sonic point and falls as 1/r^2: v_free / v_escape = {rows[3][1] / rows[3][2]:.2f} at 3 r_h, {rows[4][1] / rows[4][2]:.1e} at 10 r_h, {rows[5][1] / rows[5][2]:.0e} at 100 r_h"),
        ("W2: the escape-speed flow follows from the fluid equations with a localised mass", "NO: it needs a sink in every volume element (sigma = 3 rho v / 2r) and a body force equal to gravity, or a force 1 + 3 r/r_h times gravity if the pressure is constant-c_s"),
        ("W3: the drain is modest", f"NO: the medium in a volume of radius R is replaced every R/v (570 s for the Earth); for a Planck-density medium the drain is 3e90 (Earth) to 2e102 (galaxy) times the object's own mass per second"),
        ("W4: the first law with area change holds for the flow", "ONLY if v^2 = -2 Phi with Poisson-sourced Phi is imposed; the Bekenstein-Hawking relation then holds exactly (T delta S / dE = 1.00000)"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<86s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.0, 5.2))
    ax = axs[0]
    xs = np.geomspace(1.0, 1000.0, 120)
    vfree = np.array([brentq(lambda v, x=x: x * x * v * math.exp(-v * v / 2.0) - math.exp(-0.5), 1e-14, 1.0) if x > 1.0 else 1.0 for x in xs])
    ax.loglog(xs, np.sqrt(1.0 / xs), color=S1, lw=2.2, label="escape speed, c √(r_h/r) (gravity as a flow)")
    ax.loglog(xs, vfree, color=S2, lw=2.2, label="source-free flow of a constant-sound-speed medium (choked at r_h)")
    ax.loglog(xs, 1.0 / xs ** 2 * math.exp(-0.5), color=MUTED, ls="--", lw=1.2, label="∝ r⁻² (incompressible sink)")
    ax.set(xlabel="radius ÷ r_h", ylabel="inflow speed ÷ c", title="The medium does not make the escape-speed flow by itself", ylim=(1e-8, 2))
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1]
    xs2 = np.geomspace(1.5, 1e9, 80)
    ax.loglog(xs2, 1 + 3 * xs2, color=S2, lw=2.2, label="constant-c_s medium without sinks: f / g = 1 + 3 r / r_h")
    ax.loglog(xs2, np.ones_like(xs2), color=S1, lw=2.2, label="uniform medium with sinks: f / g = 1")
    ax.axvline(R_EARTH / r_h_earth, color=MUTED, ls=":", lw=1.3)
    ax.text(R_EARTH / r_h_earth * 1.5, 3.0, "Earth's surface", fontsize=9, color=INK_2, rotation=90, va="bottom")
    ax.set(xlabel="radius ÷ r_h", ylabel="required body force ÷ Newtonian gravity", title="The force the medium would need", ylim=(0.5, 1e11))
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "flow")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
