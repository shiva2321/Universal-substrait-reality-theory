"""
r21 - USRT's own relation: the cosmological constant from the number of particle species
(LAB_NOTEBOOK.md entry E29)

Question (user): "So far we have relied on the work of others; now it is time to embark on our own
ideas and establish calculations, rules and formulations of our own, grounded in the actual reality
of the world, novel and actually useful."

The idea (ours, to our knowledge -- see E29 for the literature check).  Two results of this
programme combine into a relation nobody had written down:
  * r14 (Jacobson / Bekenstein-Hawking on the substrate): the substrate's cell size is fixed by the
    number of particle species N:  l^2 = 4 N eta l_P^2,  eta = 0.0242 per cell face (computed).
  * r19 / Sorkin's 'everpresent Lambda': in unimodular gravity Lambda and 4-volume V are conjugate,
    Delta Lambda Delta V ~ 8 pi kappa l_P^2 (kappa = 1/2 or 1 by convention), and a discrete substrate
    has Poisson volume noise Delta V = l^2 sqrt(V).
  =>  USRT relation:   Lambda * sqrt(V)  =  2 pi kappa / (N eta)        (Planck units drop out)
The amplitude of Lambda is set by how many kinds of particles exist.  We test it against reality:
  A. Exact pieces: past-light-cone volumes V = C t^4 in radiation/matter eras (sympy); the observed
     A_obs = Lambda_obs sqrt(V_past) for Planck 2018 LCDM (numerical, validated on the exact limits).
  B. The species number this needs, vs the Standard Model.
  C. The same mechanism at EVERY epoch: Omega_Lambda fluctuates with rms = A g(z); the early universe
     (BBN, recombination) is the test.  Exact: X = W(V)/sqrt(V) is an Ornstein-Uhlenbeck process in ln V.
  D. Monte Carlo of whole histories: probability to pass BBN, CMB and today's value, as a function of N.
  E. Late-time behaviour of the histories that match today: effective (w0, wa) vs DESI DR2.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
from scipy import integrate  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r21_lambda_from_species"
ETA = 0.02421                         # r14: area-law coefficient per cell face (cubic lattice)
ETA_RAD = 0.02349                     # r14: radial (Srednicki) lattice, kappa/4pi
# Planck 2018 (TT,TE,EE+lowE+lensing) background
h, OM, ORH2 = 0.6736, 0.3153, 4.18e-5
OR = ORH2 / h ** 2
OL = 1 - OM - OR
T0_EV = 2.3487e-4                     # photon temperature today in eV (2.7255 K)
NEFF = (2.99, 0.17)                   # Planck 2018 N_eff (BBN+CMB-consistent)
DESI = {"DESI+CMB+Pantheon+": (-0.838, 0.055, -0.62, 0.205),
        "DESI+CMB+Union3": (-0.667, 0.088, -1.09, 0.29)}      # DR2 2025, arXiv:2503.14738
SM_DOF = 118                          # 28 bosonic + 90 fermionic degrees of freedom


def background():
    H0 = 1.0                          # work in units of 1/H0
    def H(a):
        return H0 * np.sqrt(OR / a ** 4 + OM / a ** 3 + OL)
    lna = np.linspace(np.log(1e-13), 0, 60001)
    a = np.exp(lna)
    dt = 1 / H(a)
    t = integrate.cumulative_trapezoid(dt, lna, initial=0) + 1e-26 / (2 * math.sqrt(OR))
    eta = integrate.cumulative_trapezoid(1 / (a * H(a)), lna, initial=0) + 1e-13 / math.sqrt(OR)
    # past-light-cone 4-volume of an observer at every epoch: V(i) = (4 pi/3) int dt a^3 (eta_i - eta)^3
    w = (4 * np.pi / 3) * a ** 3 * dt
    # expand (eta_i - eta)^3 to get all V(i) from cumulative sums (exact algebra, O(n))
    d = np.diff(lna)
    def cum(f):
        return np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * d)])
    I0, I1, I2, I3 = cum(w), cum(w * eta), cum(w * eta ** 2), cum(w * eta ** 3)
    V = eta ** 3 * I0 - 3 * eta ** 2 * I1 + 3 * eta * I2 - I3
    return a[1:], H(a)[1:], t[1:], V[1:]          # drop the first point (V = 0 there)


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. The relation, and the exact pieces")
    p("unimodular conjugacy  Delta V * Delta(Lambda/8 pi G) ~ kappa hbar   ->  Delta Lambda = 8 pi kappa l_P^2 / Delta V")
    p("Poisson substrate     Delta V = l^2 sqrt(V)       (one element per l^4)")
    p("species fix the cell  l^2 = 4 N eta l_P^2         (r14: entanglement area law = A/4G)")
    p("=> Lambda sqrt(V) = 2 pi kappa / (N eta)  ==: A_N    (dimensionless; l_P cancels)")
    u = sp.symbols("u", positive=True)
    C_rad = sp.simplify(sp.Rational(32, 3) * sp.pi * 2 * sp.integrate(u ** 4 * (1 - u) ** 3, (u, 0, 1)))
    C_mat = sp.simplify(36 * sp.pi * 3 * sp.integrate(u ** 8 * (1 - u) ** 3, (u, 0, 1)))
    g_rad = sp.nsimplify(4 / (3 * sp.sqrt(C_rad)))
    g_mat = sp.nsimplify(3 / (4 * sp.sqrt(C_mat)))
    p(f"exact past-light-cone volumes: radiation era V = {C_rad} t^4, matter era V = {C_mat} t^4")
    p(f"rms Omega_Lambda per unit A_N:  radiation era 4/(3 sqrt C) = {float(g_rad):.4f};  matter era 3/(4 sqrt C) = {float(g_mat):.4f}")
    a, H, t, V = background()
    g = 1 / (3 * H ** 2 * np.sqrt(V))                   # rms Omega_Lambda per unit A
    i_rad = np.argmin(abs(a - 1e-9))
    p(f"numerical LCDM check deep in radiation era: {g[i_rad]:.4f} (exact {float(g_rad):.4f})")
    A_obs = 3 * OL * math.sqrt(V[-1])                   # Lambda_obs sqrt(V_past) in units H0 = c = 1
    p(f"today: V_past H0^4 = {V[-1]:.4f};  A_obs = Lambda_obs sqrt(V_past) = {A_obs:.4f}  (Planck 2018 LCDM)")

    p.section("B. How many particle species does today's Lambda need?")
    rows = []
    for et, lab in ((ETA, "cubic lattice"), (ETA_RAD, "radial lattice")):
        for kap in (0.5, 1.0):
            Nn = 2 * math.pi * kap / (et * A_obs)
            rows.append(Nn)
            p(f"   eta = {et} ({lab}), kappa = {kap}: N_needed = {Nn:.0f}")
    p(f"   Standard Model: {SM_DOF} degrees of freedom (28 bosonic + 90 fermionic)")
    for kap in (0.5, 1.0):
        p(f"   eliminating N (no spin weighting needed): cell size l = sqrt(8 pi kappa / A_obs) l_P = "
          f"{math.sqrt(8 * math.pi * kap / A_obs):.2f} l_P  (kappa = {kap})")
    p("   -> if Lambda is the substrate's counting noise, its cells are 4-6 Planck lengths across.")
    p(f"=> if every degree of freedom counts once, the SM gives Lambda within a factor {min(rows) / SM_DOF:.1f}-{max(rows) / SM_DOF:.1f}"
      f" of the observed value -- no parameter fitted (the conventions span the range).")
    p("   CAVEAT: how much each spin counts in eta (and in induced 1/G) is regulator-dependent and contested:")
    p("   heat-kernel weights give gauge fields NEGATIVE contributions (Kabat 1995; Larsen & Wilczek 1996),")
    p("   which could push the SM's effective N to O(1). So this is an order-of-magnitude link, not a fit.")

    p.section("C. The same mechanism at every epoch")
    for z_lab, z in (("BBN, T = 1 MeV", 1e6 / T0_EV - 1), ("BBN, T = 70 keV", 7e4 / T0_EV - 1),
                     ("matter-radiation equality", 3400), ("recombination", 1100), ("z = 2", 2), ("today", 0)):
        i = np.argmin(abs(a - 1 / (1 + z)))
        p(f"   {z_lab:26s} z = {z:9.3g}: rms Omega_Lambda = {g[i]:.3f} x A  ->  {g[i] * A_obs:.2f} with A = A_obs")
    om_bbn = 0.2271 * 2 * NEFF[1] / (1 + 0.2271 * 3.044)
    p(f"BBN allows extra energy |Omega_x| < {om_bbn:.3f} (N_eff = {NEFF[0]} +- {NEFF[1]}, 2 sigma)")
    p("=> with today's Lambda as a typical fluctuation, Omega_Lambda during nucleosynthesis is ~2: the")
    p("   expansion rate then would be wrong by tens of percent. The mechanism TRACKS the critical density")
    p("   (rms Omega_Lambda is ~constant: 2.7 A, 1.8 A, 0.95 A), so it cannot be small early and large today.")

    p.section("D. Whole histories: Monte Carlo of the Ornstein-Uhlenbeck process X = W(V)/sqrt(V)")
    p("X(s), s = ln V, obeys dX = -X/2 ds + dB exactly (unit stationary variance); Omega_Lambda = A X g(z).")
    s = np.log(V)
    zall = 1 / a - 1
    Tall = T0_EV * (1 + zall)
    sel_b = (Tall > 7e4) & (Tall < 1e6)
    sel_c = (zall > 1000) & (zall < 3500)
    sel_l = a > 1 / 3.0
    # fine grids (ds = 0.05) inside the tested windows; exact OU jumps in between
    grids = []
    for sel in (sel_b, sel_c, sel_l):
        lo, hi = s[sel].min(), s[sel].max()
        grids.append(np.arange(lo, hi + 1e-12, 0.05))
    pts = np.concatenate(grids)
    g_at = np.interp(pts, s, g)
    a_at = np.interp(pts, s, a)
    win = np.concatenate([np.full(len(grids[0]), 0), np.full(len(grids[1]), 1), np.full(len(grids[2]), 2)])
    rng = np.random.default_rng(29)
    n_hist = 200000
    x = rng.standard_normal(n_hist)                    # stationary start (exact)
    sums = np.zeros((2, n_hist))
    late_rows = []
    prev = pts[0]
    for k, sk in enumerate(pts):
        ds = sk - prev
        if ds > 0:
            x = x * math.exp(-ds / 2) + math.sqrt(-math.expm1(-ds)) * rng.standard_normal(n_hist)
        prev = sk
        if win[k] < 2:
            sums[win[k]] += x * g_at[k]
        else:
            late_rows.append(x.astype(np.float32).copy())
    bbn_mean = sums[0] / len(grids[0])
    cmb_mean = sums[1] / len(grids[1])
    X_late = np.array(late_rows)
    x0 = X_late[-1] * g_at[-1]
    Ns = np.unique(np.round(np.logspace(np.log10(30), np.log10(3e4), 40)))
    prob = {}
    for N in Ns:
        A = 2 * math.pi / (N * ETA)
        okB = np.abs(A * bbn_mean) < om_bbn
        okC = np.abs(A * cmb_mean) < 0.05
        ok0 = np.abs(A * x0 - OL) < 0.02
        prob[N] = (okB.mean(), okC.mean(), ok0.mean(), (okB & okC & ok0).mean(), okB & okC & ok0)
    for N in (60, 120, 360, 1000, 3000, 10000, 30000):
        Nk = Ns[np.argmin(abs(Ns - N))]
        pb, pc, p0, pall, _ = prob[Nk]
        p(f"   N = {Nk:6.0f} (A = {2 * math.pi / (Nk * ETA):.3f}): P(BBN ok) = {pb:.4f}, P(CMB ok) = {pc:.4f},"
          f" P(Omega_L today = 0.685 +- 0.02) = {p0:.5f}, ALL three = {pall:.2e}")
    best = max(prob, key=lambda k: prob[k][3])
    p(f"   best N = {best:.0f}: P(all) = {prob[best][3]:.2e}   (LCDM: 1 by construction)")
    p("   (BBN criterion: |mean Omega over 70 keV < T < 1 MeV| < 0.046; CMB: |mean over 1000 < z < 3500| < 0.05,")
    p("    an approximate early-dark-energy bound; fixed LCDM background, no back-reaction.)")

    p.section("E. Late-time behaviour of histories that match today's Omega_Lambda: (w0, wa) vs DESI")
    Nsel = 360
    A = 2 * math.pi / (Nsel * ETA)
    match = np.abs(A * x0 - OL) < 0.02
    Xl = X_late[:, match]
    al = a_at[win == 2]
    rho = Xl * (1 / np.sqrt(np.exp(pts[win == 2])))[:, None]
    rho = rho / rho[-1]
    signchange = np.any(rho <= 0, axis=0)
    good = ~signchange
    w0s, was = [], []
    M = np.vstack([np.log(al), 1 - al]).T
    for col in np.where(good)[0]:
        y = np.log(rho[:, col])
        # ln rho = -3(1+w0+wa) ln a - 3 wa (1-a)
        coef = np.linalg.lstsq(M, y, rcond=None)[0]
        wa = -coef[1] / 3
        w0 = -coef[0] / 3 - 1 - wa
        w0s.append(w0)
        was.append(wa)
    w0s, was = np.array(w0s), np.array(was)
    p(f"   N = {Nsel}: {match.sum()} histories match today; {signchange.mean():.0%} of them change the sign of Lambda before z = 2")
    if len(w0s):
        p(f"   the rest: median w0 = {np.median(w0s):.2f}, median wa = {np.median(was):.2f};"
          f" in DESI's quadrant (w0 > -1, wa < 0): {np.mean((w0s > -1) & (was < 0)):.0%}")
        for k, (m0, s0, ma, sa) in DESI.items():
            inside = np.mean((np.abs(w0s - m0) < 2 * s0) & (np.abs(was - ma) < 2 * sa))
            p(f"   within the 2-sigma box of {k} (w0 = {m0} +- {s0}, wa = {ma} +- {sa}): {inside:.1%}")
    p("=> the mechanism's dark energy evolves strongly at late times (it tracks V^(-1/2) and fluctuates):")
    p("   it naturally gives w0 > -1 like DESI's hint, but usually far more evolution than measured.")

    p.section("F. Inventing the box: can quieter-than-Poisson counting rescue it? (no-go for any power law)")
    p("Generalise the substrate's counting statistics: Var(number in V) = (V/l^4)^gamma  (Poisson: gamma = 1;")
    p("gamma < 1 = 'hyperuniform', quieter on large scales). Then Delta V = l^4 (V/l^4)^(gamma/2) and")
    p("   Lambda = 8 pi kappa lam^(2 gamma - 4) V^(-gamma/2)   (Planck units, l = lam l_P),  Omega_Lambda ~ V^((1-gamma)/2) g(z)")
    lP_m, H0_si = 1.616255e-35, 67.36e3 / 3.0857e22
    V0_pl = V[-1] * (2.99792458e8 / H0_si / lP_m) ** 4
    Lam_pl = 3 * OL * (H0_si / 2.99792458e8) ** 2 * lP_m ** 2
    p(f"today: V_past = {V0_pl:.2e} Planck 4-volumes, Lambda_obs = {Lam_pl:.3e} (Planck units)")
    gam_mag = {}
    for lam in (1, 4, 6, 10, 30):
        for kap in (0.5, 1.0):
            gm = (math.log(8 * math.pi * kap) - 4 * math.log(lam) - math.log(Lam_pl)) / (0.5 * math.log(V0_pl) - 2 * math.log(lam))
            gam_mag[(lam, kap)] = gm
        p(f"   cell size {lam:2d} l_P: today's Lambda needs gamma = {gam_mag[(lam, 0.5)]:.4f} (kappa 1/2) - {gam_mag[(lam, 1.0)]:.4f} (kappa 1)")
    i_b = np.argmin(abs(a - 1 / (1 + 1e6 / T0_EV)))
    lnVr = math.log(V[-1] / V[i_b])
    need = math.log((g[i_b] / g[-1]) * OL / om_bbn)
    gam_bbn = 1 - 2 * need / lnVr
    p(f"   BBN (|Omega| < {om_bbn:.3f} at T = 1 MeV while Omega_0 = {OL:.3f}): gamma <= {gam_bbn:.3f}"
      f"   [ln(V_0/V_BBN) = {lnVr:.1f}]")
    dlnV = np.gradient(np.log(V), np.log(a))[-1]
    w0_max = DESI["DESI+CMB+Union3"][0] + 2 * DESI["DESI+CMB+Union3"][1]
    gam_w0 = 6 * (1 + w0_max) / dlnV
    p(f"   near-constancy today: the typical (tracking) part gives w0 = -1 + gamma (dlnV/dlna)/6 with dlnV/dlna = {dlnV:.2f};")
    p(f"   the loosest DESI bound w0 < {w0_max:.3f} (Union3, 2 sigma) needs gamma <= {gam_w0:.3f}")
    p(f"=> NO-GO: today's size needs gamma = 1.00 (to +-{max(abs(v - 1) for v in gam_mag.values()):.3f} for cells of 1-30 l_P),")
    p(f"   BBN needs gamma <= {gam_bbn:.3f} and today's near-constancy gamma <= {gam_w0:.2f}. No power-law counting")
    p("   statistics gives a dark energy that is both the right size and as steady as observed. Counting-")
    p("   noise Lambda needs fluctuations that FREEZE (non-Markovian memory) -- or Lambda has another origin.")
    G_NOGO = (gam_mag, gam_bbn, gam_w0)

    p.section("Verdict")
    for line in (
        "* NEW RELATION (ours): Lambda sqrt(V_past) = 2 pi kappa/(N eta). With every Standard-Model degree of",
        f"  freedom counting once, it gives today's Lambda within a factor ~1.5-3 (N needed {min(rows):.0f}-{max(rows):.0f} vs 118).",
        "* BUT the same counting noise acts at every epoch and tracks the critical density: it makes the",
        "  early universe fail BBN/CMB unless we are lucky at the ~1e-4 level or worse (D). This agrees with",
        "  the difficulties reported for everpresent-Lambda models (Das et al. 2023-24) and now quantifies",
        "  them as a function of the species number.",
        "* DESIGN RULE for USRT dynamics: Lambda's counting noise must be suppressed in the early universe",
        f"  by a factor >~ {g[i_rad] * A_obs / om_bbn:.0f} relative to white noise in V (BBN), while staying O(1) today.",
        "* NO-GO (ours, F): quieter-than-Poisson counting with any power law cannot do it -- the size of",
        f"  Lambda pins gamma = 1.00, while BBN and DESI's near-constancy need gamma <= {G_NOGO[1]:.3f} and <= {G_NOGO[2]:.2f}.",
        "  A working version needs fluctuations with memory that freeze at late times.",
    ):
        p(line)

    # ---------- figure
    fig, axs4 = plt.subplots(2, 2, figsize=(12.5, 9.2))
    axs = [axs4[0, 0], axs4[0, 1], axs4[1, 0]]
    ax = axs[0]
    NN = np.logspace(0.5, 4, 200)
    ax.loglog(NN, 2 * np.pi / (NN * ETA), color=S1, lw=2, label="USRT: Λ√V = 2π/(N η)  (κ = 1)")
    ax.loglog(NN, np.pi / (NN * ETA), color=S1, lw=1.5, ls="--", label="same, κ = 1/2")
    ax.axhline(A_obs, color=S2, lw=1.8, label=f"observed Λ√V_past = {A_obs:.2f}")
    ax.axvline(SM_DOF, color=MUTED, ls=":", lw=1.4)
    ax.text(SM_DOF * 1.1, 30, "Standard Model\n118 d.o.f.", color=INK_2, fontsize=8.5)
    ax.set(xlabel="number of particle species N", ylabel="Λ √V (dimensionless)", ylim=(0.01, 100),
           title="Today's Λ from the species count:\na factor ~1.5–3 from the Standard Model")
    ax.legend(loc="lower left", fontsize=8.5)
    ax = axs[1]
    zplot = 1 / a - 1
    m = (zplot > 1e-3) & (zplot < 1e10)
    ax.loglog(1 + zplot[m], g[m] * A_obs, color=S1, lw=2, label="rms |Ω_Λ| of the mechanism (A = A_obs)")
    ax.axhspan(1e-4, om_bbn, xmin=0.0, xmax=1.0, color="#e4efe9", lw=0)
    ax.axvspan(1 + 7e4 / T0_EV, 1 + 1e6 / T0_EV, color="#f4e4dc", lw=0)
    ax.text(1.4e8, 0.012, "BBN window", color=INK_2, fontsize=8.5)
    ax.text(2, 0.025, f"allowed at BBN: |Ω| < {om_bbn:.3f}", color=INK_2, fontsize=8.5)
    ax.set(xlabel="1 + z", ylabel="|Ω_Λ| (rms)", ylim=(1e-2, 10),
           title="The mechanism tracks the critical density:\nO(1) at nucleosynthesis, where ~0.05 is allowed")
    ax.legend(loc="upper left", fontsize=8.5)
    ax = axs[2]
    if len(w0s):
        ax.plot(w0s, was, ".", color=MUTED, ms=2, alpha=0.5,
                label=f"histories matching today, N = {Nsel}\n(the {1 - signchange.mean():.0%} without a sign flip)")
    for (k, (m0, s0, ma, sa)), col in zip(DESI.items(), (S1, S3)):
        ax.errorbar(m0, ma, xerr=s0, yerr=sa, fmt="o", color=col, ms=7, capsize=3, label=k)
    ax.plot(-1, 0, "*", color=S2, ms=12, label="cosmological constant (ΛCDM)")
    ax.set(xlim=(-2.5, 1.5), ylim=(-6, 4), xlabel="w0 (dark-energy pressure today)", ylabel="wa (its evolution)",
           title="Late-time dark energy of the mechanism\nvs DESI DR2")
    ax.legend(loc="lower left", fontsize=8)
    ax = axs4[1, 1]
    gam_mag, gam_bbn, gam_w0 = G_NOGO
    lams = np.logspace(0, np.log10(30), 50)
    for kap, ls in ((0.5, "--"), (1.0, "-")):
        gm = [(math.log(8 * math.pi * kap) - 4 * math.log(L) - math.log(Lam_pl)) / (0.5 * math.log(V0_pl) - 2 * math.log(L))
              for L in lams]
        ax.semilogx(lams, gm, color=S1, ls=ls, lw=2, label=f"γ that gives today's Λ (κ = {kap:g})")
    ax.axhspan(0, min(gam_bbn, gam_w0), color="#e4efe9", lw=0)
    ax.text(1.05, 0.38, "allowed by BBN and DESI", color=INK_2, fontsize=8.5)
    ax.axhline(gam_bbn, color=S3, lw=1.6, label=f"BBN allows γ ≤ {gam_bbn:.3f}")
    ax.axhline(gam_w0, color=S2, lw=1.6, label=f"DESI near-constancy allows γ ≤ {gam_w0:.2f}")
    ax.set(xlabel="substrate cell size (Planck lengths)", ylabel="counting exponent γ  (Var ∝ V^γ)",
           ylim=(0, 1.1), title="No power-law counting statistics can make\nΛ both the right size and steady")
    ax.legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "lambda_species")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
