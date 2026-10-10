"""
Audit 04 - Mechanics, gravity and internal-consistency checks.

  1. Navier-Cauchy elasticity: is u_r = -r_g/r a solution, and can ANY displacement
     field produce the strain the documents need for g_ij = (1 + 2GM/(c^2 r)) delta_ij?
  2. Does a density 'cavity' in a Gross-Pitaevskii superfluid fall off like 1/r
     (Newtonian gravity) or exponentially (short-range force)?
  3. Units and mutually inconsistent substrate parameters across the documents.
  4. Smaller checks: MIT-bag numbers, the 'circulating light' electron, Kaluza-Klein
     masses, a static electric field in the E = -du/dt identification, de Boer values
     for real substances.
"""
import math
import os
import sys

import numpy as np
import sympy as sp
from scipy.integrate import solve_bvp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import G, banner, c, e, eV, hbar, m_e_kg, planck_length, planck_mass  # noqa: E402


def navier_cauchy(p):
    p(banner("1. Navier-Cauchy elasticity and the claimed 'rank-2 metric'"))
    r, rg, lam, mu, A, B = sp.symbols("r r_g lambda mu A B", positive=True)
    # radial displacement u(r) e_r: div u = (1/r^2) d(r^2 u)/dr, curl u = 0,
    # equilibrium (no body force): (lambda + 2 mu) d/dr(div u) = 0
    def residual(u):
        div = sp.diff(r**2 * u, r) / r**2
        return sp.simplify((lam + 2 * mu) * sp.diff(div, r))
    p(f"equilibrium residual for u = -r_g/r      : {residual(-rg / r)}   (must be 0; it is not)")
    p(f"equilibrium residual for u = A r + B/r^2 : {residual(A * r + B / r**2)}   (general radial solution)")
    eps_rr = sp.diff(B / r**2, r)
    eps_tt = (B / r**2) / r
    p(f"strain of u = B/r^2: eps_rr = {sp.simplify(eps_rr)}, eps_thth = eps_phph = {sp.simplify(eps_tt)}")
    p("  -> traceless and anisotropic (pure shear), falling like 1/r^3: not (GM/c^2 r) delta_ij.")
    # Saint-Venant compatibility for eps_ij = f(r) delta_ij
    x, y, z = sp.symbols("x y z", real=True)
    R = sp.sqrt(x**2 + y**2 + z**2)
    f = 1 / R
    X = (x, y, z)
    # contracted compatibility condition: f_,kl + delta_kl lap f = 0
    lap = sum(sp.diff(f, v, 2) for v in X)
    cond = sp.simplify(sp.diff(f, x, 2) + lap)
    p(f"compatibility of eps_ij = (1/r) delta_ij: f_xx + lap f = {cond}  (must vanish identically)")
    p("  -> it does not vanish, so NO displacement field u can produce the isotropic strain needed")
    p("     for g_ij = (1 + 2GM/(c^2 r)) delta_ij. The documents (and cauchy_tensor_gravity.py) simply")
    p("     write down the isotropic GR metric and ray-trace it; the 1.751 arcsec is GR's number.")


def solve_gp_cavity(V0=3.5, r0=1.2):
    """Radial GP ground state around a repulsive source (healing-length units)."""
    # dimensionless GP with a repulsive source: psi'' + 2psi'/r = (psi^2 - 1 + V(r)) psi
    def ode(rr, y):
        return np.vstack((y[1], -2 / rr * y[1] + (y[0] ** 2 - 1 + V0 * np.exp(-(rr / r0) ** 2)) * y[0]))

    def bc(ya, yb):
        return np.array([ya[1], yb[0] - 1.0])

    rr = np.linspace(1e-3, 40, 2000)
    guess = np.vstack((1 - 0.7 * np.exp(-(rr / 3) ** 2), np.zeros_like(rr)))
    return solve_bvp(ode, bc, rr, guess, max_nodes=100000, tol=1e-8)


def gp_cavity(p):
    p(banner("2. Range of the 'cavitation' attraction in a superfluid (Gross-Pitaevskii)"))
    sol = solve_gp_cavity()
    rs = np.linspace(5, 18, 200)
    drho = sol.sol(rs)[0] ** 2 - 1
    slope = np.polyfit(rs, np.log(-drho * rs), 1)[0]
    p(f"solver converged: {sol.success};  tail fit: |delta_rho| * r ~ exp({slope:.4f} r)")
    p(f"linearised theory predicts exp(-sqrt2 r) = exp({-math.sqrt(2):.4f} r) in healing-length units")
    p("=> The density dip around a 'cluster' is screened (Yukawa-like), with range ~ the healing length.")
    p("   If the healing length is ~ the Planck length, the force is gone beyond ~1e-35 m.")
    p("   Newton's 1/r needs a massless (gapless) mediator. In a superfluid the gapless mode is the")
    p("   phase/flow (sound) field, so a long-range force has to come from flow - e.g. sources/sinks or")
    p("   pulsating bodies (Bjerknes forces) - not from a static density dent. The repo's own")
    p("   cavity_simulation.py produces exactly this exponential tail. The ORIGINAL universe_simulation.py")
    p("   did not use the cavity at all - its orbit was driven by a typed-in force a = -0.85/(r^2 + 1.2);")
    p("   the audited version derives the force from the screened cavity and prints how it falls off.")


