"""
r31 - Independent re-test, by calculation, of r25 (rule R15), r26 (rule R16) and r28 (rule R17)
(LAB_NOTEBOOK.md entry E42)

Question (user): "analyze this entire research repo deeply and tell me what is it, and what do you think of ot
honestly and where does it stand ds ion plain easy to understand english"

Method: the three newest claims were written in the parallel (Gemini) session. E39 (r29) computed the gauge-field
weight that r26 asserts, and E41 reviewed r25 and r28 by reading their code and printed output ("neither was
re-run"). Here the scripts are re-run and each claim is re-tested with a calculation that does not reuse the thing
being tested; where E41 states a number, it is checked.
  A. r25 (causal-horizon "memory kernel" for the cosmological constant)
     A1. Does splitting a Poisson count into independent causal patches reduce the noise?
     A2. For which observer is the patch count taken?  As coded, against an observer living at that epoch.
     A3. The raw (white-noise) Omega_Lambda at BBN: r25's printed value against the exact past-cone volume.
     A4. The equation of state r25 plots against DESI, and the dark-energy density it implies at z = 1.
  B. r26 (complete Standard Model N_eff ledger)
     B1. Is "0.0 % residual" a test or an identity?
     B2. How far does the Wilson regulator alone move N_eff?
     B3. Are 4.2 and 5.9 l_P independent confirmations from r13 and r14?
  C. r28 (neutral Hopfion dark matter)
     C1. Where the soliton mass comes from.
     C2. sigma = pi R^2 (the code) against 4 pi R^2 (the E38 text).
     C3. What the "sweet spot" requires.
     C4. How sigma/M scales with the Skyrme coupling e under the script's own definitions (E41 states e^-2).
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402
import r25_cosmological_constant_memory as r25  # noqa: E402
import r26_gauge_entanglement_weights as r26  # noqa: E402
import r28_topological_dark_matter as r28  # noqa: E402

NAME = "r31_audit_of_r25_r26_r28"
RNG = np.random.default_rng(29)

OM, OR, OL = r25.OM, r25.OR, r25.OL
A_MIN = 1e-14                       # start of the exact background grid (pure radiation era below this)

# Wilson-fermion weights typed into r26 from r22 / E31, and the cell-size coefficients quoted in r13 / r14
# (results/r13_induced_gravity.txt, results/r14_entanglement_gravity.txt): cell size = coefficient * sqrt(N) l_P.
R_GRID = np.array([0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0])
WD_GRID = np.array([16.50, 12.10, 9.13, 7.20, 5.85, 4.31, 2.70, 1.83])
CELL_PER_SQRT_N = (("entanglement, cubic lattice (r14)", 0.311), ("Sakharov, from inertia (r13)", 0.364),
                   ("Sakharov, from stiffness (r13)", 0.261))


def hubble(a):
    """H / H0 for the Planck 2018 background used in r21 and r25."""
    return np.sqrt(OR / a ** 4 + OM / a ** 3 + OL)


def exact_background(n=60001):
    """Log-spaced grid with the conformal time eta(a) = int da / (a^2 H) (comoving particle horizon)."""
    lna = np.linspace(math.log(A_MIN), 0.0, n)
    a = np.exp(lna)
    H = hubble(a)
    eta = A_MIN / math.sqrt(OR) + integrate.cumulative_trapezoid(1.0 / (a * H), lna, initial=0.0)
    cosmic_t = A_MIN ** 2 / (2.0 * math.sqrt(OR)) + integrate.cumulative_trapezoid(1.0 / H, lna, initial=0.0)
    return lna, a, H, eta, cosmic_t


def cone_volume_and_median_patches(i, lna, a, H, eta):
    """4-volume of the past light cone of the event at grid index i, and the volume-weighted median number of
    Hubble patches N = 1 + 4 (chi a H)^2 across the cone (chi = comoving radius of the cone at the emission epoch).
    dV = (4 pi / 3) a^3 chi^3 dt, with dt = d ln a / H."""
    chi = eta[i] - eta[: i + 1]
    w = (4.0 * np.pi / 3.0) * a[: i + 1] ** 3 / H[: i + 1] * chi ** 3
    cum = integrate.cumulative_trapezoid(w, lna[: i + 1], initial=0.0)
    volume = cum[-1]
    j = int(np.searchsorted(cum, 0.5 * volume))
    return volume, 1.0 + 4.0 * (chi[j] * a[j] * H[j]) ** 2


def poisson_split_demo(n_total=1_000_000, ks=(1, 4, 16, 64, 256, 1024, 4096)):
    """Relative fluctuation of a Poisson count of mean n_total split into K independent patches, in units of
    the unsplit value 1/sqrt(n_total).  r25's rule predicts 1/sqrt(K)."""
    out = []
    for k in ks:
        m = max(1000, 4_000_000 // k)
        total = RNG.poisson(n_total / k, size=(m, k)).sum(axis=1)
        out.append((k, total.std() / total.mean() * math.sqrt(n_total), 1.0 / math.sqrt(2.0 * m)))
    return out


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. r25 (R15): the causal-horizon memory kernel")
    # ------------------------------------------------------------------------------------------------------
    p("A1. Poisson additivity: split a Poisson count (mean 1e6 elements) into K independent patches, add the patch")
    p("    counts, and measure the relative fluctuation of the total in units of the unsplit value 1/sqrt(1e6).")
    p("    r25 multiplies the monolithic noise by 1/sqrt(K) (its 'central limit theorem' step); additivity says 1.")
    demo = poisson_split_demo()
    for k, ratio, err in demo:
        p(f"    K = {k:5d} patches: measured {ratio:.3f} +- {err:.3f}   r25's rule {1 / math.sqrt(k):.3f}")
    worst = max(abs(r - 1.0) / e for _, r, e in demo)
    p(f"    => consistent with 1 for every K (largest deviation {worst:.1f} sigma among {len(demo)} points).  This is the")
    p("       additivity of independent Poisson variables made visible: disjoint counts are already independent, adding")
    p("       them in quadrature returns sqrt(V) exactly, so the extra 1/sqrt(N_patches) in r25 counts the averaging")
    p("       twice. (A separate Lambda per patch would make the noise larger, not smaller.)")

    # ------------------------------------------------------------------------------------------------------
    p("\nA2. Which observer?  r25 takes d_C(a) = comoving distance from the epoch a to TODAY (line 69-74) and applies")
    p("    it to the noise AT epoch a.  For an observer living at the epoch, the cone is built from emission epochs")
    p("    a_em < a_obs and the patch count is N(a_em; a_obs) = 1 + 4 [(eta_obs - eta_em) a_em H_em]^2.")
    lna, a, H, eta, cosmic_t = exact_background()

    # validation of the volume integral: radiation-era closed form V = 8 pi / 105 t^4 at z = 1e9, and r25's own V today
    i_bbn = int(np.searchsorted(a, 1.0 / (1.0 + 1.0e9)))
    v_bbn, _ = cone_volume_and_median_patches(i_bbn, lna, a, H, eta)
    v_rd = 8.0 * np.pi / 105.0 * cosmic_t[i_bbn] ** 4
    v_today, n_today = cone_volume_and_median_patches(len(a) - 1, lna, a, H, eta)
    a25, H25, dc25, np25, sup25, v25 = r25.background()
    p(f"    check: exact V(z=1e9) / (8 pi t^4 / 105) = {v_bbn / v_rd:.5f};  V_today = {v_today:.5f} (r25: {v25[-1]:.5f}, "
      f"r21: 0.1229) in (c/H0)^4")

    targets_z = np.array([1.0e9, 1100.0, 10.0, 1.0, 0.0])
    epochs = np.unique(np.concatenate([np.geomspace(1e-12, 1.0, 120), 1.0 / (1.0 + targets_z)]))
    idx = np.searchsorted(a, epochs)
    v_exact = np.zeros(len(epochs))
    n_med = np.zeros(len(epochs))
    for k, i in enumerate(idx):
        v_exact[k], n_med[k] = cone_volume_and_median_patches(min(i, len(a) - 1), lna, a, H, eta)
    z_ep = 1.0 / epochs - 1.0
    lna25 = np.log(a25)
    sup_coded = np.interp(np.log(epochs), lna25, sup25)
    sup_obs = 1.0 / np.sqrt(n_med)

    needed = 1.0 / 43.0
    p(f"    needed at BBN (E29 design target): suppression <= 1/43 = {needed:.4f}")
    p(f"    {'epoch':<22s} {'as coded 1/sqrt(N)':>19s} {'observer at epoch':>18s} {'N_median':>9s} {'N_horizon':>10s}")
    rows = []
    for name, zt in (("BBN, z = 1e9", 1.0e9), ("recombination, z = 1100", 1100.0), ("z = 10", 10.0),
                     ("z = 1", 1.0), ("today, z = 0", 0.0)):
        k = int(np.argmin(np.abs(z_ep - zt)))
        n_hor = 1.0 + 4.0 * (np.interp(math.log(epochs[k]), lna, eta) * epochs[k] * hubble(epochs[k])) ** 2
        rows.append((name, sup_coded[k], sup_obs[k], n_med[k]))
        p(f"    {name:<22s} {sup_coded[k]:19.3e} {sup_obs[k]:18.3f} {n_med[k]:9.1f} {n_hor:10.1f}")
    p("    'observer at epoch' = 1/sqrt(N_median), N_median = volume-weighted median patch count across the observer's own")
    p("    cone; N_horizon = 1 + 4 (eta a H)^2 at the observer's particle horizon.  E41 gives the exact values 5 (radiation era,")
    p("    eta a H = 1) and 17 (pure matter era, eta a H = 2); the row z = 1e9 reproduces 5, the rows z = 1100 and 10 approach")
    p("    17, and the count grows as the cosmological constant takes over (about 41 today).  Either way it is O(1-50), never 1e15.")
    bbn_coded, bbn_obs = rows[0][1], rows[0][2]

    # ------------------------------------------------------------------------------------------------------
    p("\nA3. Raw (white-noise) |Omega_Lambda| at BBN.  r25 line 88 floors the cone volume: V = max(1e-25, V).")
    z25 = 1.0 / a25 - 1.0
    i25 = len(a25) - 1
    a_obs25 = 3.0 * OL * math.sqrt(v25[i25])
    g_r25 = a_obs25 / (3.0 * H25 ** 2 * np.sqrt(v25))
    a_obs_ex = 3.0 * OL * math.sqrt(v_today)
    k_bbn = int(np.argmin(np.abs(z_ep - 1.0e9)))
    g_ex_bbn = a_obs_ex / (3.0 * hubble(epochs[k_bbn]) ** 2 * math.sqrt(v_exact[k_bbn]))
    j_bbn = int(np.argmin(np.abs(z25 - 1.0e9)))
    v_ratio = v25[:: 1] / np.exp(np.interp(lna25, np.log(epochs), np.log(v_exact)))
    bad = np.where(np.abs(v_ratio - 1.0) > 0.10)[0]
    z_first_bad = z25[bad[-1]] if len(bad) else float("nan")      # lowest redshift where r25's V is off by > 10 %
    p(f"    z = 1e9: exact cone volume {v_exact[k_bbn]:.3e}, r25 uses {v25[j_bbn]:.3e} (the floor)")
    p(f"    raw rms |Omega_Lambda| at BBN: exact {g_ex_bbn:.2f} (r21 and E29: 1.96);  r25 prints {g_r25[j_bbn]:.4f}")
    p(f"    r25's volume is off by more than 10 % for every z above {z_first_bad:.1e}")
    p(f"    => the headline 'filtered |Omega_Lambda| = 1.4e-28 at BBN' is an artefact. With the exact volume the same")
    p(f"       kernel gives {g_ex_bbn * rows[0][1]:.1e}: still 'passes', but only because of the frame problem in A2.")

    # ------------------------------------------------------------------------------------------------------
    p("\nA4. Equation of state and dark-energy density of r25's rms envelope (what r25 plots against DESI).")
    sig25 = g_r25 * sup25
    rho25 = H25 ** 2 * sig25
    w25 = -1.0 - (1.0 / 3.0) * np.gradient(np.log(rho25), np.log(a25))
    w0_r25 = float(w25[i25])
    j1 = int(np.argmin(np.abs(z25 - 1.0)))
    rho_ratio_r25 = float(rho25[j1] / rho25[i25])
    p(f"    r25 envelope: w0 = {w0_r25:.3f}  (r25 prints -0.343)   rho_DE(z=1) / rho_DE(0) = {rho_ratio_r25:.2f}")
    desi_ratio = []
    for name, (w0, dw0, wa, dwa) in r25.DESI.items():
        ratio = 2.0 ** (3.0 * (1.0 + w0 + wa)) * math.exp(-3.0 * wa * 0.5)      # CPL at z = 1
        desi_ratio.append(ratio)
        p(f"    {name:<22s} w0 = {w0:+.3f} +- {dw0:.3f}  -> w0 is {abs(w0_r25 - w0) / dw0:.1f} sigma from r25's envelope;"
          f" CPL best fit gives rho_DE(z=1)/rho_DE(0) = {ratio:.2f}")
    p("    r25's text says 'produces w0 ~ -1, consistent with Planck 2018 and DESI DR2' (line 190, a fixed string).")
    p("    No history is evolved at late times in r25: the 100,000 'histories' draw independent Gaussians at three epochs.")

    # ======================================================================================================
    p.section("B. r26 (R16): the complete Standard Model ledger")
    # ------------------------------------------------------------------------------------------------------
    n_eff_of_r = np.array([r26.sm_species_ledger(w_D_val=w, w_V_val=2.0)["n_eff"] for w in WD_GRID])
    n_eff_1 = float(np.interp(1.0, R_GRID, n_eff_of_r))
    per_kappa = 2.0 * math.pi / (r26.A_OBS * r26.ETA_S)         # N_needed = per_kappa * kappa
    kappa_solved = n_eff_1 / per_kappa
    kappa_gm = math.sqrt(0.5 * 1.0)
    p(f"B1. N_eff(r = 1) = {n_eff_1:.1f};  N_needed = {per_kappa:.1f} x kappa.  r26 line 205 SOLVES kappa = N_eff / {per_kappa:.1f}")
    p(f"    = {kappa_solved:.4f}, then reports 'residual 0.0 %'.  The geometric mean of 0.5 and 1.0 is {kappa_gm:.4f}, not 0.65.")
    ratios = []
    for label, kap in (("kappa = 0.5", 0.5), (f"kappa = {kappa_solved:.3f} (solved)", kappa_solved),
                       (f"kappa = {kappa_gm:.3f} (geometric mean)", kappa_gm), ("kappa = 1.0", 1.0)):
        ratios.append((label, n_eff_1 / (per_kappa * kap)))
        p(f"    {label:<34s} N_needed = {per_kappa * kap:6.1f}   N_eff / N_needed = {n_eff_1 / (per_kappa * kap):.3f}")
    p("    => agreement at the tens-of-percent level for conventional kappa; 'exact' only where kappa is the unknown solved for.")

    p("\nB2. The Wilson regulator r alone moves the fermion weight, hence N_eff, by a large factor:")
    for r_val, n_val in zip(R_GRID, n_eff_of_r):
        inside = 180.2 <= n_val <= 360.4
        p(f"    r = {r_val:4.2f}: N_eff = {n_val:6.1f}  {'inside' if inside else 'outside'} the band [180.2, 360.4]")
    r_hi = float(np.interp(180.2, n_eff_of_r[::-1], R_GRID[::-1]))
    r_lo = float(np.interp(360.4, n_eff_of_r[::-1], R_GRID[::-1]))
    frac = math.log(r_hi / r_lo) / math.log(R_GRID[-1] / R_GRID[0])
    span = n_eff_of_r.max() / n_eff_of_r.min()
    p(f"    N_eff spans a factor {span:.1f} over r = 0.5 ... 4; the band (width factor 2 from kappa) covers r = {r_lo:.2f} ... {r_hi:.2f},")
    p(f"    i.e. {100 * frac:.0f} % of that range on a log scale; of the four values scanned in r22 (0.5, 1, 2, 4) one lands inside.")
    p("    The edge-mode entropy computed at r26 lines 84-103 and 153-155 is never passed to sm_species_ledger(): the")
    p("    ledger uses 'a gauge boson = 2 real scalars' only (w_V = 2), so the Donnelly-Wall part does not enter the 233.4.")

    p("\nB3. Cell size: E35 says 4.75 l_P 'agrees with the independent Sakharov (4.2) and Bekenstein-Hawking (5.9)'.")
    cell = {kap: math.sqrt(8.0 * math.pi * kap / r26.A_OBS) for kap in (0.5, kappa_solved, 1.0)}
    p(f"    4.2 and 5.9 are the kappa = 0.5 and kappa = 1 ends of the Lambda relation itself: {cell[0.5]:.2f}, {cell[1.0]:.2f} l_P;")
    p(f"    the solved kappa gives {cell[kappa_solved]:.2f}.  r13 / r14 give cell = c * sqrt(N) l_P, which at N_eff = {n_eff_1:.1f} is:")
    for label, coef in CELL_PER_SQRT_N:
        p(f"      {label:<34s} c = {coef:.3f}  ->  {coef * math.sqrt(n_eff_1):.2f} l_P")
    p("    Comparing those with the Lambda-derived cell size is the same equation as N_eff against N_needed (B1), written in")
    p("    other units: it is not a second, independent test.")
    p("    (The physics of the ledger itself is in E39 / r29: the quantum weight of a vector boson is 1.03 scalars, not 2, and a")
    p("    classical flux term adds 50-100; and in E40 / r30: other lattice fermions, a range of x18.  The checks above are of")
    p("    r26 as written.)")

    # ======================================================================================================
    p.section("C. r28 (R17): neutral Hopfion dark matter")
    # ------------------------------------------------------------------------------------------------------
    m_sol = r28.RATIO_OBS * r28.M_PROTON_GEV
    f_gev, r_cm, sig_pi, s_over_m_pi = r28.soliton_properties(m_sol, r28.E_SKYRME)
    s_over_m_4pi = 4.0 * s_over_m_pi
    p(f"C1. r28 line 89: M_sol = RATIO_OBS * m_p = {r28.RATIO_OBS:.4f} * {r28.M_PROTON_GEV:.4f} = {m_sol:.4f} GeV.  The 'predicted'")
    p("    mass is the observed Omega_c / Omega_b restated, under the assumption n_sol = n_b (asymmetric-dark-matter")
    p("    reasoning, Nussinov 1985; Kaplan, Luty & Zurek 2009).  Then F = M / 312, R = hbar c / F: nothing independent.")
    p(f"    F_sub = {f_gev * 1e3:.2f} MeV, R_sol = {r_cm * 1e13:.2f} fm.")
    p(f"\nC2. Cross section.  r28 line 53 computes sigma = pi R^2 = {sig_pi:.3e} cm^2 -> sigma/M = {s_over_m_pi:.3f} cm^2/g.")
    p(f"    E38 states 'sigma = 4 pi R^2' (the number 4.660e-24 it quotes is pi R^2).  With 4 pi R^2: sigma/M = {s_over_m_4pi:.3f} cm^2/g,")
    p(f"    above the 1.0 cm^2/g limit that E38 itself uses (BULLET_CLUSTER_MAX, r28 line 40).  For two hard spheres of radius R the")
    p("    classical cross section is 4 pi R^2; pi R^2 is a point particle on one sphere.")
    p("    Not computed: sigma_SI = 1e-49 cm^2 is a typed number (r28 line 210), the exclusion curve is a hand-drawn function")
    p("    (line 201) and disagrees with LZ_LIMIT_5GEV in the same file.")
    p("    (Merging-cluster analyses quote limits nearer 0.5 cm^2/g, e.g. Harvey et al. 2015; from memory, not re-checked.)")

    p("\nC3. What the 'sweet spot' needs.  sigma/M scales as M^-3 at fixed form factor, so it is set by the assumption n_sol / n_b:")
    p(f"    {'n_sol / n_b':>12s} {'M (GeV)':>9s} {'pi R^2':>10s} {'4 pi R^2':>10s}   (cm^2/g; band 0.1 - 1.0)")
    for ratio_n in (0.5, 1.0, 2.0):
        mass = m_sol / ratio_n
        _, _, _, s_pi = r28.soliton_properties(mass, r28.E_SKYRME)
        p(f"    {ratio_n:12.1f} {mass:9.2f} {s_pi:10.3f} {4 * s_pi:10.3f}")

    def window(s0):
        """Soliton mass range for which sigma/M = s0 (M / m_sol)^-3 lies in [0.1, 1.0]."""
        return m_sol * (s0 / 1.0) ** (1 / 3), m_sol * (s0 / 0.1) ** (1 / 3)

    lo_pi, hi_pi = window(s_over_m_pi)
    lo_4, hi_4 = window(s_over_m_4pi)
    p(f"    band reached for M in [{lo_pi:.1f}, {hi_pi:.1f}] GeV with pi R^2 (n_sol / n_b in [{m_sol / hi_pi:.2f}, {m_sol / lo_pi:.2f}]) and")
    p(f"    for M in [{lo_4:.1f}, {hi_4:.1f}] GeV with 4 pi R^2 (n_sol / n_b in [{m_sol / hi_4:.2f}, {m_sol / lo_4:.2f}]): n_sol = n_b falls")
    p(f"    {'inside' if lo_4 <= m_sol <= hi_4 else 'outside'} the window for the convention E38 states.")
    p("    Neither the 312 F/e energy coefficient nor the Hopfion size is computed in this repository, and the F = 16 MeV scale")
    p("    is unrelated to the Planck-scale causal-set substrate of v2.3 (cells of ~5 l_P).")

    p("\nC4. Scaling with the Skyrme coupling e at fixed mass.  r28 uses F = M e / 312 and R = hbar c / (e F) = 312 hbar c / (e^2 M),")
    p("    so R goes as e^-2 and sigma/M as e^-4.  E41 and the README row state e^-2.")
    base = r28.soliton_properties(m_sol, 1.0)[3]
    e_rows = []
    for e_val in (0.5, 0.7, 1.0, 1.4, 2.0):
        _, r_e, _, s_e = r28.soliton_properties(m_sol, e_val)
        e_rows.append((e_val, s_e))
        p(f"    e = {e_val:4.2f}: R = {r_e * 1e13:6.2f} fm, sigma/M = {s_e:7.3f} (pi R^2) or {4 * s_e:7.3f} (4 pi R^2) cm^2/g;"
          f"  ratio to e = 1: {s_e / base:6.3f}  (e^-4 = {e_val ** -4:6.3f}, e^-2 = {e_val ** -2:6.3f})")
    p("    Under either cross-section convention the value at e = 1 is not 'safely inside' a band: a factor 2 in e moves it by 16.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("R15 / r25: patch averaging reduces Lambda noise",
         f"NOT SUPPORTED: Poisson patches add back to 1.00 (not 1/sqrt(K)); as coded {bbn_coded:.1e} at BBN is an "
         f"artefact of measuring from today; for an observer at BBN {bbn_obs:.2f} (needed <= {needed:.3f})"),
        ("R15 / r25: BBN |Omega_Lambda| ~ 1e-28",
         f"ARTEFACT of the volume floor: exact raw value {g_ex_bbn:.2f}, r25 prints {g_r25[j_bbn]:.4f}"),
        ("R15 / r25: steady dark energy, w0 ~ -1, DESI-consistent",
         f"CONTRADICTED by its own output: w0 = {w0_r25:.2f}; rho_DE(z=1)/rho_DE(0) = {rho_ratio_r25:.1f} against "
         f"{min(desi_ratio):.2f}-{max(desi_ratio):.2f} for DESI fits"),
        ("R16 / r26: SM N_eff = 233.4 matches Lambda with 0.0 % residual, zero free parameters",
         f"IDENTITY: kappa = {kappa_solved:.3f} is solved from N_eff; N_eff / N_needed is {ratios[0][1]:.2f} to {ratios[3][1]:.2f} "
         f"across kappa = 0.5 ... 1; the regulator moves N_eff by x{span:.1f}"),
        ("R16 / r26: cell size agrees with independent Sakharov and BH values",
         f"SAME EQUATION, relabelled: 4.2 and 5.9 are the kappa ends ({cell[0.5]:.2f}, {cell[1.0]:.2f}) of the Lambda relation"),
        ("R17 / r28: M = 5.06 GeV 'derived' from n_sol = n_b",
         f"RESTATEMENT of the observed ratio ({r28.RATIO_OBS:.3f} m_p); asymmetric-dark-matter reasoning, not new"),
        ("R17 / r28: sigma / M = 0.517 passes the Bullet Cluster limit",
         f"CONVENTION-DEPENDENT: {s_over_m_pi:.3f} with pi R^2 (code), {s_over_m_4pi:.3f} with 4 pi R^2 (E38 text) against a limit of 1.0"),
        ("E41 / README on r28: sigma / M scales as e^-2, 0.517 uses 4 pi R^2",
         f"CORRECTED: the code uses pi R^2 and scales as e^-4 (x{e_rows[0][1] / base:.0f} at e = 0.5, x{e_rows[4][1] / base:.3f} at e = 2)"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<84s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 9.4))

    ax = axs[0, 0]
    ks = np.array([d[0] for d in demo])
    ax.plot(ks, 1.0 / np.sqrt(ks), color=S2, lw=2.0)
    ax.errorbar(ks, [d[1] for d in demo], yerr=[d[2] for d in demo], fmt="o", color=S1, ms=6, capsize=3)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.1)
    ax.set(xscale="log", yscale="log", ylim=(0.008, 2.5), xlabel="number of independent causal patches K",
           ylabel="noise of the total, in units of the unsplit value",
           title="Splitting Poisson counts into K patches leaves the noise unchanged")
    ax.text(1.4, 1.22, "simulated: independent Poisson patches (stays at 1)", fontsize=9, color=S1)
    ax.text(3.0, 0.045, "r25's rule: noise ÷ √K", fontsize=9, color=S2, rotation=-27)

    ax = axs[0, 1]
    onep = 1.0 + z_ep
    ax.plot(onep, sup_coded, color=S1, lw=2.0, label="as coded: distance from the epoch to today")
    ax.plot(onep, sup_obs, color=S2, lw=2.0, label="observer at the epoch (median patch count)")
    ax.axhline(needed, color=MUTED, ls="--", lw=1.1)
    ax.set(xscale="log", yscale="log", xlim=(1.0, 1e10), ylim=(3e-9, 2.0), xlabel="1 + z",
           ylabel="noise suppression factor 1/√N_patches",
           title="Patch suppression: r25 as coded vs an observer living at that epoch")
    ax.text(3e3, 0.034, "needed at BBN: ≤ 0.023 (dashed)", fontsize=9, color=INK_2)
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[1, 0]
    labels = ["κ = 0.5", f"κ = {kappa_solved:.3f}\n(solved for)", f"κ = {kappa_gm:.3f}\n(geometric mean)", "κ = 1.0"]
    vals = [r[1] for r in ratios]
    bars = ax.bar(range(4), vals, color=[S1, S3, S1, S1], width=0.62)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.1)
    for xpos, v in enumerate(vals):
        ax.text(xpos, v + 0.03, f"{v:.2f}", ha="center", fontsize=9.5, color=INK_2)
    ax.set_xticks(range(4), labels, fontsize=9)
    ax.set(ylim=(0, 1.6), ylabel="N_eff (Standard Model, r = 1) ÷ N_needed",
           title="r26: Standard Model N_eff ÷ N_needed for different κ conventions")
    ax.text(0.02, 1.47, f"regulator r alone moves N_eff by ×{span:.1f} (r = 0.5 … 4)", fontsize=9, color=INK_2)

    ax = axs[1, 1]
    m_grid = np.geomspace(2.0, 20.0, 200)
    s_grid = np.array([r28.soliton_properties(m, r28.E_SKYRME)[3] for m in m_grid])
    ax.axhspan(0.1, 1.0, color=S3, alpha=0.10, lw=0)
    ax.plot(m_grid, s_grid, color=S1, lw=2.0)
    ax.plot(m_grid, 4.0 * s_grid, color=S2, lw=2.0)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.1)
    ax.axvline(m_sol, color=MUTED, ls=":", lw=1.1)
    ax.plot([m_sol], [s_over_m_pi], "o", color=S1, ms=7)
    ax.plot([m_sol], [s_over_m_4pi], "o", color=S2, ms=7)
    ax.set(xscale="log", yscale="log", xlim=(2.0, 20.0), ylim=(0.01, 100.0), xlabel="soliton mass (GeV)",
           ylabel="σ / M  (cm² / g)",
           title="r28: σ/M at 5.06 GeV depends on the cross-section formula")
    ax.set_xticks([2, 3, 5, 10, 20], ["2", "3", "5", "10", "20"])
    ax.minorticks_off()
    ax.text(4.7, 0.30, f"{s_over_m_pi:.2f}: σ = πR² (the code)", fontsize=9, color=S1, ha="right")
    ax.text(5.5, s_over_m_4pi * 1.25, f"{s_over_m_4pi:.2f}: σ = 4πR² (E38 text)", fontsize=9, color=S2)
    ax.text(19.5, 1.15, "limit used in E38: 1.0", fontsize=9, color=INK_2, ha="right")
    ax.text(2.1, 0.12, "'sweet-spot' band 0.1–1", fontsize=9, color=S3)
    ax.text(m_sol * 1.03, 0.012, "n_sol = n_b", fontsize=9, color=INK_2)

    fig.tight_layout()
    save_fig(fig, NAME, "audit")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
