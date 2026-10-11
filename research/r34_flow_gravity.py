"""
r34 - Gravity as a flow of the medium: what flow bends sound like gravity bends light?
(LAB_NOTEBOOK.md entry E45, test F2)

Question (user): "matter eithree creates cavity or a bubble in/on the sapce ... a still object ... is goin to follow the
direction of the ripple ... the fluide/space is moving".  r01 and the audit showed that a static density dip is short-range.
The other fluid option is a FLOW: matter drains the medium (into a hyper-dimension) and the medium streams inward.

Physics: in a medium streaming with velocity v(x), sound of speed c has the ray Hamiltonian  H = c |k| + v(x) . k  (the acoustic
metric, Unruh 1981).  Painlevé-Gullstrand form of Schwarzschild: the exact geometry of a mass M is the flat-space metric
with the medium falling inward at the escape speed v = sqrt(2 G M / r)  (the "river model").  So a flow of that profile gives
exactly general relativity's light bending, 4GM/(c^2 b) + 15 pi (GM)^2/(4 c^4 b^2) + ...

Method (units c = 1, GM = 1):
  A. Trace sound rays through three inward flows, each normalised to the same speed (0.447 c) at r = 10 GM so that only their
     shape differs: (1) escape-speed flow v ~ r^-1/2 (river model); (2) a flow LINEAR in the source, v ~ GM / (c r), the response
     a linearly sourced field would give; (3) the far field of a fluid sink in an incompressible-like medium (continuity),
     v ~ r^-2.  Compare the deflection with the exact Schwarzschild value.
  B. Scale the river flow by a factor eps and measure how the deflection depends on the flow speed.
  C. What would sustain the river flow in a conserved fluid?  Sink density, Euler equation, and the drain rates.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, lP, mP, save_fig, style  # noqa: E402

NAME = "r34_flow_gravity"
R_REF = 10.0                              # radius (in GM/c^2) where the three flows are normalised
V_REF = math.sqrt(2.0 / R_REF)            # the escape speed there, 0.447 c


def river(eps=1.0):
    return (lambda r: -eps * math.sqrt(2.0) * r ** -0.5), (lambda r: 0.5 * eps * math.sqrt(2.0) * r ** -1.5)


def linear_response():
    lam = V_REF * R_REF
    return (lambda r: -lam / r), (lambda r: lam / r ** 2)


def sink_far_field():
    q = V_REF * R_REF ** 2
    return (lambda r: -q / r ** 2), (lambda r: 2.0 * q / r ** 3)


def deflection(flow, b, x_far_factor=2000.0):
    """Deflection angle (toward the mass) of a sound ray with impact parameter b, ray Hamiltonian H = |k| + v.k."""
    f, fp = flow
    x_far = x_far_factor * b

    def rhs(_, s):
        x, y, kx, ky = s
        r = math.hypot(x, y)
        kn = math.hypot(kx, ky)
        fr, fpr = f(r), fp(r)
        xk = x * kx + y * ky
        # d_j v_i = f' x_i x_j / r^2 + f (delta_ij / r - x_i x_j / r^3);   dk_j/dt = - k_i d_j v_i
        dkx = -(fpr * x * xk / r ** 2 + fr * (kx / r - x * xk / r ** 3))
        dky = -(fpr * y * xk / r ** 2 + fr * (ky / r - y * xk / r ** 3))
        return [kx / kn + fr * x / r, ky / kn + fr * y / r, dkx, dky]

    def reached(_, s):
        return s[0] - x_far
    reached.terminal = True
    sol = solve_ivp(rhs, (0.0, 4.0 * x_far), [-x_far, b, 1.0, 0.0], method="DOP853", rtol=1e-12, atol=1e-14, events=reached)
    kx, ky = sol.y[2, -1], sol.y[3, -1]
    return -math.atan2(ky, kx)


def deflection_extrapolated(flow, b):
    """The river flow decays slowly (v ~ r^-1/2), so the finite starting distance X leaves an error that goes as X^-1/2
    (the wave vector keeps being stretched and tilted by the weak far-field inflow).  Richardson extrapolation in X^-1/2
    from X = 2000 b and 8000 b removes it."""
    return 2.0 * deflection(flow, b, 8000.0) - deflection(flow, b, 2000.0)


def schwarzschild_deflection(b):
    """Exact deflection of light by a mass M = 1 for impact parameter b (Schwarzschild), by quadrature."""
    # u = 1/r; the orbit equation is (du/dphi)^2 = g(u) = 1/b^2 - u^2 + 2 u^3, with turning point u0 (g(u0) = 0).
    g = lambda u: 1.0 / b ** 2 - u ** 2 + 2.0 * u ** 3
    u0 = brentq(g, 0.9 / b, 1.5 / b, xtol=1e-15, rtol=1e-15)
    # factor out the root: g(u) = (u0 - u) q(u), q(u) = (1 - 2 u0)(u + u0) - 2 u^2; substitute u = u0 (1 - s^2)
    q = lambda u: (1.0 - 2.0 * u0) * (u + u0) - 2.0 * u ** 2
    val, _ = quad(lambda s: 4.0 * math.sqrt(u0) / math.sqrt(q(u0 * (1.0 - s * s))), 0.0, 1.0, epsabs=1e-12, epsrel=1e-12)
    return val - math.pi


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. Sound rays through three inward flows (c = 1, GM = 1, all flows 0.447 c at r = 10)")
    # ------------------------------------------------------------------------------------------------------
    bs = [20.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
    flows = [("river flow  v ~ r^-1/2 (escape speed)", river()), ("linear-in-source flow  v ~ 1/r", linear_response()),
             ("fluid-sink far field  v ~ r^-2", sink_far_field())]
    # convergence check on the starting distance
    a1 = deflection(flows[0][1], 100.0, 2000.0)
    a2 = deflection(flows[0][1], 100.0, 8000.0)
    a_ext = 2.0 * a2 - a1
    p(f"Convergence: river flow, b = 100: start at 2000 b -> {a1:.8f}, 8000 b -> {a2:.8f}; the error goes as X^-1/2 (v ~ r^-1/2")
    p(f"    stretches and tilts the wave vector all the way out), Richardson-extrapolated value {a_ext:.8f}, exact GR {schwarzschild_deflection(100.0):.8f}.")
    p("    The river flow below uses the extrapolated value; the faster-decaying flows are converged at 2000 b.")
    p(f"    {'b':>6s} {'GR exact':>10s} {'4GM/b':>9s} " + " ".join(f"{n[:22]:>24s}" for n, _ in flows))
    table = {}
    for b in bs:
        gr = schwarzschild_deflection(b)
        vals = [deflection_extrapolated(flows[0][1], b), deflection(flows[1][1], b), deflection(flows[2][1], b)]
        table[b] = (gr, vals)
        p(f"    {b:6.0f} {gr:10.6f} {4.0 / b:9.6f} " + " ".join(f"{v:12.6f} ({v / gr:7.4f})" for v in vals))
    p("    (in brackets: deflection divided by the exact general-relativistic value)")
    river_err = max(abs(table[b][1][0] / table[b][0] - 1) for b in bs)
    p(f"    => the river flow reproduces exact Schwarzschild light bending to {river_err:.1e} at every b.")
    lin_ratios = [table[b][1][1] / table[b][0] for b in bs]
    sink_ratios = [table[b][1][2] / table[b][0] for b in bs]
    p(f"    => the linear-in-source flow gives {lin_ratios[0]:.3f} of it at b = 20 and {lin_ratios[-1]:.4f} at b = 1000 (the ratio falls as 1/b:")
    p(f"       bending ~ v(b)^2 ~ b^-2); the fluid-sink flow gives {sink_ratios[0]:.3f} and {sink_ratios[-1]:.1e} (ratio ~ b^-3: bending ~ b^-4).")

    # ------------------------------------------------------------------------------------------------------
    p("\nB. How does the deflection depend on the flow speed?  River flow scaled by eps, b = 100")
    b0 = 100.0
    gr0 = schwarzschild_deflection(b0)
    eps_list = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
    eps_defl = []
    for eps in eps_list:
        a = deflection_extrapolated(river(eps), b0)
        eps_defl.append(a)
        p(f"    eps = {eps:4.2f}: deflection = {a:.6f} = {a / gr0:.4f} of GR   (eps^2 = {eps ** 2:.4f})")
    slope = np.polyfit(np.log(eps_list[:4]), np.log(eps_defl[:4]), 1)[0]
    p(f"    => log-log slope at small eps = {slope:.2f}: the bending goes as the SQUARE of the flow speed.")
    p("       First-order (linear in v) terms cancel for a symmetric inflow; the bending comes from v^2, the 'potential' part")
    p("       of the acoustic metric.  A flow produced linearly by the source, v ~ G M, would bend by ~ (G M)^2: far too little.")
    p("       Only a flow with v^2 ~ G M / r, i.e. v ~ sqrt(G M) (non-analytic in the source strength), matches gravity.")

    # ------------------------------------------------------------------------------------------------------
    p("\nC. What would sustain the river flow in a conserved fluid?")
    p("   Continuity with uniform density rho and steady flow: div v = - s / rho, so the sink density needed is")
    p("       s(r) = rho (3/2) sqrt(2 G M) r^(-3/2)      (kg per second per cubic metre),")
    p("   and the total drain through a sphere of radius r is  Phi(r) = 4 pi rho sqrt(2 G M) r^(3/2).")
    p("   Phi GROWS with r: the sinks are spread through all space, not located in the body, and Phi is not proportional to M.")
    rho = mP() / lP() ** 3
    m_sun, r_sun, au = 1.98847e30, 6.957e8, 1.495978707e11
    phi_sun = 4.0 * math.pi * rho * math.sqrt(2.0 * G0 * m_sun) * r_sun ** 1.5
    phi_au = 4.0 * math.pi * rho * math.sqrt(2.0 * G0 * m_sun) * au ** 1.5
    p(f"   Sun, medium at Planck density {rho:.2e} kg/m^3: drain through the Sun's surface {phi_sun:.1e} kg/s, through 1 AU {phi_au:.1e} kg/s.")
    p("   Euler equation: for the river flow v . grad v = - G M / r^2, i.e. the fluid elements themselves accelerate inward at the")
    p("   Newtonian rate.  A steady irrotational flow of a uniform-density fluid has v . grad v = grad(v^2/2) balanced only by pressure")
    p("   gradients, which are zero for uniform density: the flow needs an external inward force equal to gravity to exist.")
    p("   A real fluid sink (continuity alone, no extra force) has v ~ r^-2 (scenario 3 above): it bends sound ~ b^-4, not b^-1.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F2a: an inward flow of the medium can bend light like gravity",
         f"YES for the river flow v = sqrt(2GM/r): matches exact Schwarzschild to {river_err:.0e}"),
        ("F2b: the flow can be a linear response to the mass",
         f"NO: bending goes as v^2 (slope {slope:.2f}); a flow v ~ GM/r gives {lin_ratios[-1]:.3f} of GR at b = 1000 and falling as 1/b"),
        ("F2c: a conserved fluid draining into a hyper-dimension makes that flow",
         f"NO: a real sink flow has v ~ r^-2 and bends {sink_ratios[-1]:.0e} of GR at b = 1000 (~b^-4); the river flow needs sinks "
         f"everywhere (Phi grows as r^1.5) and an inward force equal to gravity"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.8, 5.2))

    ax = axs[0]
    for idx, (name, col) in enumerate(((flows[0][0], S1), (flows[1][0], S2), (flows[2][0], S3))):
        ax.plot(bs, [table[b][1][idx] / table[b][0] for b in bs], "o-", color=col, ms=6, label=name)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.set(xscale="log", yscale="log", ylim=(1e-8, 4.0), xlabel="impact parameter b  (units of GM/c²)",
           ylabel="light bending ÷ general relativity", title="Which flow of the medium bends sound like gravity?")
    ax.text(21, 1.35, "general relativity", fontsize=9, color=INK_2)
    ax.legend(loc="lower left", fontsize=8.5)

    ax = axs[1]
    ax.plot(eps_list, [a / gr0 for a in eps_defl], "o", color=S1, ms=7, label="ray tracing")
    ee = np.geomspace(0.04, 1.2, 50)
    ax.plot(ee, ee ** 2, color=MUTED, ls="--", lw=1.2, label="ε²")
    ax.set(xscale="log", yscale="log", xlabel="flow speed ÷ escape speed (ε)", ylabel="light bending ÷ general relativity",
           title="Bending goes as the square of the flow speed (b = 100 GM/c²)")
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "flow_gravity")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
