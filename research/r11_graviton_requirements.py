"""
r11 - What measurements demand of the substrate's gravity mode  (LAB_NOTEBOOK.md entry E16)

Question (user): "Long-range gravity needs a special protected mode in the substrate ... let's
research, brainstorm and give it a few out-of-the-box and field-established and measured ways
and see if we can solve it or not, based on our theory as well."

Before trying to BUILD a graviton from the substrate (r12-r15), pin down what any candidate must
do, using measured numbers only:
  A. Which spin?  One-particle exchange between two static masses, and between a mass and light,
     for spin 0, 1, 2 (massless and massive).  The ratio gives the PPN parameter gamma, which
     Cassini measured: gamma - 1 = (2.1 +- 2.3) x 10^-5.
  B. How massless?  Graviton mass bound from LIGO-Virgo-KAGRA (GWTC-3) vs the substrate's natural
     scale (the Planck energy).  How many orders of magnitude the 'protection' has to cover.
  C. Same speed as light?  GW170817 / GRB 170817A.
  D. Polarisations and universality: GW170814 polarisation test, MICROSCOPE equivalence principle.
  E. The theorems that frame the problem: Weinberg (1964), Deser (1970), Weinberg-Witten (1980).
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, mP, save_fig, style  # noqa: E402

NAME = "r11_graviton_requirements"
ETA = np.diag([1.0, -1.0, -1.0, -1.0])            # metric signature (+,-,-,-)

# measured inputs
GAMMA_CASSINI = (2.1e-5, 2.3e-5)                  # gamma - 1, Bertotti, Iess & Tortora, Nature 425, 374 (2003)
M_G_BOUND_EV = 1.27e-23                           # graviton mass, 90% UL, LVK GWTC-3 tests of GR (2021)
DV_GW170817 = (-3e-15, 7e-16)                     # (v_gw - c)/c, Abbott et al. ApJL 848, L13 (2017)
ETA_MICROSCOPE = (-1.5e-15, math.hypot(2.3e-15, 1.5e-15))  # Touboul et al. PRL 129, 121102 (2022)
H0_KM_S_MPC = 67.4                                # Planck 2018


def static_mass(m):
    T = np.zeros((4, 4))
    T[0, 0] = m
    return T


def light_ray(E):
    """Stress tensor of a light pulse moving along x (traceless)."""
    T = np.zeros((4, 4))
    T[0, 0] = T[1, 1] = E
    T[0, 1] = T[1, 0] = E
    return T


def lower(T):
    return ETA @ T @ ETA


def trace(T):
    return float(np.einsum("mn,mn->", ETA, T))


def exchange(T1, T2, kind):
    """Numerator of the one-particle-exchange amplitude in the static limit.
    Positive = attraction for spin 0 and 2 conventions used here (propagator i N / k^2)."""
    if kind == "spin-0 (scalar, couples to T)":
        return trace(T1) * trace(T2)
    if kind == "spin-1 (vector, couples to p^mu)":
        J1, J2 = T1[:, 0], T2[:, 0]                # energy-momentum density as the 'charge' current
        return -float(J1 @ ETA @ J2)               # propagator -eta: like charges REPEL (negative)
    if kind == "spin-2 massless (Fierz-Pauli, m=0)":
        return float(np.einsum("mn,mn->", lower(T1), T2)) - 0.5 * trace(T1) * trace(T2)
    if kind == "spin-2 massive (any m > 0)":
        return float(np.einsum("mn,mn->", lower(T1), T2)) - (1 / 3) * trace(T1) * trace(T2)
    raise ValueError(kind)


def sigma(gamma, meas=GAMMA_CASSINI):
    """Distance of a predicted gamma from Cassini's measured gamma - 1, in standard deviations."""
    return abs((gamma - 1) - meas[0]) / meas[1]


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Which spin? One-particle exchange: mass-mass vs mass-light")
    p("static sources: T^00 = m;  light pulse along x: T^00 = T^0x = T^xx = E (trace 0)")
    p("Newton's constant is fixed by the mass-mass amplitude; light bending is then set by the ratio")
    p("R = (light-mass amplitude)/(slow-particle-mass amplitude) at equal energy. PPN: 1 + gamma = R.")
    M, E = 1.0, 1.0
    kinds = ["spin-0 (scalar, couples to T)", "spin-1 (vector, couples to p^mu)",
             "spin-2 massive (any m > 0)", "spin-2 massless (Fierz-Pauli, m=0)"]
    gammas = {}
    for k in kinds:
        mm = exchange(static_mass(M), static_mass(M), k)
        lm = exchange(light_ray(E), static_mass(M), k)
        R = lm / mm
        g = R - 1
        gammas[k] = g
        sign = "attracts" if mm > 0 else "REPELS"
        p(f"  {k:36s} mass-mass {mm:+.3f} ({sign})  light-mass {lm:+.3f}  R = {R:.3f}  gamma = {g:+.3f}"
          + ("" if mm <= 0 else f"  -> {sigma(g):9.1e} sigma from Cassini"))
    p("  extra candidates from earlier entries:")
    extra = {"medium with eps changed only (r08)": 0.0, "medium with eps = mu (r08)": 1.0,
             "Brans-Dicke omega = 40,000 (spin 2 + scalar)": (1 + 4e4) / (2 + 4e4)}
    for k, g in extra.items():
        gammas[k] = g
        p(f"  {k:46s} gamma = {g:+.6f}  -> {sigma(g):8.1e} sigma")
    p(f"Cassini: gamma - 1 = ({GAMMA_CASSINI[0]:.1e} +- {GAMMA_CASSINI[1]:.1e}).")
    p("=> spin 1 is out (like 'charges' repel: apples would fall up). Spin 0 is out (no light bending).")
    p("   A massive spin 2 is out for ANY mass, however small (gamma = 1/2: the van Dam-Veltman-Zakharov")
    p("   discontinuity), unless non-linear Vainshtein screening hides the extra mode. Only a MASSLESS,")
    p("   pure helicity-+-2 mode gives gamma = 1. In r08's language: that is exactly the eps = mu medium.")

    p.section("B. How massless? The gap the substrate must protect")
    EP_eV = mP() * c ** 2 / eV
    lam_g = 2 * math.pi * hbar * c / (M_G_BOUND_EV * eV)
    H0 = H0_KM_S_MPC * 1e3 / 3.0857e22
    p(f"graviton mass bound (LVK GWTC-3, 90%): m_g c^2 < {M_G_BOUND_EV:.2e} eV -> Compton wavelength "
      f"> {lam_g:.2e} m ({lam_g / 3.0857e16:.1f} pc)")
    p(f"substrate's natural energy scale ~ Planck energy {EP_eV:.3e} eV")
    p(f"ratio m_g / m_P < {M_G_BOUND_EV / EP_eV:.1e}: the gap must be suppressed by {math.log10(EP_eV / M_G_BOUND_EV):.0f} orders"
      f" of magnitude ({2 * math.log10(EP_eV / M_G_BOUND_EV):.0f} in m^2, which is what a stiffness sets)")
    p(f"(for scale: hbar H0 = {hbar * H0 / eV:.2e} eV, the energy of a wave as long as the visible universe)")
    p("=> no accident or tuning can do this: the zero must be enforced by a SYMMETRY, as gauge")
    p("   invariance keeps the photon massless (r02, r09). For spin 2 the symmetry is (linearised)")
    p("   diffeomorphism invariance h -> h + d xi + d xi.")

    p.section("C. Same speed as light?")
    p(f"GW170817 + GRB 170817A (1.7 s apart after 130 million light years): {DV_GW170817[0]:.0e} <= (v_gw - c)/c <= {DV_GW170817[1]:.0e}")
    p("=> the gravity mode and the light mode must share ONE light cone to 1 part in 10^15.")
    p("   In a substrate, each mode's speed is sqrt(stiffness/inertia). Two unrelated modes would have")
    p("   to be tuned equal; two modes that are the same kind of excitation of the same cells are equal")
    p("   automatically. This is a strong hint that light and gravity must come from ONE structure.")

    p.section("D. Polarisations and universal coupling")
    p("GW170814 (3 detectors): pure tensor polarisation preferred over pure vector and pure scalar")
    p("  (Bayes factors ~200 and ~1000; Abbott et al., PRL 119, 141101 (2017)).")
    p(f"MICROSCOPE: Eotvos eta(Ti,Pt) = ({ETA_MICROSCOPE[0]:.1e} +- {ETA_MICROSCOPE[1]:.1e}): everything falls alike to ~10^-15.")
    p("Weinberg (1964): a massless spin-2 field MUST couple equally to all energy (soft-graviton")
    p("  theorem). So getting a massless spin-2 mode would give the equivalence principle for free.")
    p("Deser (1970) (after Gupta 1954, Kraichnan 1955, Feynman 1962): a massless spin-2 field coupled")
    p("  to all energy, including its own, is forced to become full non-linear General Relativity.")
    p("=> the whole problem reduces to ONE thing: a gapless helicity-+-2 mode of the substrate that")
    p("   couples to T^{mu nu}. The rest (Newton, bending, black holes, waves) follows.")

    p.section("E. The obstacle and its loopholes")
    p("Weinberg-Witten (1980): a theory with a Lorentz-covariant, conserved T^{mu nu} cannot contain a")
    p("  massless particle of helicity |h| > 1 that carries energy-momentum. So the graviton cannot")
    p("  be an ordinary bound state (e.g. two photons) living in a pre-existing flat spacetime.")
    p("Loopholes, each tried in the next scripts:")
    p("  1. gauge route (r12): the graviton is a gauge mode; its own T is not gauge-covariant (as in GR).")
    p("  2. induced route (r13): Sakharov 1967 - the substrate's quantum jiggling gives spacetime stiffness.")
    p("  3. entanglement route (r14): Jacobson 1995 - Einstein's equations from entanglement area law.")
    p("  4. defect route (r15): Kroener/Kleinert world crystal - curvature = density of disclinations.")
    p("  5. Lorentz symmetry only emergent (lattice), or an extra dimension (holography) - both evade the")
    p("     theorem's assumptions.")

    p.section("Requirement sheet for the substrate's gravity mode (all from measurement)")
    rows = [
        ("helicity", "+-2 only (tensor)", "GW170814 polarisations; gamma = 1"),
        ("gap", f"< {M_G_BOUND_EV:.1e} eV  (10^-51 of Planck)", "GWTC-3"),
        ("speed", "= c to 10^-15", "GW170817"),
        ("coupling", "to all energy equally, to 10^-15", "MICROSCOPE; Weinberg 1964"),
        ("gamma (eps = mu)", "1 to 2 x 10^-5", "Cassini"),
    ]
    for a, b, cc in rows:
        p(f"  {a:18s} {b:40s} [{cc}]")

    # ---------- figure
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.05, 1]})
    names = ["scalar (spin 0)", "medium, eps only (r08)", "massive spin 2", "massless spin 2\n= medium, eps = mu"]
    vals = [(1 + gammas[kinds[0]]) / 2, (1 + extra["medium with eps changed only (r08)"]) / 2,
            (1 + gammas[kinds[2]]) / 2, (1 + gammas[kinds[3]]) / 2]
    cols = [MUTED, MUTED, MUTED, S1]
    y = np.arange(len(names))
    axs[0].barh(y, vals, color=cols, height=0.55)
    for yi, v in zip(y, vals):
        axs[0].text(v + 0.02, yi, f"{v:.2f}", va="center", color=INK_2, fontsize=9)
    axs[0].axvline(1.0, color=S2, lw=1.4, ls="--")
    axs[0].text(0.98, 3.45, "measured (Cassini):\n1.00001 ± 0.00001", color=S2, fontsize=8.5, ha="right", va="bottom")
    axs[0].set(yticks=y, yticklabels=names, xlim=(0, 1.25), ylim=(-0.6, 4.2),
               xlabel="light bending by the Sun, relative to General Relativity",
               title="Only a massless spin-2 mode bends light correctly")
    axs[0].grid(axis="y", visible=False)

    ladder = [("Planck energy", EP_eV), ("Higgs field (246 GeV)", 246e9), ("proton", 938.27e6),
              ("electron", 0.511e6), ("CMB photon today", 6.3e-4), ("graviton: upper bound", M_G_BOUND_EV),
              ("ħ × Hubble rate", hbar * H0 / eV)]
    yl = np.arange(len(ladder))[::-1]
    for yi, (nm, val) in zip(yl, ladder):
        col = S2 if nm.startswith("graviton") else (S1 if nm == "Planck energy" else MUTED)
        axs[1].plot([1e-35, val], [yi, yi], color=col, lw=3, solid_capstyle="butt")
        axs[1].plot(val, yi, "o", color=col, ms=6)
        axs[1].text(val * 300, yi, f"{nm}", va="center", fontsize=8.5, color=INK_2)
    axs[1].set_xscale("log")
    axs[1].set(xlim=(1e-35, 1e40), yticks=[], xlabel="energy (eV)",
               title="The graviton's gap must sit 51 orders below the Planck scale")
    axs[1].grid(axis="y", visible=False)
    fig.tight_layout()
    save_fig(fig, NAME, "requirements")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
