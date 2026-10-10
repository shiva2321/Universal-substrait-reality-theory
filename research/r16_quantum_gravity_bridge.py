"""
r16 - Gravity and quantum mechanics: one thing at different scales?  (LAB_NOTEBOOK.md entry E21)

Question (user): "We also need to see if we can unify gravity and quantum mechanics as well, since
they are one and the same thing, just at a different magnitude scale."

  A. How big are the quantum effects of gravity, as a function of scale?  Gravity as an effective
     quantum field theory (Donoghue 1994; Bjerrum-Bohr, Donoghue & Holstein 2003) gives the
     quantum correction to Newton's law exactly.  Where does it become O(1)?
  B. Where quantum mechanics and gravity already meet in the lab (measured):
     COW neutron interferometry, quantum bouncing neutrons, Page-Geilker, Diosi-Penrose tests,
     analogue Hawking radiation.
  C. The decisive next experiment: gravity-mediated entanglement (Bose et al. 2017; Marletto &
     Vedral 2017).  A QUANTUM substrate (USRT v2, r06/r14) predicts entanglement; a classical
     'dent' substrate predicts none.
  D. What 'unification' means in the substrate picture: hbar, c and G from the same cells.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r16_quantum_gravity_bridge"
H_PLANCK = 2 * math.pi * hbar
M_N = 1.67492750056e-27          # neutron mass, kg (CODATA 2022)
G_EARTH = 9.80665
AIRY_ZEROS = (2.33810741, 4.08794944, 5.52055983, 6.78670809)


def quantum_correction(r):
    """Relative one-loop quantum correction to Newton's potential (BDH 2003): (41/10pi) (l_P/r)^2."""
    return 41 / (10 * math.pi) * (lP() / r) ** 2


