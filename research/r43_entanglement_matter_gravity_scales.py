"""
r43 - Entanglement, matter concentrations and gravity from the quantum to the cosmic scale  (LAB_NOTEBOOK.md entry E47, tests M1-M3)

Question (user): "also we need see how would they react and what about the quantum entanglement of the particles and matter concentrations and
gravity too from quantum to major real scale as well".

What E19 and E21 already did: the area-law entanglement coefficient of the substrate (eta = 0.0242 per face), G from it (Sakharov/Jacobson), the size of
the quantum correction to Newton's law, and the QGEM entangling phases.  This script adds three things the fluid-space programme can test:

  M1. The ladder.  For objects from an electron to the Hubble sphere: how quantum (Compton wavelength / size), how gravitationally compact (r_s / R), the
      self-gravity rate E_G / hbar, and how much of the Bekenstein-Hawking bound the medium's surface entanglement fills.  Arithmetic from constants.
  M2. Matter concentration and entanglement.  A matter lump = a local change of the medium's field Hamiltonian (here a mass bump of a lattice scalar field).
      Does the entanglement entropy of a region respond to it through the first law of entanglement  delta S = delta <K_A>  (K_A = -ln rho_A, the
      modular Hamiltonian), with the relative entropy delta<K> - delta S >= 0 as the second-order remainder?  Gaussian-state numerics, exact.
      (This is the lattice version of the step Jacobson's 'entanglement equilibrium' argument uses to turn matter into curvature.)
  M3. Stretching entangles.  The phonon pairs (k, -k) squeezed by the stretching of r37: exact mode integration gives the number of quanta, the entanglement
      entropy per pair, the entropy per Hubble volume, and its size against the horizon entropy.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, hbar, lP, mP, save_fig, style  # noqa: E402
from r37_expansion_and_structure import integrate_mode  # noqa: E402

NAME = "r43_entanglement_matter_gravity_scales"
H0_SI = 67.4e3 / 3.0857e22          # Planck 2018, 1/s
M_PL_REDUCED_GEV = 2.435e18


# ----------------------------------------------------------------------------------------------------------------------
# M2: Gaussian states of a lattice scalar field
# ----------------------------------------------------------------------------------------------------------------------
def ground_state_cov(n_sites, m2, bump):
    """Covariances of the ground state of H = (1/2) sum [pi^2 + (phi_{i+1} - phi_i)^2 + (m2 + bump_i) phi_i^2] on an open chain: X = K^-1/2 / 2, P = K^1/2 / 2."""
    k = np.zeros((n_sites, n_sites))
    for i in range(n_sites):
        k[i, i] = 2.0 + m2 + bump[i]
        if i + 1 < n_sites:
            k[i, i + 1] = k[i + 1, i] = -1.0
    w, v = np.linalg.eigh(k)
    root = (v * np.sqrt(w)) @ v.T
    inv_root = (v / np.sqrt(w)) @ v.T
    return 0.5 * inv_root, 0.5 * root


def sym_power(a, p):
    w, v = np.linalg.eigh(a)
    return (v * w ** p) @ v.T


def entropy_and_modular(x_a, p_a):
    """Entropy of the reduced Gaussian state and the matrices (A, B) of its modular Hamiltonian K = (1/2) phi^T A phi + (1/2) pi^T B pi + const."""
    xh = sym_power(x_a, 0.5)
    r = xh @ p_a @ xh
    nu2, o = np.linalg.eigh(r)
    nu = np.sqrt(np.maximum(nu2, 0.25 + 1e-14))
    eps = np.log((nu + 0.5) / (nu - 0.5))
    ent = float(np.sum((nu + 0.5) * np.log(nu + 0.5) - (nu - 0.5) * np.log(nu - 0.5)))
    xmh = sym_power(x_a, -0.5)
    f = (np.sqrt(nu)[:, None] * o.T) @ xmh                 # q~ = F phi
    g = ((1.0 / np.sqrt(nu))[:, None] * o.T) @ xh          # p~ = G pi
    a_mat = f.T @ np.diag(eps) @ f
    b_mat = g.T @ np.diag(eps) @ g
    return ent, a_mat, b_mat, nu, eps


def modular_expectation(a_mat, b_mat, x1, p1):
    return 0.5 * float(np.trace(a_mat @ x1) + np.trace(b_mat @ p1))


def pair_entropy(n):
    return (n + 1.0) * math.log(n + 1.0) - n * math.log(n) if n > 1e-12 else 0.0


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("M1. The ladder: from an electron to the Hubble sphere (arithmetic from constants)")
    # ------------------------------------------------------------------------------------------------------
    lp = lP()
    mp_kg = mP()
    m_h = c ** 3 / (2.0 * G0 * H0_SI)
    r_h = c / H0_SI
    rho = lambda m, dens: (3.0 * m / (4.0 * math.pi * dens)) ** (1.0 / 3.0)
    objects = [
        ("electron", 9.1093837e-31, hbar / (9.1093837e-31 * c)),          # radius taken as the reduced Compton wavelength
        ("proton", 1.67262192e-27, 0.84e-15),
        ("C60 molecule", 1.197e-24, 0.35e-9),
        ("10^-14 kg grain (QGEM scale)", 1.0e-14, rho(1.0e-14, 2200.0)),
        ("dust speck 10^-9 kg", 1.0e-9, rho(1.0e-9, 2000.0)),
        ("human 70 kg", 70.0, rho(70.0, 1000.0)),
        ("Earth", 5.972e24, 6.371e6),
        ("Sun", 1.989e30, 6.957e8),
        ("neutron star 1.4 Msun", 2.8e30, 1.2e4),
        ("Hubble sphere (c / H0)", m_h, r_h),
    ]
    p(f"    Constants: l_P = {lp:.3e} m, m_P = {mp_kg:.3e} kg, H0 = 67.4 km/s/Mpc  =>  c / H0 = {r_h:.2e} m, mass inside c^3/(2 G H0) = {m_h:.2e} kg.")
    p("    Compton = reduced Compton wavelength hbar/(M c);  compactness = 2 G M / (R c^2);  E_G/hbar = G M^2 / (R hbar) is both the self-gravity rate")
    p("    (Diosi-Penrose decoherence time = hbar/E_G) and the rate at which two copies of the object at distance ~R would gain gravitational phase;")
    p("    S_surf = pi R^2 / l_P^2 (nats) is the medium's entanglement across the surface (area law with Bekenstein-Hawking coefficient, E19); S_BH = pi r_s^2 / l_P^2.")
    p(f"    {'object':>30s} {'M (kg)':>10s} {'R (m)':>10s} {'Compton/R':>10s} {'compactness':>12s} {'E_G/hbar (1/s)':>15s} {'S_surf':>9s} {'S_surf/S_BH':>12s} {'(l_P/R)^2':>10s}")
    ladder = []
    for name, m, r in objects:
        rs = 2.0 * G0 * m / c ** 2
        compact = rs / r
        eg_rate = G0 * m ** 2 / (r * hbar)
        s_surf = math.pi * r ** 2 / lp ** 2
        s_bh = math.pi * rs ** 2 / lp ** 2
        ladder.append((name, m, r, hbar / (m * c) / r, compact, eg_rate, s_surf, s_surf / s_bh, (lp / r) ** 2))
        p(f"    {name:>30s} {m:10.2e} {r:10.2e} {hbar / (m * c) / r:10.1e} {compact:12.1e} {eg_rate:15.1e} {s_surf:9.1e} {s_surf / s_bh:12.1e} {(lp / r) ** 2:10.1e}")
    p("    Reading:")
    p("      * Compton/R is 1 for the electron (its size is taken to be its reduced Compton wavelength), 0.25 for the proton and below 1e-9 for everything larger: for")
    p("        every larger object the quantum character lives in superposition and entanglement of states, not in the size of the object.")
    p("      * Compactness stays below 1e-8 until a neutron star (0.35) -- gravity is a weak-field theory everywhere we measure it; the Hubble sphere sits exactly at 1 by")
    p("        construction (M = c^3/(2 G H0)): the observable universe is at its own Schwarzschild threshold, a standard identity, not a coincidence of this programme.")
    p("      * The medium's entanglement across an object's surface exceeds the Bekenstein-Hawking entropy of the same mass by (R/r_s)^2 = 1/compactness^2: the area-law entropy is")
    p("        not 'used up' by ordinary matter; only black holes (and the Hubble sphere) saturate it.  Matter concentration enters only through how close R is to r_s.")
    p(f"      * E_G/hbar is {ladder[3][5]:.0f} /s for the QGEM-scale grain (self-gravity time {1e3 / ladder[3][5]:.0f} ms, of the order of the experiment's duration), 1e10 /s for a dust speck")
    p("        and 1e28 /s for a person: the scale where gravity-mediated entanglement (E21: 0.03-2.8 rad) becomes visible.  If quantum states collapsed by self-gravity")
    p("        (Diosi-Penrose; the parameter-free version was excluded by Donadi et al. 2021, E21), heavier objects could not keep them for longer than hbar/E_G.")
    p(f"      * The quantum correction to Newton's law at the surface, (41/10 pi)(l_P/R)^2 (E21), is {41 / (10 * math.pi) * ladder[0][8]:.0e} for the electron's Compton radius and falls to")
    p(f"        {41 / (10 * math.pi) * ladder[-1][8]:.0e} at the Hubble radius.")

    # ======================================================================================================
    p.section("M2. Matter concentration and entanglement: the first law of entanglement on a lattice")
    # ------------------------------------------------------------------------------------------------------
    n_sites, m2, sigma = 200, 0.01, 2.0
    a_lo, a_hi = 96, 104
    region = slice(a_lo, a_hi)
    x0, p0 = ground_state_cov(n_sites, m2, np.zeros(n_sites))
    s0, a_mat, b_mat, nu0, eps0 = entropy_and_modular(x0[region, region], p0[region, region])
    check_s = float(np.sum(eps0 * nu0 - np.log(2.0 * np.sinh(eps0 / 2.0))))
    check_k = modular_expectation(a_mat, b_mat, x0[region, region], p0[region, region])
    p(f"    Lattice scalar, {n_sites} sites, mass^2 = {m2}, region A = sites {a_lo}..{a_hi - 1} ({a_hi - a_lo} sites).  Vacuum entropy S_A = {s0:.5f} nats.")
    p(f"    Self-checks of the modular Hamiltonian: S = <K> + ln Z  (thermodynamic identity): {s0:.5f} vs {check_s:.5f};  <K0>_vacuum = sum eps nu = {float(np.sum(eps0 * nu0)):.5f} vs trace formula {check_k:.5f}.")
    p(f"    (Region of {a_hi - a_lo} sites, correlation length 1/m = {1 / math.sqrt(m2):.0f} sites.  A first attempt with a 40-site region at m^2 = 0.25 failed: the deep-interior entanglement-spectrum")
    p("    values nu - 1/2 fall below double precision (1e-16) there, so the modular Hamiltonian is numerical noise; all nu - 1/2 here exceed 1e-12.)")
    p("    Matter lump: mass^2 raised by lambda exp(-(i - i0)^2 / (2 sigma^2)), sigma = 2 sites (a localized matter concentration), lump at the centre of A.")
    centre = (a_lo + a_hi) // 2
    p(f"    {'lambda':>8s} {'delta S':>13s} {'delta <K0>':>13s} {'relative entropy':>17s} {'rel / lambda^2':>15s}")
    lams = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
    rows = []
    for lam in lams:
        bump = lam * np.exp(-0.5 * ((np.arange(n_sites) - centre) / sigma) ** 2)
        x1, p1 = ground_state_cov(n_sites, m2, bump)
        xa, pa = x1[region, region], p1[region, region]
        ent1, _, _, _, _ = entropy_and_modular(xa, pa)
        dk = modular_expectation(a_mat, b_mat, xa, pa) - check_k
        ds = ent1 - s0
        rows.append((lam, ds, dk, dk - ds))
        p(f"    {lam:8.0e} {ds:13.3e} {dk:13.3e} {dk - ds:17.3e} {(dk - ds) / lam ** 2:15.3e}")
    lam_arr = np.array([r[0] for r in rows])
    slope_s = np.polyfit(np.log(lam_arr[:5]), np.log(np.abs([r[1] for r in rows[:5]])), 1)[0]
    slope_rel = np.polyfit(np.log(lam_arr[:5]), np.log(np.abs([r[3] for r in rows[:5]])), 1)[0]
    ratio_small = rows[0][1] / rows[0][2]
    slope_k = np.polyfit(np.log(lam_arr[:5]), np.log(np.abs([r[2] for r in rows[:5]])), 1)[0]
    p(f"    => at small lambda delta S and delta <K0> agree (ratio {ratio_small:.4f} at lambda = {lam_arr[0]}); they go as lambda^{slope_s:.2f} and lambda^{slope_k:.2f} (first order); the relative entropy delta<K0> - delta S ~ lambda^{slope_rel:.2f}")
    p("       (second order) and is never negative (positivity: the vacuum is the entropy-maximising state for given modular energy).")
    p("    Where the lump sits (lambda = 0.01): delta S of region A against the lump position i0:")
    pos = np.arange(60, 142, 4)
    ds_pos, dk_pos = [], []
    for i0 in pos:
        bump = 0.01 * np.exp(-0.5 * ((np.arange(n_sites) - i0) / sigma) ** 2)
        x1, p1 = ground_state_cov(n_sites, m2, bump)
        xa, pa = x1[region, region], p1[region, region]
        ds_pos.append(entropy_and_modular(xa, pa)[0] - s0)
        dk_pos.append(modular_expectation(a_mat, b_mat, xa, pa) - check_k)
    ds_pos, dk_pos = np.array(ds_pos), np.array(dk_pos)
    centre_i = (a_lo + a_hi) // 2
    in_a = int(np.argmin(np.abs(pos - centre_i)))
    far = np.abs(pos - centre_i) >= 40
    p(f"      lump at the centre of A: delta S = {ds_pos[in_a]:+.2e};  lump 20 sites away: {ds_pos[int(np.argmin(np.abs(pos - (centre_i + 20))))]:+.2e};  lump 40 or more sites away: |delta S| <= {np.max(np.abs(ds_pos[far])):.1e}.")
    p("      The sign and size of the effect: a heavier local field is less correlated, so matter inside or beside the region changes its entanglement; the response dies off over a")
    p(f"      few correlation lengths (1/m = {1 / math.sqrt(m2):.0f} sites): it is local, which is what lets it behave like a field equation.")
    p("    Meaning for the fluid picture: a matter concentration is a local change of the medium's Hamiltonian; the entanglement of any region changes by delta<K> to first")
    p("    order.  For a region bounded by a Rindler/Unruh horizon K is the boost energy and delta S = delta<K> is the Clausius relation  delta S = delta Q / T  that Jacobson (1995)")
    p("    turns into Einstein's equation.  What is verified here is only the lattice first law in a free field: not Einstein's equation.")

    # ======================================================================================================
    p.section("M3. Stretching entangles: the phonon pairs of the expanding medium (r37 mode integration)")
    # ------------------------------------------------------------------------------------------------------
    p("In de Sitter the phonon pair (k, -k) is a two-mode squeezed state.  With u'' + [1 + (lambda^2/2) tau^2 - 2/tau^2] u = 0 (tau = -c k eta, lambda = H xi/c, r37) and the")
    p("adiabatic vacuum at early times, the number of quanta in each mode at tau is  n = (|u'|^2 + |u|^2)/2 - 1/2  and the entanglement entropy of the pair is")
    p("S = (n+1) ln(n+1) - n ln n.  For lambda = 0 the exact solution gives n = 1 / (4 tau^4).")
    taus = [3.0, 1.0, 0.3, 0.1, 0.03, 0.01]
    rows3 = []
    for lam in (0.0, 0.3):
        tau_i = 400.0 if lam == 0 else max(200.0, 40.0 / lam)
        sol = integrate_mode((lambda t, lam=lam: 1.0 + 0.5 * lam ** 2 * t ** 2 - 2.0 / t ** 2), tau_i, 0.01)
        for t in taus:
            y = sol.sol(t)
            u2 = y[0] ** 2 + y[2] ** 2
            up2 = y[1] ** 2 + y[3] ** 2
            n = 0.5 * (u2 + up2) - 0.5
            rows3.append((lam, t, n, pair_entropy(n)))
    p(f"    {'lambda':>7s} {'tau':>6s} {'e-folds since exit':>19s} {'n (numerical)':>14s} {'1/(4 tau^4)':>12s} {'S (nats)':>10s}")
    for lam, t, n, s in rows3:
        p(f"    {lam:7.1f} {t:6.2f} {math.log(1.0 / t):19.2f} {n:14.4e} {1.0 / (4 * t ** 4):12.4e} {s:10.3f}")
    r0 = [r for r in rows3 if r[0] == 0.0 and r[1] <= 0.3]
    s_slope = np.polyfit([math.log(1 / r[1]) for r in r0], [r[3] for r in r0], 1)[0]
    worst = max(abs(r[2] * 4 * r[1] ** 4 - 1.0) for r in rows3 if r[0] == 0.0)
    gr = [r for r in rows3 if r[0] == 0.3 and r[1] <= 0.3]
    s_slope_g = np.polyfit([math.log(1 / r[1]) for r in gr], [r[3] for r in gr], 1)[0]
    p(f"    => lambda = 0: n agrees with 1/(4 tau^4) to {worst:.0e}; for tau < 0.3 the pair entropy grows by {s_slope:.2f} nats per e-fold after horizon exit (a squeezing")
    p(f"       parameter r = 2 ln(aH/k), S = 2 r); with the medium's graininess (lambda = 0.3) the same slope, {s_slope_g:.2f}: the entanglement is not an artefact of the continuum.")
    # entropy per Hubble volume
    taus_f = np.geomspace(1e-4, 200.0, 200001)
    n_f = 1.0 / (4.0 * taus_f ** 4)
    s_f = np.array([pair_entropy(v) for v in n_f])
    integral = float(np.trapezoid(taus_f ** 2 * s_f, taus_f))
    s_hubble = integral / (3.0 * math.pi)
    p(f"    Entropy of all pairs per Hubble volume (de Sitter, exact n = 1/(4 tau^4); pairs counted once): S_H = I / (3 pi), I = int tau^2 S(n(tau)) d tau = {integral:.3f}  =>  S_H = {s_hubble:.3f} nats,")
    p("    independent of H: a constant, small amount of entanglement per Hubble volume, produced and diluted continuously.")
    p(f"    Compare with the horizon's own area-law entropy S_dS = 8 pi^2 (M_Pl/H)^2  (M_Pl = reduced Planck mass):")
    p(f"    {'epoch':>34s} {'H (GeV)':>10s} {'S_dS':>10s} {'S_H / S_dS':>11s}")
    h_today = H0_SI * hbar / 1.602176634e-10          # GeV
    ent_rows = []
    for name, h_gev in (("inflation (r39 plateau, r37)", 1.0e13), ("end of the quench (r35 scale, H ~ 1e17)", 1.0e17), ("dark-energy era (H0)", h_today)):
        s_ds = 8.0 * math.pi ** 2 * (M_PL_REDUCED_GEV / h_gev) ** 2
        ent_rows.append((name, h_gev, s_ds, s_hubble / s_ds))
        p(f"    {name:>34s} {h_gev:10.1e} {s_ds:10.1e} {s_hubble / s_ds:11.1e}")
    p("    So the pairs made by stretching carry entanglement of order 0.1 nat per Hubble volume, while the horizon's area-law entanglement is 1e12 to 1e122 nats: the")
    p("    structure-seeding pairs are an exceedingly small part of the medium's entanglement.  The entanglement that matters for G and for horizon entropy is the")
    p("    short-distance one, E19, not the cosmological pairs.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("M1: where matter is quantum and where it is gravitating",
         f"Compton/R = 1 (electron, by definition), {ladder[1][3]:.2f} (proton), < {ladder[2][3] * 1.01:.0e} for everything larger; compactness {ladder[7][4]:.0e} (Sun), {ladder[8][4]:.2f} (neutron star), 1 (Hubble sphere)"),
        ("M1': ordinary matter saturates the medium's area-law entanglement",
         f"NO: S_surf / S_BH = 1/compactness^2: {ladder[3][7]:.0e} for the grain, {ladder[7][7]:.0e} for the Sun; only black holes reach 1"),
        ("M2: first law of entanglement for a matter lump in the medium's field",
         f"{'CONFIRMED' if abs(ratio_small - 1) < 0.01 else 'NOT CONFIRMED'} on the lattice: delta S / delta<K> = {ratio_small:.4f} at the smallest lambda; relative entropy ~ lambda^{slope_rel:.2f}, positive; lump effect local"),
        ("M2': this proves gravity from entanglement",
         "NO: it checks the lattice first law in a free field; the step to Einstein's equation needs the Rindler/Unruh structure (Jacobson 1995) and is not tested here"),
        ("M3: stretching entangles the medium's phonon pairs",
         f"CONFIRMED: n = 1/(4 tau^4) to {worst:.0e}, entropy grows {s_slope:.1f} nats per e-fold ({s_slope_g:.1f} with graininess); S_H = {s_hubble:.2f} nats per Hubble volume"),
        ("M3': these pairs account for the horizon entropy",
         f"NO: S_H / S_dS = {ent_rows[0][3]:.0e} (inflation) to {ent_rows[-1][3]:.0e} (today)"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(13.2, 10.4))

    ax = axs[0, 0]
    rr = np.geomspace(1e-18, 1e28, 100)
    ax.plot(np.log10(rr), np.log10(hbar / (c * rr)), color=MUTED, ls="--", lw=1.4, label="size = Compton wavelength (below: quantum)")
    ax.plot(np.log10(rr), np.log10(rr * c ** 2 / (2 * G0)), color=INK_2, ls=":", lw=1.6, label="size = 2GM/c² (above: black hole)")
    for (name, m, r, *_), col in zip(ladder, [S1] * 3 + [S2] * 4 + [S3] * 3):
        ax.plot(math.log10(r), math.log10(m), "o", color=col, ms=7)
    short = {"electron": "electron", "proton": "proton", "C60 molecule": "C60", "10^-14 kg grain (QGEM scale)": "grain (QGEM)", "dust speck 10^-9 kg": "dust",
             "human 70 kg": "human", "Earth": "Earth", "Sun": "Sun", "neutron star 1.4 Msun": "neutron star", "Hubble sphere (c / H0)": "Hubble sphere"}
    offs = {"electron": (8, -3), "proton": (-30, 7), "C60 molecule": (7, 4), "10^-14 kg grain (QGEM scale)": (7, -12), "dust speck 10^-9 kg": (-34, 6),
            "human 70 kg": (7, 4), "Earth": (8, -12), "Sun": (9, -3), "neutron star 1.4 Msun": (-82, 4), "Hubble sphere (c / H0)": (-100, -4)}
    for name, m, r, *_ in ladder:
        ax.annotate(short[name], (math.log10(r), math.log10(m)), textcoords="offset points", xytext=offs[name], fontsize=8.5, color=INK_2)
    ax.set(xlabel="log₁₀ size R (m)", ylabel="log₁₀ mass M (kg)", xlim=(-18, 28), ylim=(-40, 58),
           title="Objects between the quantum line and the black-hole line")
    ax.legend(loc="center right", fontsize=9)

    ax = axs[0, 1]
    ax.loglog(lam_arr, np.abs([r[1] for r in rows]), "o-", color=S1, ms=7, label="|δS| (change of entropy)")
    ax.loglog(lam_arr, np.abs([r[2] for r in rows]), "s", color=S2, ms=6, label="|δ⟨K₀⟩| (first law)")
    ax.loglog(lam_arr, np.abs(np.array([r[3] for r in rows])), "^-", color=S3, ms=7, label="relative entropy δ⟨K₀⟩ − δS")
    ax.loglog(lam_arr, abs(rows[-1][3]) * (lam_arr / lam_arr[-1]) ** 2, color=MUTED, ls=":", lw=1.4, label="∝ λ² (reference)")
    ax.set(xlabel="strength λ of the matter lump", ylabel="nats", title="First law of entanglement: δS = δ⟨K⟩ to first order")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[1, 0]
    ax.plot(pos, ds_pos, "o-", color=S1, ms=5)
    ax.axvspan(a_lo, a_hi, color=S3, alpha=0.18, lw=0)
    ax.axhline(0, color=MUTED, lw=1.0)
    ax.text(a_lo - 1, 0.0, "region A", fontsize=9, color=S3, va="bottom", ha="right")
    ax.set(xlabel="position of the lump (site)", ylabel="δS of region A (nats)", title="Entanglement responds to matter locally (λ = 0.01)")

    ax = axs[1, 1]
    for lam, col, lab in ((0.0, S1, "λ = 0 (no graininess)"), (0.3, S2, "λ = 0.3 (grainy medium)")):
        pts = [(math.log(1 / r[1]), r[3]) for r in rows3 if r[0] == lam]
        ax.plot(*zip(*pts), "o", color=col, ms=7, label=lab)
    ee = np.linspace(0, 4.8, 20)
    ax.plot(ee, 4.0 * ee - math.log(4.0) + 1.0, color=MUTED, ls="--", lw=1.4, label="S = 4 N − ln 4 + 1")
    ax.set(xlabel="e-folds since horizon exit, N = ln(1/τ)", ylabel="entanglement entropy of the pair (nats)",
           title="Each e-fold of stretching adds 4 nats to a phonon pair")
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "scales")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