def units_and_consistency(p):
    p(banner("3. Units and the three incompatible parameter sets in the documents"))
    mP, _ = planck_mass()
    lP = planck_length()
    G0 = G[0]
    p(f"c^4/G = {c**4/G0:.4e}  -> units kg m s^-2 = NEWTON (a force), not N/m as the chat's")
    p("        'k_spring = c^4/G N/m = Einstein's coupling constant' claim states.")
    sets = {
        "Preprint sec.1 (V0 = M0c^2/7.2, FCC)": dict(rho=math.sqrt(2) * mP / lP**3,
                                                    k=72 * (mP * c**2 / 7.2) / lP**2,
                                                    mu_rule="k/(5 sqrt2 a)"),
        "Treatise sec.13 (V0 = E_P, mu = 3K/5)": dict(rho=math.sqrt(2) * mP / lP**3,
                                                      k=mP * c**2 / lP**2, mu_rule="3/5 rho c^2"),
        "ironclad script (rho = m/l^3, mu = k/l)": dict(rho=mP / lP**3, k=mP * c**2 / lP**2,
                                                        mu_rule="k/a"),
    }
    for name, d in sets.items():
        if d["mu_rule"] == "k/(5 sqrt2 a)":
            mu = d["k"] / (5 * math.sqrt(2) * lP)
        elif d["mu_rule"] == "3/5 rho c^2":
            mu = 0.6 * d["rho"] * c**2
        else:
            mu = d["k"] / lP
        ct = math.sqrt(mu / d["rho"])
        p(f"{name:42s} rho={d['rho']:.3e} kg/m^3  k={d['k']:.3e} N/m  mu={mu:.3e} Pa  sqrt(mu/rho)={ct/c:.4f} c")
    p("The treatise sec.13 states mu = (3/5)K with K = rho0 c^2 and then 'c = sqrt(mu/rho0)'; that")
    p("arithmetic gives 0.7746 c. The documents also use V0 = M0c^2/7.2 (sec.1) and V0 = E_P (sec.13),")
    p("and k = 7.49e79 N/m (sec.1) vs 7.49e78 N/m (sec.13). planckion_properties_and_physics.py hard-codes")
    p("Lambda* = 2.6833 ('lambda_de_boer_corrected = 2.6833'), although its own formula gives 1.0000.")


def small_checks(p):
    p(banner("4. Smaller checks"))
    # MIT bag as used in forces_and_mass.py / chat
    Rg = np.linspace(0.2, 2.0, 200001)
    E = 3 * 2.04 * 197.327 / Rg + 4 / 3 * math.pi * Rg**3 * 55.0
    i = np.argmin(E)
    p(f"MIT bag (3 quarks, x=2.04, B=55 MeV/fm^3): minimum at R = {Rg[i]:.3f} fm, M = {E[i]:.0f} MeV.")
    p("  The chat claimed R = 0.841 fm and then subtracted an unexplained 635 MeV to reach 938 MeV.")
    # circulating-light electron
    me = m_e_kg[0]
    rC = hbar / (me * c)
    L = rC * (me * c**2) / c
    p(f"Light-loop electron: r_C * (E/c) = {L/hbar:.3f} hbar (the chat inserted a factor 1/2 to get hbar/2);")
    p("  a circulating charge has gyromagnetic factor g = 1, but the electron has g = 2.00232, so a")
    p("  loop cannot give both spin hbar/2 and moment ~ mu_B. (Known objection to Zitterbewegung models.)")
    # Kaluza-Klein
    mP, _ = planck_mass()
    lP = planck_length()
    m1 = hbar / (lP * c)
    p(f"Kaluza-Klein: extra dimension of radius l_P gives first mode m = hbar/(R c) = {m1/mP:.3f} m_P"
      f" = {m1*c**2/eV/1e9:.3e} GeV, not an electron.")
    p("Static Coulomb field with E = -du/dt (MacCullagh identification): a constant E needs u growing")
    p("  linearly in time without bound - unbounded strain of the 'solid'. Charges are not described.")
    # de Boer parameters, paper convention (hbar, r_min = 2^(1/6) sigma, epsilon)
    kB = 1.380649e-23
    amu = 1.66053906660e-27
    subs = {"He-4": (10.22, 2.556, 4.0026, "liquid to T=0"), "H2": (37.0, 2.928, 2.016, "solid below 14 K"),
            "Ne": (35.6, 2.749, 20.18, "solid below 25 K"), "Ar": (119.8, 3.405, 39.95, "solid below 84 K")}
    p("de Boer parameter in the paper's convention Lambda* = hbar/(r_min sqrt(m eps)):")
    for nm, (epsK, sig, m, state) in subs.items():
        lam = hbar / (2 ** (1 / 6) * sig * 1e-10 * math.sqrt(m * amu * epsK * kB))
        p(f"  {nm:5s} Lambda* = {lam:.3f}  ({state})")
    p("  The documents quote 0.28 for He-4. In this convention He-4 is ~0.38 (0.43 using sigma instead of")
    p("  r_min), while H2 - which DOES freeze - is ~0.25-0.28. The threshold idea (~0.3) is roughly right;")
    p("  the problem is that the Planckion value is set by the fitted constant (Lambda* = sqrt(7.2)).")
    # black hole threshold (correct, standard)
    p("Black-hole threshold r_s = hbar/(Mc) -> M = m_P/sqrt2: correct, but standard GR+QM dimensional")
    p("  analysis; it does not involve the substrate.")


def main():
    out = []
    p = out.append
    navier_cauchy(p)
    gp_cavity(p)
    units_and_consistency(p)
    small_checks(p)
    text = "\n".join(out)
    print(text)
    with open(os.path.join(os.path.dirname(__file__), "results", "a04_mechanics_checks.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
