"""
r05 - Brainstorm: can the substrate fix the speed of light?  (2026-10-10, LAB_NOTEBOOK.md entry E8)

  1. Where a speed limit comes from in ANY lattice of locally coupled quantum units:
     the Lieb-Robinson bound.  Simulated: a particle hopping on a chain spreads with a
     sharp front at speed 2 J a / hbar (J = coupling energy, a = spacing).
  2. The free knob, made explicit: three natural substrate rules (speed limit,
     'maximally quantum grain', gravity from grain stiffness) are satisfied for ANY
     value of c once hbar and G are given.  So the number needs one more measured
     substrate property (or it is just our choice of metre and second).
  3. What a substrate theory CAN aim to derive: dimensionless numbers and universality.
  4. Candidate routes, each with what it would need and what it would predict.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.linalg import expm  # noqa: E402
from scipy.special import jv  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import ALPHA, G0, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, mP, save_fig, style  # noqa: E402

NAME = "r05_speed_of_light"


def main():
    p = Report(NAME)
    style(plt)

    p.section("1. A speed limit emerges from local coupling (Lieb-Robinson), simulated")
    N, J = 301, 1.0
    H = -J * (np.eye(N, k=1) + np.eye(N, k=-1))
    psi0 = np.zeros(N, complex)
    psi0[N // 2] = 1.0
    ts = np.linspace(0, 60, 121)
    n = np.arange(N) - N // 2
    prob = np.array([np.abs(expm(-1j * H * t) @ psi0) ** 2 for t in ts])
    exact = np.array([jv(n, 2 * J * t) ** 2 for t in ts])
    p(f"numerical vs exact Bessel solution |J_n(2Jt)|^2: max difference {np.abs(prob - exact).max():.1e}")
    front, peak = [], []
    for row in prob:
        inside = np.where(row > 1e-6)[0]
        front.append(n[inside].max())
        right = row.copy()
        right[n < 0] = 0
        peak.append(n[np.argmax(right)])          # leading (outermost, largest) peak on the right
    late = ts >= 30
    slope = np.polyfit(ts[late], np.array(front)[late], 1)[0]
    slope_pk = np.polyfit(ts[late], np.array(peak)[late], 1)[0]
    p(f"late-time speeds: threshold front {slope:.3f}, leading peak {slope_pk:.3f} sites per unit time;"
      f" Lieb-Robinson 2Ja/hbar = {2 * J:.3f}")
    p("  (the edge has an Airy-type precursor whose width grows ~ t^(1/3): a threshold front runs slightly")
    p("   fast, the peak slightly slow; both converge to 2Ja/hbar as t grows)")
    i40 = np.argmin(abs(ts - 40))
    outside = prob[i40][np.abs(n) > 2 * J * 40 * 1.2].sum()
    p(f"probability found more than 20% beyond the front at t = 40: {outside:.1e} (exponentially small)")
    p("=> any lattice of locally coupled units has a maximum signal speed  c = 2 J a / hbar  (up to geometry")
    p("   factors). For grains one Planck length apart, reproducing c needs a coupling")
    Jp = hbar * c / (2 * lP())
    p(f"   J = hbar c / (2 l_P) = {Jp:.2e} J = {Jp / (1e9 * eV):.2e} GeV  (half the Planck energy)")

    p.section("2. The free knob: three natural substrate rules hold for ANY value of c")
    p("rules:  (i) c = 2 J a / hbar   (ii) hbar = M a c  (grain's quantum size = spacing)   (iii) G = c^2 a / M")
    p(f"{'chosen c (m/s)':>16} {'spacing a (m)':>14} {'grain mass M (kg)':>18} {'coupling J (J)':>15}  residuals (i),(ii),(iii)")
    for cc in (1.0, 299792458.0, 1e12):
        a = math.sqrt(hbar * G0 / cc ** 3)
        M = math.sqrt(hbar * cc / G0)
        Jc = hbar * cc / (2 * a)
        r1 = 2 * Jc * a / hbar / cc - 1
        r2 = M * a * cc / hbar - 1
        r3 = cc ** 2 * a / M / G0 - 1
        p(f"{cc:16.4g} {a:14.3e} {M:18.3e} {Jc:15.3e}  {r1:+.0e}, {r2:+.0e}, {r3:+.0e}")
    p("=> with only hbar and G as inputs, every value of c is equally consistent. To 'derive' 299,792,458 m/s")
    p("   the theory needs ONE independently measured substrate property (spacing, coupling or grain mass),")
    p("   e.g. from the energy at which light starts to disperse (r03: not seen up to ~1.5e19 GeV).")
    p("   And since 1983 the metre is DEFINED from c, so the number is partly our unit choice.")

    p.section("3. What a substrate theory can aim to derive instead: pure numbers")
    mp = 1.67262192595e-27
    alphaG = G0 * mp ** 2 / (hbar * c)
    rows = (
        ("alpha (vacuum's stiffness for light, r03)", f"1/{1 / ALPHA:.6f}", "computable in emergent-photon models (spin ice ~0.08)"),
        ("alpha_G = G m_p^2/(hbar c) (gravity vs proton)", f"{alphaG:.2e}", "why gravity is so weak: the hierarchy problem"),
        ("v_gravity / v_light", "1 +- 1e-15", "natural only if both ride on ONE emergent light cone"),
        ("v_light by direction", "isotropic to 1e-17", "needs symmetry protection (cubic, r02) or no lattice"),
        ("m_p / m_e", "1836.152673", "a target, but audit/a02 shows fitted formulas are cheap"),
    )
    for name, val, note in rows:
        p(f"  {name:48s} {val:>18}   {note}")

    p.section("4. Candidate routes (brainstorm) and their status")
    routes = (
        ("c = grain spacing / grain tick (a/tau)",
         "Exact restatement; explains why c is universal and a limit, not its value in m/s.", "sound"),
        ("c = Lieb-Robinson speed 2Ja/hbar of the substrate",
         "Mechanism for the speed LIMIT; needs J or a measured independently.", "sound, needs data"),
        ("One shared emergent light cone for all fields (Volovik Weyl points, r02)",
         "Explains universality; open problem: why species agree to 1e-15 (fine-tuning, Collins 2004).", "open"),
        ("Lorentz invariance as a low-energy attractor (Chadha & Nielsen 1983)",
         "Different speeds flow together at low energy, but only logarithmically: too slow alone.", "partial"),
        ("Supersymmetry protecting the shared cone (Groot Nibbelink & Pospelov 2005)",
         "Suppresses the dangerous low-energy Lorentz violation; SUSY not yet seen at LHC.", "speculative"),
        ("Induced gravity (Sakharov 1967): G from substrate fluctuations",
         f"Links grain size to the number N of particle fields: a ~ sqrt(N) l_P (N ~ 100 -> a ~ 10 l_P).", "testable in principle"),
        ("Measure the grain: energy-dependent light speed, birefringence",
         "Would supply the missing number; current bounds a < ~l_P (order-1) or ~1e-27 m (order-2).", "experimental"),
        ("Derive alpha = 1/137 from substrate couplings",
         "The real prize: a dimensionless prediction. Shown possible in principle (spin ice gives ~1/12).", "open"),
    )
    for title, body, status in routes:
        p(f"  [{status:>21}] {title}")
        p(f"  {'':>23} {body}")

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw={"width_ratios": [1.25, 1]})
    sel = np.abs(n) <= 150
    im = axs[0].imshow(np.log10(prob[:, sel] + 1e-16).T, origin="lower", aspect="auto", cmap="Blues",
                       extent=(ts[0], ts[-1], n[sel][0], n[sel][-1]), vmin=-12, vmax=0)
    axs[0].plot(ts, 2 * J * ts, color=S2, ls="--", lw=1.6, label="speed limit 2Ja/ħ")
    axs[0].plot(ts, -2 * J * ts, color=S2, ls="--", lw=1.6)
    axs[0].set(xlim=(0, 60), ylim=(-150, 150), xlabel="time (ħ/J)", ylabel="lattice site",
               title="A particle hopping on a lattice spreads inside a light cone")
    axs[0].legend(loc="upper left", fontsize=9)
    axs[0].grid(False)
    cb = fig.colorbar(im, ax=axs[0], pad=0.02)
    cb.set_label("log10 probability", color=INK_2)
    axs[1].plot(ts, front, color=S1, label=f"edge (probability > 1e-6): speed {slope:.2f}")
    axs[1].plot(ts, peak, color=S3, label=f"leading peak: speed {slope_pk:.2f}")
    axs[1].plot(ts, 2 * J * ts, color=S2, ls="--", label="Lieb-Robinson limit 2Ja/ħ = 2")
    axs[1].set(xlim=(0, 60), xlabel="time (ħ/J)", ylabel="position (sites)",
               title="Edge and peak both approach 2Ja/ħ: a built-in 'c'")
    axs[1].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "lieb_robinson")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
