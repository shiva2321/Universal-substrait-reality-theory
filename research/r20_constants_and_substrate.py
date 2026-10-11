"""
r20 - The constants of nature and the substrate: how, why and whether they relate  (LAB_NOTEBOOK.md E27)

Question (user): "I think all the constants of reality have something to do with the universal
substrate too. They all have relations which we might be missing field-wide, and nobody has made the
connections yet. Let's explore them too and see what, how and why they relate and contribute."

Rules (from the audit, which caught the original USRT fitting constants): compare with measurements
in sigma, separate inputs from outputs, and count the look-elsewhere effect.
  A. Units vs numbers: c, hbar, G are conversion factors -- in the substrate, the cells' signal speed,
     action and size (r05, r13, r14, r19).  Only DIMENSIONLESS numbers carry physics.
  B. How the numbers build the world: atom, planet and star sizes/masses from alpha, alpha_G and m_e/m_p
     (Carr & Rees 1979; Press & Lightman 1983) -- computed and compared with real objects.
  C. Real connections already known: the three gauge couplings run with energy and (nearly) meet --
     one coupling of the substrate at high energy?  One-loop running, SM vs MSSM; proton-decay test.
  D. Why gravity is so weak: dimensional transmutation turns a modest coupling into a 10^-19 mass ratio.
  E. Large-number coincidences (Dirac) and the test that killed them; are the constants constant?
  F. A null test for 'new connections': are the measured constants closer to simple formulas
     (2^a 3^b 5^c pi^d e^f) than RANDOM numbers are?  If not, a 'relation' is numerology.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import ALPHA, G0, INK_2, MUTED, S1, S2, S3, Report, c, hbar, lP, mP, save_fig, style  # noqa: E402

AUD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audit")
sys.path.insert(0, AUD)
from common import alpha as ALPHA_U, m_e_kg, m_e_MeV, m_mu_MeV, m_tau_MeV, mu_pe, dm_np_MeV  # noqa: E402

NAME = "r20_constants_and_substrate"
M_P_KG = 1.67262192595e-27                       # proton mass (CODATA 2022)
M_SUN, M_JUP, R_SUN = 1.98892e30, 1.89813e27, 6.957e8
MZ = 91.1880                                     # GeV (PDG 2024)
AINV_EM_MZ, SW2, AS_MZ = 127.951, 0.2312, 0.1180  # alpha^-1(MZ) MS-bar, sin^2 theta_W(MZ), alpha_s(MZ)
YEAR = 3.15576e7


def running(b, ainv0, t):
    return ainv0 - b / (2 * math.pi) * t


def main():
    p = Report(NAME)
    style(plt)
    me, mp_ = m_e_kg[0], M_P_KG
    aG = G0 * mp_ ** 2 / (hbar * c)

    p.section("A. Units versus numbers")
    p("c, hbar, G (and k_B, epsilon_0) only convert between units; change them together with your rulers")
    p("and clocks and nothing observable changes (Duff, Okun & Veneziano, JHEP 03 (2002) 023).")
    p("In the substrate picture they are the CELLS' properties:")
    p("   c    = maximum signal speed of the cells (r05) -- or the cone structure itself (r19)")
    p("   hbar = quantum of action per cell (r06, r17)")
    p(f"   G    = l_P^2 c^3/hbar, with the cell size a = 0.31 sqrt(N) l_P (r14): l_P = {lP():.4e} m")
    p("What physics actually measures are pure numbers. The ones that build our world:")
    nums = [("alpha (electromagnetism)", ALPHA, "1/137.035999177(21)"),
            ("alpha_G = G m_p^2/(hbar c) (gravity)", aG, "rel. unc. 2e-5 (from G)"),
            ("beta = m_e/m_p", me / mp_, "1/1836.152673426(32)"),
            ("alpha_s(M_Z) (strong force)", AS_MZ, "+- 0.0009"),
            ("Lambda l_P^2 (cosmological constant)", 2.8e-122, "Planck 2018"),
            ("eta = baryons/photons", 6.1e-10, "Planck 2018 / BBN")]
    for n, v, u in nums:
        p(f"   {n:42s} {v:.6e}   [{u}]")
    p("The Standard Model + gravity + cosmology needs about 31 such numbers (Tegmark, Aguirre, Rees &")
    p("Wilczek, PRD 73, 023505 (2006)). No accepted theory derives any of them from first principles.")

    p.section("B. How the numbers build the world (dimensional estimates, then real objects)")
    a0 = hbar / (me * c * ALPHA)
    Ry = 0.5 * ALPHA ** 2 * me * c ** 2 / 1.602176634e-19
    M_star = aG ** -1.5 * mp_
    M_ch = 3.098 * (hbar * c / G0) ** 1.5 / (2 * mp_) ** 2            # Chandrasekhar, mu_e = 2
    M_planet = (ALPHA / aG) ** 1.5 * mp_
    p(f"atom size     a0 = hbar/(m_e c alpha)            = {a0:.4e} m      (Bohr radius, exact definition)")
    p(f"atom energy   alpha^2 m_e c^2 / 2               = {Ry:.4f} eV     (hydrogen ionisation 13.6 eV)")
    p(f"star mass     alpha_G^(-3/2) m_p                = {M_star:.3e} kg = {M_star / M_SUN:.2f} solar masses")
    p(f"   Chandrasekhar limit 3.098 (hbar c/G)^(3/2) / (mu_e m_p)^2 = {M_ch / M_SUN:.3f} M_sun (measured white dwarfs: <= ~1.4)")
    p(f"largest cold planet  (alpha/alpha_G)^(3/2) m_p   = {M_planet:.3e} kg = {M_planet / M_JUP:.2f} Jupiter masses")
    p(f"number of protons in a star ~ alpha_G^(-3/2)    = {aG ** -1.5:.2e}")
    p("=> two numbers, alpha ~ 1e-2 and alpha_G ~ 1e-39, set the sizes of atoms, planets and stars")
    p("   (Carr & Rees, Nature 278, 605 (1979); Press & Lightman, Phil. Trans. R. Soc. A 310, 323 (1983)).")
    p("   A star holds ~ alpha_G^(-3/2) ~ 1e57 protons BECAUSE gravity is 1e39 times weaker than the")
    p("   other forces. These are real, quantitative relations between constants and structure.")

    p.section("C. A real connection: the three forces' strengths meet at high energy (one-loop running)")
    a1 = 0.6 * (1 - SW2) * AINV_EM_MZ
    a2 = SW2 * AINV_EM_MZ
    a3 = 1 / AS_MZ
    p(f"inputs at M_Z: 1/alpha_1 = {a1:.2f} (GUT-normalised), 1/alpha_2 = {a2:.2f}, 1/alpha_3 = {a3:.3f}")
    models = {"Standard Model": (41 / 10, -19 / 6, -7.0), "MSSM (superpartners from M_Z)": (33 / 5, 1.0, -3.0)}
    cross = {}
    for name, (b1, b2, b3) in models.items():
        t12 = (a1 - a2) / ((b1 - b2) / (2 * math.pi))
        t23 = (a2 - a3) / ((b2 - b3) / (2 * math.pi))
        t13 = (a1 - a3) / ((b1 - b3) / (2 * math.pi))
        mus = [MZ * math.exp(t) for t in (t12, t23, t13)]
        spread = max(mus) / min(mus)
        cross[name] = (mus, (b1, b2, b3))
        p(f"   {name:30s} pairwise meeting points: {mus[0]:.1e}, {mus[1]:.1e}, {mus[2]:.1e} GeV (spread x{spread:.0f})")
        if name.startswith("MSSM"):
            tU = t12
            p(f"      unified 1/alpha = {running(b1, a1, tU):.2f} at {MZ * math.exp(tU):.1e} GeV;"
              f" 1/alpha_3 there = {running(b3, a3, tU):.2f}")
    MPl_GeV = mP() * c ** 2 / 1.602176634e-10
    p(f"   Planck energy {MPl_GeV:.2e} GeV")
    p("=> the three couplings are NOT independent-looking: they nearly meet near 1e16 GeV, within ~1e3 of")
    p("   the Planck scale (Georgi & Glashow 1974; Amaldi, de Boer & Fuerstenau, Phys. Lett. B 260, 447")
    p("   (1991)). With the SM alone they miss (a triangle); with superpartners they meet. In substrate")
    p("   terms: 'the three twist modes may have ONE stiffness at the cell scale; what we measure at low")
    p("   energy is that one number, dressed by the substrate's quantum fluctuations'.")
    p("   Test: unification predicts proton decay. Super-Kamiokande: tau(p -> e+ pi0) > 2.4e34 years")
    p("   (PRD 102, 112011 (2020)); minimal SU(5) (~1e31 yr) is excluded; SUSY versions survive so far.")

    p.section("D. Why gravity is so weak: an exponential from a modest number (dimensional transmutation)")
    b3_6 = 7.0
    a3_P = a3 + b3_6 / (2 * math.pi) * math.log(MPl_GeV / MZ)
    p(f"run 1/alpha_s up to the Planck energy (one loop, 6 flavours): 1/alpha_s(M_P) ~ {a3_P:.1f}")
    p("the strong scale where alpha_s blows up: Lambda ~ M_P exp(-2 pi / (b alpha_s(M_P)))")
    p(f"   d ln(m_p) / d(1/alpha_s(M_P)) = -2 pi / b = {-2 * math.pi / b3_6:.2f}: a 10% change in 1/alpha_s(M_P)"
      f" changes m_p by x{math.exp(2 * math.pi / b3_6 * 0.1 * a3_P):.0f} and alpha_G by x{math.exp(2 * 2 * math.pi / b3_6 * 0.1 * a3_P):.0e}")
    p(f"   alpha_G = (m_p/m_P)^2 = {aG:.2e}: the 1e-39 is the square of an exponential of ~{a3_P:.0f} x (2 pi/7)")
    p("=> the 'hierarchy' between gravity and the other forces is not a coincidence to be fitted: it is the")
    p("   logarithmic running of the strong coupling (Wilczek; Gross, Politzer 1973). The original USRT")
    p("   formula m_e ~ m_P exp(-3/(8 alpha)) imitated this, but with the wrong coupling and a fitted exponent.")

    p.section("E. Large-number coincidences, and whether the constants are constant")
    re_ = ALPHA * hbar / (me * c)
    t0 = 13.80e9 * YEAR
    N1 = ALPHA * hbar * c / (G0 * mp_ * me)
    N2 = t0 / (re_ / c)
    H0 = 67.4e3 / 3.0857e22
    rho_b = 0.02237 / 0.674 ** 2 * 3 * H0 ** 2 / (8 * math.pi * G0)      # Omega_b h^2 = 0.02237 (Planck 2018)
    Nb = rho_b * 4 / 3 * math.pi * (c / H0) ** 3 / mp_
    p(f"Dirac's numbers: electric/gravitational force between p and e  N1 = {N1:.2e}")
    p(f"                 age of universe / light-crossing time of an electron  N2 = {N2:.2e}")
    p(f"                 protons in the Hubble volume  Nb = {Nb:.1e}  (vs N1^2 = {N1 ** 2:.1e})")
    p("Dirac (1937) guessed N1 ~ N2 always, so G ~ 1/t: predicted dG/dt / G = -1/t0 =" f" {-1 / (13.8e9):.1e} per year.")
    LLR = (4e-13, 9e-13)
    p(f"Lunar laser ranging (Williams, Turyshev & Boggs, PRL 93, 261101 (2004)): ({LLR[0]:.0e} +- {LLR[1]:.0e}) per year"
      f" -> Dirac excluded at {abs(-1 / 13.8e9 - LLR[0]) / LLR[1]:.0f} sigma")
    p("Dicke (Nature 192, 440 (1961)): N1 ~ N2 because observers exist when stars shine, which ties t to")
    p("   alpha_G -- a selection effect, not a law.")
    ALDOT = (1.0e-18, 1.1e-18)
    p(f"alpha today: atomic clocks give d(alpha)/dt / alpha = ({ALDOT[0]:.1e} +- {ALDOT[1]:.1e}) per year (Lange et al.,")
    p(f"   PRL 126, 011102 (2021)): over the age of the universe at most ~{(ALDOT[0] + 2 * ALDOT[1]) * 13.8e9:.0e}.")
    p("=> whatever the substrate is, the ratios of its couplings are FROZEN to ~1e-8 over cosmic history.")

    p.section("F. Null test: are the constants closer to simple formulas than random numbers are?")
    ex = np.arange(-4, 5)
    E = np.array(np.meshgrid(ex, ex, ex, ex, ex, indexing="ij")).reshape(5, -1).T
    logs = E @ np.log([2.0, 3.0, 5.0, math.pi, math.e])
    order = np.argsort(logs)
    logs_s, E_s = logs[order], E[order]
    p(f"formula family: 2^a 3^b 5^c pi^d e^f with |exponents| <= 4: {len(logs)} formulas")

    def best(x):
        lx = math.log(x)
        i = np.searchsorted(logs_s, lx)
        cand = [j for j in (i - 1, i) if 0 <= j < len(logs_s)]
        j = min(cand, key=lambda k: abs(logs_s[k] - lx))
        return abs(logs_s[j] - lx), E_s[j]
    rng = np.random.default_rng(42)
    rand = np.exp(rng.uniform(math.log(1e-2), math.log(1e4), 20000))
    rand_best = np.array([best(x)[0] for x in rand])
    consts = [("1/alpha", 1 / ALPHA_U[0], ALPHA_U[1] / ALPHA_U[0]),
              ("m_p/m_e", mu_pe[0], mu_pe[1] / mu_pe[0]),
              ("m_mu/m_e", m_mu_MeV[0] / m_e_MeV[0], m_mu_MeV[1] / m_mu_MeV[0]),
              ("m_tau/m_e", m_tau_MeV[0] / m_e_MeV[0], m_tau_MeV[1] / m_tau_MeV[0]),
              ("m_n/m_p", 1 + dm_np_MeV[0] / 938.27208943, dm_np_MeV[1] / 938.27208943),
              ("1/alpha_s(M_Z)", 1 / AS_MZ, 0.0009 / AS_MZ),
              ("sin^2 theta_W", SW2, 0.0001 / SW2),
              ("m_W/m_Z", 80.3692 / 91.1880, math.hypot(0.0133 / 80.3692, 0.0020 / 91.188))]
    names = ("2", "3", "5", "pi", "e")
    pct = {}
    for n, v, rel in consts:
        d, e = best(v)
        frac = float(np.mean(rand_best <= d))
        pct[n] = (d, frac, rel)
        form = " ".join(f"{b}^{k}" for b, k in zip(names, e) if k != 0)
        n_fit = int(np.sum(np.abs(logs - math.log(v)) <= rel))
        p(f"   {n:15s} = {v:.10g}: nearest formula {form:28s} misses by {d:.1e} (= {d / rel:.1e} sigma);"
          f" {100 * frac:4.1f}% of random numbers do better; formulas within 1 sigma: {n_fit}")
    lenz = 6 * math.pi ** 5
    p(f"   e.g. Lenz (1951): m_p/m_e = 6 pi^5 = {lenz:.6f} vs {mu_pe[0]:.9f}: off by"
      f" {abs(lenz - mu_pe[0]) / mu_pe[1]:.1e} sigma")
    p("   (a constant measured to 1e-2 or 1e-4 is 'fitted' within 1 sigma by many formulas -- that is the")
    p("   look-elsewhere effect, not a discovery; the precisely measured ones are fitted by none)")
    p("=> the measured constants are NOT special with respect to simple formulas: their 'closest formula'")
    p("   is as close as it is for random numbers (percentiles spread between 0 and 100%), and for the")
    p("   precisely measured ones the best formula misses by thousands to millions of sigma. A NEW")
    p("   connection must (i) beat this look-elsewhere baseline, (ii) hit within the measurement error,")
    p("   and (iii) come from a mechanism (like C or D), not a search.")

    p.section("G. Map: which constants the substrate explains, constrains, or takes as input")
    rows = [("c, hbar, G", "units of the substrate's cells", "r05, r13, r14, r19"),
            ("spacetime dimension 4", "counted from the order (Myrheim-Meyer), not explained", "r19"),
            ("Lambda ~ 1e-122", "order of magnitude from counting fluctuations (causal set)", "r19"),
            ("alpha_G ~ 1e-39", "exp of the strong coupling's running (D); cell size restates it", "r07, r14, r20"),
            ("alpha, alpha_s, alpha_w", "maybe one coupling at the cell scale (C); alpha < 0.079 bound", "r06, r20"),
            ("star / planet / atom scales", "follow from alpha, alpha_G, m_e/m_p (B)", "r20"),
            ("mass ratios, mixing angles", "INPUTS: no mechanism; formula fits fail the null test (F)", "audit, r20"),
            ("eta (matter excess)", "INPUT; needs T violation (r18) + something more", "r18")]
    for a, b_, cc in rows:
        p(f"   {a:28s} {b_:66s} [{cc}]")

    # ---------- figure
    fig, axs = plt.subplots(2, 2, figsize=(12.5, 9.2))
    ax = axs[0, 0]
    objs = [("hydrogen atom", me + mp_, a0, "atom"), ("Earth", 5.972e24, 6.371e6, "planet"),
            ("Jupiter", M_JUP, 6.9911e7, "planet"), ("Sun", M_SUN, R_SUN, "star"),
            ("Sirius B (white dwarf)", 1.018 * M_SUN, 5.8e6, "star"), ("neutron star", 1.4 * M_SUN, 1.2e4, "star")]
    col = {"atom": S2, "planet": S3, "star": S1}
    place = {"hydrogen atom": (8.0, 8.0, "left"), "Earth": (0.2, 1.0, "right"), "Jupiter": (0.2, 1.6, "right"),
             "Sun": (8.0, 1.0, "left"), "Sirius B (white dwarf)": (8.0, 1.0, "left"), "neutron star": (8.0, 1.0, "left")}
    for n, m, r, k in objs:
        ax.loglog(m, r, "o", color=col[k], ms=8)
        fx, fy, ha = place[n]
        ax.text(m * fx, r * fy, n, fontsize=8, color=INK_2, va="center", ha=ha)
    ax.axvline(M_star, color=S1, ls="--", lw=1.2)
    ax.text(M_star * 2.5, 1e-3, "α_G^(−3/2) m_p\n(stellar mass)", color=S1, fontsize=8.5, ha="left")
    ax.axvline(M_planet, color=S3, ls="--", lw=1.2)
    ax.text(M_planet * 0.4, 1e-3, "(α/α_G)^(3/2) m_p\n(largest planet)", color=S3, fontsize=8.5, ha="right")
    ax.axhline(a0, color=S2, ls="--", lw=1.2)
    ax.text(1e-6, a0 * 200, "a0 = ħ/(m_e c α): atom size", color=S2, fontsize=8.5)
    ax.set(xlim=(1e-29, 1e40), ylim=(1e-12, 1e11), xlabel="mass (kg)", ylabel="radius (m)",
           title="Atoms, planets and stars are sized by\nα, α_G and m_e/m_p")
    ax = axs[0, 1]
    tt = np.linspace(0, math.log(1e19 / MZ), 300)
    E_ = MZ * np.exp(tt)
    for name, ls in (("Standard Model", "-"), ("MSSM (superpartners from M_Z)", "--")):
        b1, b2, b3 = cross[name][1]
        for ainv, b, colr, lab in ((a1, b1, S1, "1/α₁"), (a2, b2, S2, "1/α₂"), (a3, b3, S3, "1/α₃")):
            ax.semilogx(E_, running(b, ainv, tt), color=colr, ls=ls, lw=1.8,
                        label=f"{lab} ({'SM' if name.startswith('Standard') else 'MSSM'})")
    ax.axvline(MPl_GeV, color=MUTED, ls=":", lw=1.2)
    ax.text(MPl_GeV * 0.5, 62, "Planck", color=INK_2, fontsize=8.5, ha="right")
    ax.set(xlabel="energy (GeV)", ylabel="inverse coupling strength", ylim=(0, 84), yticks=[0, 10, 20, 30, 40, 50, 60],
           title="The three forces' strengths run with energy\nand nearly meet: one coupling underneath?")
    ax.legend(loc="upper center", fontsize=7.5, ncol=3)
    ax = axs[1, 0]
    items = list(pct.items())
    yy = np.arange(len(items))
    ax.axvspan(0, 5, color="#f4e4dc", lw=0)
    ax.text(6, 0.5, "← a real hidden relation would sit here (< 5%)", fontsize=8, color=INK_2, va="center")
    ax.plot([100 * f for _, (d, f, rel) in items], yy, "o", color=S1, ms=8, label="measured constant")
    ax.axvline(50, color=MUTED, ls="--", lw=1.2, label="typical for a random number")
    ax.set(yticks=yy, yticklabels=[n for n, _ in items], xlim=(0, 100), ylim=(-0.6, len(items) - 0.2),
           xlabel="% of random numbers that lie closer to a simple formula",
           title="Measured constants are no closer to simple formulas\nthan random numbers are (look-elsewhere test)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(axis="y", visible=False)
    ax = axs[1, 1]
    vals = [("Dirac: G ∝ 1/t", 1 / 13.8e9, S2), ("lunar laser ranging\nbound on |Ġ/G|", LLR[0] + 2 * LLR[1], S1),
            ("atomic clocks:\nbound on |α̇/α|", ALDOT[0] + 2 * ALDOT[1], S1)]
    y = np.arange(len(vals))
    ax.barh(y, [v[1] for v in vals], color=[v[2] for v in vals], height=0.5)
    for yi, v in zip(y, vals):
        ax.text(v[1] * 2, yi, f"{v[1]:.0e} per year", va="center", fontsize=8.5, color=INK_2)
    ax.set_xscale("log")
    ax.set(yticks=y, yticklabels=[v[0] for v in vals], xlim=(1e-19, 1e-7), xlabel="fractional change per year",
           title="Are the constants constant? Dirac's drift is excluded;\nα is frozen to 10⁻¹⁸ per year")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save_fig(fig, NAME, "constants")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
