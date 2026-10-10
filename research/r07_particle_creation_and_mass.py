"""
r07 - How a particle comes into existence and gets its mass  (LAB_NOTEBOOK.md entry E11)

Question (user): "How would a particle come into existence and get the mass ... I think the
energy trapped in a well would give some insights, because trapped energy at a point in space
is mass, since mass and energy are proportional."

A. Particle creation from concentrated energy (simulation).  A 1D substrate field with two
   equal ground states (phi^4: V = (phi^2 - 1)^2 / 2).  Its 'particles' are kinks: stable knots
   of trapped energy with rest energy M = 4/3 (exact).  We hit the calm substrate with a
   localized kick of energy E_in and count what is left after the radiation has escaped.
B. Why trapped energy IS mass: the box of light (inertia and weight both E/c^2).
C. Real-world evidence: deuteron mass defect (CODATA 2022), proton mass vs quark masses,
   precision E = mc^2 test.
D. Where big mass ratios can come from: dimensional transmutation (QCD), the honest version of
   the exponential mass formula the original USRT tried to fit.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, c, save_fig, style  # noqa: E402

NAME = "r07_particle_creation_and_mass"
M_KINK = 4.0 / 3.0                     # exact rest energy of a phi^4 kink in these units

H, LBOX, DT, EDGE = 0.05, 250.0, 0.02, 50.0
X = np.arange(-LBOX, LBOX, H)
DAMP = np.where(np.abs(X) > LBOX - EDGE, ((np.abs(X) - (LBOX - EDGE)) / EDGE) ** 2 * 2.0, 0.0)
CORE = np.abs(X) < LBOX - EDGE


def kick(P, w=4.0, T=160.0, record=False):
    """Kick the vacuum phi = 1 with velocity -P sech(x/w); absorbing edges remove radiation."""
    phi = np.ones_like(X)
    dphi = -P / np.cosh(X / w)

    def acc(p):
        lap = np.zeros_like(p)
        lap[1:-1] = (p[2:] - 2 * p[1:-1] + p[:-2]) / H ** 2
        return lap - 2 * p * (p * p - 1)
    a = acc(phi)
    snaps, frames = [], []
    nsteps = int(T / DT)
    for n in range(nsteps + 1):
        if n % int(20 / DT) == 0:
            s = np.sign(phi[CORE])
            idx = np.where(s[1:] != s[:-1])[0]
            snaps.append((n * DT, X[CORE][idx]))
        if record and n % int(1.0 / DT) == 0:
            frames.append(phi[::8].copy())
        dphi += 0.5 * DT * a
        phi += DT * dphi
        a = acc(phi)
        dphi += 0.5 * DT * a
        dphi *= (1 - DAMP * DT)
    return snaps, np.array(frames)


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Creating particles by concentrating energy in a calm substrate (phi^4 field)")
    p(f"particle (kink) rest energy M = 4/3 = {M_KINK:.4f}; a pair needs at least 2M = {2 * M_KINK:.3f}")
    w = 4.0
    rows = []
    for P in np.linspace(0.6, 2.0, 29):
        snaps, _ = kick(P, w)
        last, prev = snaps[-1][1], snaps[-3][1]
        sep_l = last.max() - last.min() if len(last) >= 2 else 0.0
        sep_p = prev.max() - prev.min() if len(prev) >= 2 else 0.0
        escaped = len(last) >= 2 and sep_l > sep_p + 5
        n = len(last) if escaped else 0
        v = (sep_l - sep_p) / 80.0 if escaped else 0.0          # outermost pair, each side
        g = 1 / math.sqrt(1 - min(v, 0.99) ** 2)
        E_in = P * P * w
        rows.append((E_in, n, v, g))
        frac = (2 * g * M_KINK) / E_in if escaped else 0.0
        p(f"E_in = {E_in:6.2f} ({E_in / (2 * M_KINK):4.2f} x 2M): particles created = {n}"
          + (f", outer pair speed {v:.2f}c, energy in that pair {100 * frac:3.0f}%" if escaped else ""))
    made = [r for r in rows if r[1] > 0]
    p(f"lowest energy that created a lasting pair: {made[0][0]:.2f} = {made[0][0] / (2 * M_KINK):.2f} x 2M "
      f"(never below 2M = {2 * M_KINK:.2f})")
    p(f"every outcome has an EVEN number of particles: {all(r[1] % 2 == 0 for r in rows)} "
      "(topological charge is conserved, so particles appear as particle + antiparticle)")
    ok = all(r[0] >= r[1] * M_KINK for r in rows)
    p(f"N particles never appear with less than N x M of energy: {ok}")
    p("Some energies make nothing: the substrate 'rings' and the bubble re-collapses (known resonance")
    p("windows of kink-antikink dynamics). The leftover energy always leaves as ordinary waves (radiation).")

    p.section("B. Why trapped energy IS mass: light in a box")
    p("A pulse of light (energy E) bouncing between two mirrors:")
    p("  * push the box: the forward-moving mirror reflects blue-shifted light, the back mirror red-shifted;")
    p("    the net momentum of the trapped light is P = gamma E v / c^2 -> inertial mass = E/c^2.")
    p("  * hang it in gravity g: light at the bottom has energy higher by a factor (1 + g L/c^2), so the")
    p("    bottom mirror is pushed harder: net weight = (E/c^2) g -> gravitational mass = E/c^2.")
    p(f"  1 joule of trapped light adds {1 / c ** 2:.2e} kg to the box, and weighs exactly that much.")

    p.section("C. Real-world evidence that mass is trapped energy")
    mp, mn, md = 938.27208943, 939.56542194, 1875.61294500     # CODATA 2022, MeV
    B = mp + mn - md
    p(f"deuteron: m_p + m_n - m_d = {B:.6f} MeV  (CODATA 2022 masses)")
    p("  = the energy released (2.2246 MeV gamma) when a neutron is captured by a proton: binding the two")
    p("  traps less energy, so the bound system weighs less, exactly by E/c^2.")
    p("  Direct test: Rainville et al., Nature 438, 1096 (2005) confirmed E = mc^2 to 4 parts in 10^7.")
    mu, md_q = 2.16, 4.70                                        # PDG 2024 MS-bar at 2 GeV, MeV
    p(f"proton: quark rest masses 2 m_u + m_d = {2 * mu + md_q:.1f} MeV vs proton {mp:.1f} MeV ->"
      f" {100 * (1 - (2 * mu + md_q) / mp):.0f}% of the proton's mass is trapped field energy")
    p("  (lattice QCD reproduces hadron masses from this trapped energy: Durr et al., Science 322, 1224 (2008)).")
    p("So ordinary matter is overwhelmingly trapped energy: this part of the user's intuition is exactly")
    p("how nature works.")

    p.section("D. Where large mass ratios come from: dimensional transmutation")
    aS, dS, MZ = 0.1180, 0.0009, 91.1876          # PDG 2024 alpha_s(M_Z), Z mass (GeV)
    b0 = 11 - 2 * 5 / 3
    lam = MZ * math.exp(-2 * math.pi / (b0 * aS))
    lam_hi = MZ * math.exp(-2 * math.pi / (b0 * (aS + dS)))
    lam_lo = MZ * math.exp(-2 * math.pi / (b0 * (aS - dS)))
    p(f"one-loop QCD scale: Lambda = M_Z exp(-2 pi / (b0 alpha_s)), b0 = 23/3, alpha_s(M_Z) = {aS} +- {dS}")
    p(f"  -> Lambda = {1000 * lam:.0f} MeV  (range {1000 * lam_lo:.0f}-{1000 * lam_hi:.0f} MeV); two-loop MS-bar value ~210 MeV")
    p(f"  an O(0.1) coupling gives a scale {MZ / lam:.0f}x below M_Z through an EXPONENTIAL; the proton mass")
    p("  (~4-5 x the two-loop Lambda) is set this way. The original USRT electron formula m_e ~ m_P exp(-3/(8 alpha))")
    p("  imitated this mechanism, but here the exponent comes from a measured running coupling, not a fit.")

    # ---------- figures
    _, frames = kick(1.4, w, T=120.0, record=True)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
    xs = X[::8]
    im = axs[0].imshow(frames.T, origin="lower", aspect="auto", cmap="RdBu", vmin=-1.2, vmax=1.2,
                       extent=(0, frames.shape[0] - 1, xs[0], xs[-1]))
    axs[0].set(ylim=(-120, 120), xlabel="time", ylabel="position in the substrate",
               title=f"A kick of energy {1.4 ** 2 * w:.1f} (= {1.4 ** 2 * w / (2 * M_KINK):.1f} x 2M) creates a particle pair")
    axs[0].grid(False)
    cb = fig.colorbar(im, ax=axs[0], pad=0.02)
    cb.set_label("substrate field (blue = original ground state, red = the other one)", color=INK_2)
    Es = np.array([r[0] for r in rows])
    Ns = np.array([r[1] for r in rows])
    axs[1].plot(Es, Ns, "o", color=S1, ms=7, label="simulated outcome")
    ee = np.linspace(0, Es.max() * 1.05, 200)
    axs[1].plot(ee, np.floor(ee / M_KINK / 2) * 2, color=S2, ls="--", label="most particles energy allows (E / M)")
    axs[1].axvline(2 * M_KINK, color=MUTED, ls=":", lw=1.2)
    axs[1].text(2 * M_KINK + 0.2, 6.3, "2M: minimum\nfor one pair", color=INK_2, fontsize=9)
    axs[1].set(xlabel="energy injected", ylabel="particles left after radiation escapes", ylim=(-0.5, 9),
               xlim=(0, Es.max() * 1.05), title="Particles appear in pairs, only above 2M")
    axs[1].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "pair_creation")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
