"""
r10 - What could be MEASURED?  Concrete predictions of the revised substrate  (LAB_NOTEBOOK.md E14)

Question (user): "... see if our testing helps something emerge that is promising, measurable
and experimentable."

A. A cubic substrate's fingerprint on light.  For the twist-only (gauge) lattice of r02,
   omega^2 = sum_i 4 sin^2(k_i a/2)/a^2.  Extract the group-velocity deficit
   1 - v_g/c = C(n) (k a)^2 numerically, check C(n) = (1/8) sum n_i^4, and turn it into
   arrival delays for TeV gamma rays vs the cell size a.  Signature: quadratic in energy,
   high energies LATE, no polarisation dependence, and a fixed sky pattern (axis : diagonal = 3:1).
B. Strong gravity.  r08 found gravity = 'trapped energy lowers the substrate's wave speed', with
   eps = mu.  If that lowering COMPOUNDS multiplicatively (n = e^{2GM/rc^2}, the exponential
   metric of Yilmaz/Dicke), the weak-field tests are identical to GR (gamma = beta = 1, checked
   symbolically) but black holes differ: no horizon, larger shadow, different 2nd-order bending.
   Computed exactly and compared with Event Horizon Telescope numbers.
C. Scorecard of predictions: what is distinctive, what is shared with GR/Standard Model, and
   which experiment decides.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.optimize import brentq, minimize_scalar  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r10_testable_predictions"
Gpc = 3.0857e25


def omega(k):
    return np.sqrt(np.sum(4 * np.sin(k / 2) ** 2))


def deficit_coeff(n, ka=0.02):
    """1 - v_g along n, divided by (ka)^2, from the exact lattice dispersion."""
    n = np.asarray(n, float) / np.linalg.norm(n)
    dk = 1e-6
    vg = (omega((ka + dk) * n) - omega((ka - dk) * n)) / (2 * dk)
    return (1 - vg) / ka ** 2


def deflection(n_of_r, x):
    """Exact light deflection for refractive index n(r) (isotropic static metric), mass M = 1,
    closest approach r0 chosen so that impact parameter b = n(r0) r0 = 1/x."""
    b = 1.0 / x
    r0 = brentq(lambda r: n_of_r(r) * r - b, 0.5 * b, 2.0 * b, xtol=1e-14, rtol=1e-15)
    n0r0 = n_of_r(r0) * r0

    def f(s):                                  # u = 1 - s^2 removes the end-point singularity
        u = 1 - s * s
        if u <= 0:
            return 0.0
        q = (n_of_r(r0 / u) * r0 / u / n0r0) ** 2 - 1
        return 2 * s / (u * math.sqrt(q)) if q > 0 else 0.0
    val = quad(f, 0, 1, epsabs=1e-14, epsrel=1e-13, limit=400)[0]
    return 2 * val - math.pi


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. A cubic substrate's fingerprint on high-energy light")
    for name, n in (("lattice axis [100]", (1, 0, 0)), ("face diagonal [110]", (1, 1, 0)),
                    ("body diagonal [111]", (1, 1, 1)), ("random direction", (0.3, -0.5, 0.81))):
        nn = np.asarray(n, float) / np.linalg.norm(n)
        p(f"  {name:22s}: (1 - v_g/c)/(ka)^2 = {deficit_coeff(n):.5f}   predicted (1/8) sum n^4 = {np.sum(nn ** 4) / 8:.5f}")
    p("  => delay of the axis direction : body diagonal = 3 : 1 exactly; both polarisations identical")
    p("     (r02), and higher energies arrive later. The sky-average coefficient is 3/40.")
    E, D = 10e12 * eV, 1 * Gpc
    p(f"arrival delay of a {E / eV / 1e12:.0f} TeV photon after travelling {D / Gpc:.0f} Gpc (sky average, 3/40 coefficient):")
    sizes = (("Planck length", lP()), ("10 Planck lengths", 10 * lP()), ("1e-30 m", 1e-30),
             ("1e-28 m", 1e-28), ("2e-27 m (current bound)", 2e-27))
    delays = []
    for label, a in sizes:
        ka = E * a / (hbar * c)
        dt = D / c * 3 / 40 * ka ** 2
        delays.append((a, dt))
        p(f"  cell size {label:24s} a = {a:.1e} m: delay {dt:.1e} s")
    p("  Gamma-ray bursts and blazar flares resolve delays of ~1-10 s at these energies (LHAASO, CTA):")
    p("  visible only if cells are larger than ~1e-28 m, i.e. if the substrate is much coarser than Planck.")
    p("  Distinctive test, if a delay is ever seen: compare many sources across the sky; a cubic substrate")
    p("  predicts the specific 3:1 direction pattern (a fixed mix of isotropic + l = 4 harmonic).")

    p.section("B. Strong gravity: GR vs a multiplicative ('exponential') substrate response")
    r, M = sp.symbols("r M", positive=True)
    U = M / r
    for name, A, B in (("Schwarzschild (GR)", ((1 - U / 2) / (1 + U / 2)) ** 2, (1 + U / 2) ** 4),
                       ("exponential", sp.exp(-2 * U), sp.exp(2 * U))):
        a_ser = sp.series(A, M, 0, 3).removeO()
        b_ser = sp.series(B, M, 0, 2).removeO()
        beta = sp.simplify(a_ser.coeff(M, 2) * r ** 2 / 2)
        gamma = sp.simplify(b_ser.coeff(M, 1) * r / 2)
        p(f"  {name:20s} isotropic coords: PPN gamma = {gamma}, beta = {beta}  -> solar-system tests identical")
    bS = minimize_scalar(lambda x: x / math.sqrt(1 - 2 / x), bounds=(2.05, 10), method="bounded")
    bE = minimize_scalar(lambda x: x * math.exp(2 / x), bounds=(0.5, 10), method="bounded")
    dev = bE.fun / bS.fun - 1
    p(f"  photon-capture impact parameter (shadow radius), units GM/c^2: GR {bS.fun:.4f} (= 3 sqrt3), "
      f"exponential {bE.fun:.4f} (= 2e)")
    p(f"  => shadow {100 * dev:+.2f}% larger than GR for the same mass and distance")
    p("  Event Horizon Telescope, Sgr A* (2022): fractional deviation delta = -0.08 +- 0.09 (VLTI mass) and")
    p(f"  -0.04 +0.09/-0.10 (Keck mass): the exponential value {dev:+.3f} is {abs(dev + 0.08) / 0.09:.1f} and "
      f"{abs(dev + 0.04) / 0.09:.1f} sigma away")
    p("  -> allowed today; ngEHT / space VLBI aim for a few percent.")
    p("  Horizon: GR has one at r = 2GM/c^2; the exponential metric has none (g_tt = -e^{-2GM/rc^2} never")
    p("  vanishes) and a throat of areal radius e*GM/c^2 instead: a horizonless object, which predicts")
    p("  ringdown 'echoes'. LIGO-Virgo-KAGRA ringdowns agree with GR black holes so far; echoes are not")
    p("  robustly seen. This makes the multiplicative completion testable and under pressure.")
    nS = lambda rr: (1 + 1 / (2 * rr)) ** 3 / (1 - 1 / (2 * rr))   # noqa: E731
    nE = lambda rr: math.exp(2 / rr)                                  # noqa: E731
    xs = np.array([4e-4, 6e-4, 8e-4, 1.0e-3, 1.2e-3])
    c2 = {}
    for name, nf in (("GR", nS), ("exponential", nE)):
        th = np.array([deflection(nf, x) for x in xs])
        c2[name] = np.polyfit(xs, (th - 4 * xs) / xs ** 2, 1)[1]       # intercept of C2 + C3 x
        p(f"  light bending = 4 (GM/bc^2) + C2 (GM/bc^2)^2: C2({name}) = {c2[name]:.4f}")
    p(f"  analytic: GR 15 pi/4 = {15 * math.pi / 4:.4f}; exponential 4 pi = {4 * math.pi:.4f}")
    sun = 6.674e-11 * 1.98847e30 / c ** 2 / 6.957e8
    p(f"  at the Sun's edge the 2nd-order difference is {(c2['exponential'] - c2['GR']) * sun ** 2 * 206264.806e6:.2f}"
      " micro-arcseconds: below current reach (future sub-uas astrometry).")

    p.section("C. Scorecard: predictions of the revised substrate")
    rows = (
        ("Universal free fall for anything made of substrate waves (incl. antimatter, trapped light)",
         "shared with GR", "MICROSCOPE 1e-15 OK; ALPHA-g OK; next: 1e-17-1e-18 tests"),
        ("alpha does not change with gravitational potential (eps = mu)", "shared with GR",
         "atomic clocks: coupling < ~1e-6 OK"),
        ("Photons: 2 polarisations, no vacuum birefringence even at Planck energies", "shared with GR+SM",
         "GRB/CMB polarisation OK"),
        ("Quadratic, late, polarisation-blind, 3:1 direction-patterned delay of TeV photons",
         "DISTINCTIVE (cubic substrate)", "LHAASO/CTA: only if cells > ~1e-28 m"),
        ("Our alpha below the photon-phase threshold 0.079 (r06)", "consistency check", "satisfied (10.8x)"),
        ("Shadow +4.6%, no horizon, echoes, 2nd-order bending +pi/4 (if response compounds)",
         "DISTINCTIVE (strong field)", "EHT now +-9% (allowed); ngEHT; LVK ringdowns"),
        ("Particles appear only in pairs above 2Mc^2; mass = trapped energy", "shared with QFT",
         "Breit-Wheeler (STAR 2021), E = mc^2 to 4e-7 OK"),
    )
    for claim, kind, test in rows:
        p(f"  [{kind:28s}] {claim}")
        p(f"  {'':30s} test: {test}")

    # ---------- figures
    fig = plt.figure(figsize=(14, 4.6))
    ax0 = fig.add_subplot(1, 3, 1, projection="mollweide")
    lon = np.linspace(-np.pi, np.pi, 361)
    lat = np.linspace(-np.pi / 2, np.pi / 2, 181)
    LON, LAT = np.meshgrid(lon, lat)
    nx, ny, nz = np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)
    pat = (nx ** 4 + ny ** 4 + nz ** 4) / (3 / 5)
    im = ax0.pcolormesh(LON, LAT, pat, cmap="Blues", shading="auto", vmin=0.5, vmax=1.7)
    ax0.set_xticklabels([])
    ax0.set_yticklabels([])
    ax0.set_title("Delay pattern on the sky\n(relative to sky average; lattice axes at the darkest spots)", fontsize=10)
    cb = fig.colorbar(im, ax=ax0, orientation="horizontal", pad=0.06, fraction=0.05)
    cb.set_label("relative delay (axis 1.67, diagonal 0.56)", color=INK_2)
    ax1 = fig.add_subplot(1, 3, 2)
    aa = np.logspace(-35, -26, 200)
    ax1.loglog(aa, D / c * 3 / 40 * (E * aa / (hbar * c)) ** 2, color=S1, label="10 TeV photon, 1 Gpc")
    ax1.axhspan(1, 10, color=S3, alpha=0.18, lw=0)
    ax1.text(2e-35, 2.2, "measurable today (~1-10 s)", color=INK_2, fontsize=9)
    ax1.axvline(lP(), color=MUTED, ls="--", lw=1)
    ax1.text(lP() * 1.5, 1e-7, "Planck\nlength", color=INK_2, fontsize=9)
    ax1.set(xlabel="substrate cell size a (m)", ylabel="arrival delay (s)",
            title="Delay grows as (cell size)²")
    ax1.legend(loc="upper left", fontsize=9)
    ax2 = fig.add_subplot(1, 3, 3)
    ax2.errorbar([0], [-0.08], yerr=[0.09], fmt="o", color=S1, capsize=6, label="EHT Sgr A* (VLTI mass)")
    ax2.errorbar([1], [-0.04], yerr=[[0.10], [0.09]], fmt="o", color=S1, mfc="none", capsize=6,
                 label="EHT Sgr A* (Keck mass)")
    ax2.axhline(0, color=MUTED, ls="--", lw=1.2)
    ax2.axhline(dev, color=S2, lw=2)
    ax2.text(1.45, 0.003, "GR", color=INK_2, fontsize=9, ha="right", va="bottom")
    ax2.text(-0.45, dev + 0.004, f"exponential substrate +{100 * dev:.1f}%", color=S2, fontsize=9, ha="left", va="bottom")
    ax2.set(xlim=(-0.5, 1.5), ylim=(-0.22, 0.12), xticks=[], ylabel="shadow size deviation from GR",
            title="Black-hole shadow: allowed now, decidable soon")
    ax2.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "predictions")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