def bmv_phase(m, d, dx, t):
    """Entangling phase for two masses, each split by dx, centres d apart, on one line."""
    inner, outer = d - dx, d + dx
    return G0 * m * m * t / hbar * (1 / inner + 1 / outer - 2 / d)


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. The size of quantum gravity, scale by scale")
    p("Newton's potential with its leading corrections (Bjerrum-Bohr, Donoghue & Holstein, PRD 67, 084033 (2003)):")
    p("  V(r) = -G m1 m2 / r [ 1 + 3 G (m1+m2)/(r c^2)  +  (41/10pi) G hbar/(r^2 c^3) ]")
    p("                              classical GR             QUANTUM (graviton loops)")
    for label, r in (("between two people, 1 m", 1.0), ("torsion-balance test, 52 um", 52e-6),
                     ("bouncing neutrons, 10 um", 1e-5), ("an atom, 0.1 nm", 1e-10),
                     ("a proton, 1 fm", 1e-15), ("LHC collision, 1e-19 m", 1e-19),
                     ("Planck length", lP())):
        p(f"   {label:30s} quantum correction {quantum_correction(r):9.1e}")
    p("=> the user's intuition, made quantitative: gravity and quantum mechanics are ALREADY one")
    p("   consistent theory at every scale ever probed (gravity as an effective quantum field theory).")
    p("   The quantum part grows as (l_P / r)^2 and is O(1) only near the Planck length: the two look")
    p("   different only because of the scale. What is missing is the theory AT that scale -- in USRT")
    p("   terms, the substrate's cells (0.3 sqrt(N) l_P from r13/r14).")

    p.section("B. Where quantum mechanics and gravity already meet in measurements")
    lam, area = 1.445e-10, 10.0e-4
    q = 2 * math.pi * lam * G_EARTH * M_N ** 2 * area / H_PLANCK ** 2
    p(f"1. COW (Colella, Overhauser & Werner, PRL 34, 1472 (1975)): a neutron's quantum phase shifts in")
    p(f"   Earth's gravity: phi = 2 pi lambda g m^2 A / h^2 = {q:.0f} rad for lambda = 1.445 A, A = 10 cm^2.")
    p("   Observed; precision versions agree to ~1% (with a debated ~1% residual: Littrell, Allman &")
    p("   Werner, PRA 56, 1767 (1997)). Note m^2: gravity enters the Schroedinger phase, not just m.")
    eps = (hbar ** 2 * M_N * G_EARTH ** 2 / 2) ** (1 / 3)
    z0 = eps / (M_N * G_EARTH)
    p("2. Neutrons bouncing on a mirror have QUANTISED heights (Nesvizhevsky et al., Nature 415, 297 (2002)):")
    for n, a in enumerate(AIRY_ZEROS, 1):
        p(f"   state {n}: E = {a * eps / eV * 1e12:.3f} peV, classical turning height {a * z0 * 1e6:.1f} um")
    f13 = (AIRY_ZEROS[2] - AIRY_ZEROS[0]) * eps / H_PLANCK
    p(f"   transition 1 -> 3: {f13:.1f} Hz; driven and resolved by qBounce resonance spectroscopy")
    p("   (Jenke et al., Nature Phys. 7, 468 (2011); Cronenberg et al., Nature Phys. 14, 1022 (2018)).")
    p("3. Page & Geilker, PRL 47, 979 (1981): a Cavendish balance whose masses were placed by a quantum")
    p("   random event. The pull followed the ACTUAL outcome, not the quantum average -> rules out")
    p("   'semiclassical gravity sourced by expectation values' without wavefunction collapse.")
    p("4. Diosi-Penrose gravity-induced collapse (tau = hbar / E_G): the parameter-free version is ruled out")
    p("   by the absence of the predicted spontaneous radiation (Donadi et al., Nature Phys. 17, 74 (2021)).")
    p("5. Hawking radiation from a horizon IN A MEDIUM: sonic horizons in Bose-Einstein condensates emit")
    p("   a thermal, entangled phonon spectrum (Steinhauer, Nature Phys. 12, 959 (2016); Munoz de Nova")
    p("   et al., Nature 569, 688 (2019)). The closest lab realisation of 'spacetime = medium' physics.")

    p.section("C. The decisive experiment: can gravity entangle two masses?")
    p("Two masses, each in a superposition of two places dx apart, centres d apart, for time t. Gravity")
    p("gives each branch a phase G m^2 t/(hbar r). If gravity is a QUANTUM field (any quantum substrate),")
    p("the four phases differ and the masses become entangled. A CLASSICAL field cannot entangle them")
    p("(local operations + classical communication cannot create entanglement).")
    d, dx, t = 450e-6, 250e-6, 2.5
    for m in (3e-15, 1e-14, 3e-14):
        ph = bmv_phase(m, d, dx, t)
        p(f"   m = {m:.0e} kg, d = 450 um, dx = 250 um, t = 2.5 s: entangling phase {ph:.3f} rad,"
          f" concurrence |sin(phase/2)| = {abs(math.sin(ph / 2)):.3f}")
    p("   (geometry of Bose et al., PRL 119, 240401 (2017); see also Marletto & Vedral, PRL 119, 240402.)")
    p(f"   the phase grows as m^2 t: maximal entanglement (phase = pi) for m = 1e-14 kg after"
      f" {math.pi / bmv_phase(1e-14, d, dx, 1.0):.0f} s, for 3e-14 kg after {math.pi / bmv_phase(3e-14, d, dx, 1.0):.1f} s")
    p("   Hard parts: keeping 1e-14 kg crystals coherent for seconds; screening Casimir forces.")
    p("PREDICTIONS:")
    p("   USRT v2 (quantum network substrate, G from its entanglement, r06/r14): ENTANGLEMENT appears.")
    p("   Original USRT (classical superfluid continuum) or any classical 'dent': NO entanglement.")
    p("   Classical-gravity alternatives must instead show intrinsic spacetime diffusion (Oppenheim et al.,")
    p("   Nature Commun. 14, 7910 (2023)), testable with precision mass measurements.")
    p("   (What a positive result proves exactly is debated: e.g. Martin-Martinez & Perche, PRD 108,")
    p("   L101702 (2023). It would still rule out every classical-substrate version.)")

    p.section("D. What 'unifying' gravity and quantum mechanics means in the substrate picture")
    for line in (
        "* hbar: the quantum of action of the substrate's cells (r06: a quantum network).",
        "* c:    the cells' maximum signal speed (Lieb-Robinson, r05); light and gravity share it only if",
        "        Lorentz symmetry is protected (r12, r13).",
        "* G:    NOT a separate constant: it is the stiffness / entanglement of the same quantum cells,",
        "        G ~ a^2 c^3 / (4 N eta hbar) with eta = 0.024 per cell face (r13, r14).",
        "* Planck length = ~3 x (cell size)/sqrt(N): the scale where the cells show and the two",
        "  descriptions merge (A). Quantum mechanics is the substrate's short-distance dynamics; gravity",
        "  is its long-distance elasticity/thermodynamics -- the same object at different magnifications.",
        "* Status: a CONSISTENT picture (each step is established physics: Sakharov, Bekenstein-Hawking,",
        "  Jacobson, effective field theory), not yet a derived one: the graviton's protection (local",
        "  Hamiltonian constraint) and exact Lorentz invariance at the cell scale remain the open problem.",
    ):
        p(line)

    # ---------- figure
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    r = np.logspace(-36, 1, 400)
    qc = 41 / (10 * math.pi) * (lP() / r) ** 2
    axs[0].loglog(r, qc, color=S1, lw=2, label="quantum correction to Newton (41/10π)(l_P/r)²")
    cl = 3 * G0 * 2 * 1.0 / (r * c ** 2)
    axs[0].loglog(r, cl, color=S2, lw=1.6, ls="--", label="classical GR correction, two 1 kg masses")
    axs[0].axhline(1, color=MUTED, lw=0.9, ls=":")
    axs[0].axvspan(1e-36, 3 * lP(), color="#ebeae6", lw=0)
    axs[0].text(2e-36, 1e-60, "substrate\ncells\n(r13, r14)", fontsize=8.5, color=INK_2)
    probes = [("torsion balance", 52e-6), ("atom", 1e-10), ("LHC", 1e-19)]
    for nm, rr in probes:
        axs[0].plot(rr, quantum_correction(rr), "o", color=S1, ms=6)
        axs[0].text(rr * 1.8, quantum_correction(rr) * 3, nm, fontsize=8.5, color=INK_2)
    axs[0].set(xlim=(1e-36, 10), ylim=(1e-75, 1e4), xlabel="distance r (m)", ylabel="relative size of the correction",
               title="Quantum gravity effects grow as (l_P/r)²:\nnegligible everywhere we look, O(1) at the cell scale")
    axs[0].legend(loc="lower center", fontsize=8.5)
    tt = np.linspace(0, 5, 200)
    for m, col in ((3e-15, MUTED), (1e-14, S1), (3e-14, S3)):
        ph = bmv_phase(m, d, dx, tt)
        axs[1].plot(tt, np.abs(np.sin(ph / 2)), color=col, lw=2, label=f"m = {m:.0e} kg")
    axs[1].axhline(0, color=S2, lw=2, ls="--", label="any classical substrate: exactly 0")
    axs[1].set(xlabel="interaction time (s)", ylabel="entanglement (concurrence)", ylim=(-0.05, 1.42),
               yticks=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
               title="Gravity-mediated entanglement (Bose et al. geometry):\nquantum substrate vs classical substrate")
    axs[1].legend(loc="upper center", ncol=2, fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "scales_and_test")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
