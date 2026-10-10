"""
r03 - The inverse problem: what must the vacuum "medium" be like, given the waves we see?
(2026-10-10, LAB_NOTEBOOK.md entry E6)

Seismologists infer the Earth's interior from how its waves travel (speeds, which
polarisations exist, damping).  Here the same reasoning is applied to the vacuum,
using two kinds of waves we measure precisely: light and gravitational waves.

  1. Light: speed, impedance, polarisations  -> stiffness/inertia of the medium,
     and what kind of stiffness (twist-only = MacCullagh 1839 / gauge field).
  2. Gravitational waves: speed, polarisations, strain for a known energy flux ->
     the stiffness of spacetime; check against GW150914.
  3. Polarisation patterns: why light and gravity must be different kinds of wave
     (helicity 1 vs 2) and why a 'slowing medium' (scalar) predicts the wrong wave.
  4. Graininess, isotropy, loss, and equal speeds -> bounds on the medium.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import ALPHA, G0, INK_2, MUTED, S1, S2, S3, Report, c, e, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r03_medium_from_waves"
Mpc = 3.0857e22
E_P_GeV = math.sqrt(hbar * c ** 5 / G0) / (1e9 * eV)


def main():
    p = Report(NAME)
    style(plt)

    p.section("1. Light: what its speed, impedance and polarisations say about the medium")
    mu0 = 1.25663706127e-6          # CODATA 2022 (N/A^2)
    Z0 = mu0 * c
    p(f"measured wave speed c = {c:.0f} m/s, impedance Z0 = {Z0:.6f} ohm")
    p(f"for any wave: speed = sqrt(stiffness/inertia), impedance = sqrt(stiffness*inertia)")
    p(f"  -> 'inertia'  mu0     = Z0/c = {Z0 / c:.6e} H/m")
    p(f"  -> 'stiffness' 1/eps0 = Z0*c = {Z0 * c:.6e} m/F")
    p(f"In units that do not depend on how we define charge: Z0 = 4*pi*alpha*hbar/e^2 = "
      f"{4 * math.pi * ALPHA * hbar / e ** 2:.6f} ohm")
    p(f"  => the medium's dimensionless 'stiffness' for light is alpha = 1/{1 / ALPHA:.6f}.")
    p("     Explaining 1/137 from the substrate would be a real derivation (cf. emergent alpha ~ 0.08 in")
    p("     quantum spin ice, r02).")
    k = np.array([0.3, -0.5, 0.8])
    M = (k @ k) * np.eye(3) - np.outer(k, k)
    p(f"Only 2 polarisations, both transverse: a medium whose energy depends ONLY on twist (curl u) has")
    p(f"  wave matrix |k|^2 I - k k^T with eigenvalues {np.round(np.linalg.eigvalsh(M) / (k @ k), 6)} x |k|^2:")
    p("  two transverse waves and no longitudinal one. This is MacCullagh's 1839 'rotational aether', which")
    p("  is mathematically the modern gauge field. An ordinary solid (resisting stretch too) gives 3 waves.")

    p.section("2. Gravitational waves: the stiffness of spacetime")
    T = c ** 4 / (8 * math.pi * G0)
    p(f"stiffness (tension) of spacetime c^4/(8 pi G) = {T:.2e} N  (a force: c^4/G is a tension, not N/m)")
    L, d, f, h_meas = 3.6e49, 410 * Mpc, 250.0, 1.0e-21
    F = L / (4 * math.pi * d ** 2)
    h = math.sqrt(16 * math.pi * G0 * F / (c ** 3 * (2 * math.pi * f) ** 2))
    p(f"GW150914: peak luminosity {L:.1e} W at {d / Mpc:.0f} Mpc -> flux at Earth {F * 1e3:.1f} mW/m^2")
    p(f"  predicted strain from that stiffness: h = sqrt(16 pi G F / (c^3 w^2)) = {h:.1e}; LIGO measured ~{h_meas:.0e}")
    p("  A flux several times brighter than full moonlight stretches space by only 1e-21: spacetime is extremely stiff.")

    p.section("3. Polarisation patterns: light, gravity and a 'slowing medium' are different kinds of wave")
    ang = np.linspace(0, 2 * np.pi, 361)
    vec = np.cos(ang)              # overlap of a rotated linear polarisation (helicity 1)
    ten = np.cos(2 * ang)          # overlap of a rotated plus-polarisation h_+ (helicity 2)
    sca = np.ones_like(ang)        # breathing mode of a scalar ('slowing') medium (helicity 0)
    deg = np.degrees(ang)
    for name, y in (("light (vector)", vec), ("gravity (tensor)", ten), ("scalar breathing", sca)):
        if np.allclose(y, 1.0):
            p(f"{name:17s}: pattern is unchanged by ANY rotation (helicity 0)")
            continue
        back = np.where(np.abs(y[1:] - 1.0) < 1e-9)[0]
        p(f"{name:17s}: pattern repeats after rotation by {deg[1:][back[0]]:.0f} degrees")
    p("LIGO/Virgo (GW170814, three detectors) strongly favoured pure tensor over pure scalar or vector")
    p("polarisations. A medium that only 'slows light' (Dicke 1957, Puthoff's polarizable vacuum) carries")
    p("helicity-0 waves, so it cannot be the whole story: the medium needs a tensor (spin-2) stiffness.")

    p.section("4. Other properties fixed by observation")
    p(f"same speed for light and gravity: -3e-15 < (v_gw - c)/c < +7e-16 (GW170817 + GRB 170817A)")
    p(f"isotropy of light speed: < ~1e-17 to 1e-18 (rotating optical resonators)")
    p(f"no birefringence in vacuum: ~1e-32 or tighter (polarisation of distant gamma-ray bursts / CMB)")
    for n, Eqg in ((1, 1.2 * E_P_GeV), (2, 1e11)):
        a = hbar * c / (Eqg * 1e9 * eV)
        p(f"energy-dependent speed of order {n}: E_QG,{n} > {Eqg:.1e} GeV -> grain size a < ~{a:.1e} m"
          f" ({a / lP():.1e} Planck lengths)")
    p("  (n = 1 from Fermi-LAT GRB 090510; n = 2 bound order-of-magnitude from several GRB analyses.")
    p("   Lattices and superfluids are symmetric under k -> -k, so their leading correction is n = 2.)")
    p("lossless: light from galaxies ~13 billion years away arrives with sharp spectral lines; the medium")
    p("  has no measurable friction or absorption over ~1e26 m.")
    p("no detectable rest frame: Michelson-Morley-type experiments are null to the precision above.")

    p.section("Inferred profile of any vacuum medium")
    for line in (
        "* frictionless and lossless (superfluid-like),",
        "* no detectable rest frame: every probe made of the medium must share its single light cone,",
        "* twist-only ('gauge') stiffness for light, dimensionless strength alpha = 1/137.036,",
        "* a separate tensor (spin-2) stiffness for gravity, c^4/(8 pi G) = 4.8e42 N,",
        "* both waves travel at the same speed to 1 part in 1e15,",
        "* grains (if any) smaller than ~1e-35 m (order-1) or ~1e-27 m (order-2 dispersion),",
        "* isotropic: if it is a lattice, its symmetry must protect isotropy (cubic, for gauge light; r02).",
    ):
        p(line)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(deg, vec, color=S1, label="light (vector): repeats every 360°")
    ax.plot(deg, ten, color=S2, label="gravitational wave (tensor): every 180° (what LIGO/Virgo see)")
    ax.plot(deg, sca, color=S3, label="'slowing medium' wave (scalar): never changes")
    ax.set(xlim=(0, 360), ylim=(-1.15, 2.05), xticks=range(0, 361, 45),
           xlabel="rotation of the detector about the wave's direction (degrees)",
           ylabel="overlap with original pattern",
           title="Light and gravity are different kinds of wave; a scalar medium makes a third kind")
    ax.legend(loc="upper center", ncol=1, fontsize=9)
    ax.axhline(0, color=MUTED, lw=0.8)
    fig.tight_layout()
    save_fig(fig, NAME, "polarisation_patterns")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
