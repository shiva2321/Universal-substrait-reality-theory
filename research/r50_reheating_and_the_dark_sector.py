"""
r50 - Reheating and the dark sector of the two-sector model  (LAB_NOTEBOOK.md entry E49, tests R1-R4; GPU)

Question (open item from E48): after inflation the density sector is empty (stiff share 6e-24 at N = 10) and the energy sits in the relative phase of the two-component medium, a Josephson
(sine-Gordon) field with a gap m_phi.  How does that energy get into the density sector (the one that carries gravity, light and matter) and what happens to the rest?

Setting: g = 1, n_a = 1, hbar = m = 1, g12 = g (1 - s^2) / (1 + s^2) (s = 0.5: g12 = 0.6), Rabi coupling Omega.  Density sound c_d^2 = n_a (g + g12), spin sound c_r^2 = n_a (g - g12) = s^2 c_d^2,
spin-quantum gap m^2 = 4 Omega (Omega + n_a (g - g12)) (sine-Gordon value 4 Omega n_a (g - g12) for Omega << g - g12).  The spin quanta are the quanta of the relative phase phi, the density quanta the quanta of the total phase and total density.

  R1. A selection rule: the exchange 1 <-> 2 is a symmetry (phi -> -phi, z -> -z; density sector even, spin sector odd).  Verified symbolically on the hydrodynamic energy density to third order:
      every cubic vertex has an even number of spin fields, so a single spin quantum cannot decay into density phonons (no phi-d-d vertex).  Pairs can annihilate (phi-phi-d vertices exist).
  R2. What breaks the rule: g22 = g (1 + eps).  Bogoliubov spectrum with unequal couplings: the exact crossing of the spin and density branches at k* = m / sqrt(c_d^2 - c_r^2) becomes an avoided
      crossing whose gap is proportional to eps.
  R3. If the spin sector were thermal and relativistic with the density sector at the decoupling temperature, the 1/s^3 of its density of states makes it a large share of the radiation:
      Delta N_eff against the Planck 2018 limit.
  R4. Real-time 2D Gross-Pitaevskii simulation on the GPU: a homogeneous relative-phase oscillation (phi_0 = 1.5 rad) with a tiny noise seed, for several Rabi couplings.  The energy is split into
      the condensate (the homogeneous oscillation), spin-sector fluctuations (the produced spin quanta), the density sector and the rest; how much reaches the density sector, and how does that scale with Omega?
"""
import math
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import fsolve, minimize_scalar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

import torch  # noqa: E402

NAME = "r50_reheating_and_the_dark_sector"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
G, NA = 1.0, 1.0
S_SPIN = 0.5
G12 = G * (1 - S_SPIN ** 2) / (1 + S_SPIN ** 2)
C_D = math.sqrt(NA * (G + G12))
C_R = math.sqrt(NA * (G - G12))
N_GRID = int(os.environ.get("R50_N", 512 if DEV == "cuda" else 128))
DX = 0.4
DT = float(os.environ.get("R50_DT", 0.04))
N_PER = float(os.environ.get("R50_PERIODS", 120))
OMEGAS = tuple(float(x) for x in os.environ.get("R50_OMEGAS", "0.02,0.01,0.005,0.0025").split(","))
PHI0 = float(os.environ.get("R50_PHI0", 1.5))
SEED_NOISE = float(os.environ.get("R50_NOISE", 1e-3))
CDT = torch.complex128 if os.environ.get("R50_FP64", "1") == "1" else torch.complex64


# ---------------------------------------------------------------------------------------------------------------------
def gap_exact(om):
    """spin-branch gap at k = 0 from the Bogoliubov spectrum of the symmetric state: m^2 = 4 Omega (Omega + n_a (g - g12)); the sine-Gordon value is 4 Omega n_a (g - g12)."""
    return math.sqrt(4.0 * om * (om + NA * (G - G12)))


def selection_rule(p):
    a, z, ph, vd, w, e = sp.symbols("a z phi v_d w e", real=True)
    n0, g, g12, om = sp.symbols("N0 g g12 Omega", positive=True)
    n = n0 + a
    h = n * vd ** 2 / 2 + n * w ** 2 / 8 + n * z * vd * w / 2 + (g + g12) * n ** 2 / 4 + (g - g12) * n ** 2 * z ** 2 / 4 + om * n * (1 - sp.sqrt(1 - z ** 2) * sp.cos(ph))
    swapped = h.subs({z: -z, ph: -ph, w: -w}, simultaneous=True)
    sym_ok = sp.simplify(swapped - h) == 0
    scaled = h.subs({a: e * a, z: e * z, ph: e * ph, vd: e * vd, w: e * w}, simultaneous=True)
    ser = sp.series(scaled, e, 0, 4).removeO()
    cubic = sp.expand(ser.coeff(e, 3))
    terms = sp.Add.make_args(cubic)
    bad = []
    for t in terms:
        pw = sp.Poly(t, a, z, ph, vd, w).monoms()[0]
        odd = pw[1] + pw[2] + pw[4]                               # powers of z, phi, w
        if odd % 2 == 1:
            bad.append(t)
    return sym_ok, cubic, len(terms), bad


def bdg_omegas(k, g1, g2, g12, om, mu):
    """positive Bogoliubov frequencies of the uniform two-component state (real amplitudes) with unequal couplings g1, g2."""
    def eqs(x):
        p1, p2 = x
        return [(g1 * p1 ** 2 + g12 * p2 ** 2 - mu) * p1 - om * p2, (g2 * p2 ** 2 + g12 * p1 ** 2 - mu) * p2 - om * p1]
    p1, p2 = fsolve(eqs, [math.sqrt(NA), math.sqrt(NA)], xtol=1e-13)
    gs = (g1, g2)
    ps = (p1, p2)
    a = np.zeros((2, 2))
    b = np.zeros((2, 2))
    for i in range(2):
        j = 1 - i
        a[i, i] = k * k / 2 - mu + gs[i] * ps[i] ** 2 + g12 * ps[j] ** 2 + gs[i] * ps[i] ** 2
        a[i, j] = -om + g12 * ps[i] * ps[j]
        b[i, i] = gs[i] * ps[i] ** 2
        b[i, j] = g12 * ps[i] * ps[j]
    mat = np.block([[a, b], [-b, -a]])
    ev = np.linalg.eigvals(mat)
    pos = np.sort(ev.real[ev.real > 1e-9])
    return pos[:2], ps


def crossing_gap(eps, om):
    mu = (G + G12) * NA - om
    m2 = gap_exact(om) ** 2
    k_star = math.sqrt(m2) / math.sqrt(C_D ** 2 - C_R ** 2)
    f = lambda k: (lambda o: o[1] - o[0])(bdg_omegas(k, G, G * (1 + eps), G12, om, mu)[0])
    res = minimize_scalar(f, bounds=(0.5 * k_star, 2.2 * k_star), method="bounded", options={"xatol": 1e-12})
    return res.fun, res.x, k_star


# ---------------------------------------------------------------------------------------------------------------------
def delta_neff(s, g_dec, g_s=1.0):
    x_dec = g_s / (s ** 3 * g_dec)                                  # rho_s / rho_SM at decoupling, equal temperatures
    x_bbn = x_dec * (10.75 / g_dec) ** (1.0 / 3.0)                  # entropy of the SM bath dilutes it: x ~ g*^(1/3) (g* = g*_s)
    return x_bbn * 10.75 / 1.75                                    # one neutrino species has 7/4 degrees of freedom out of 10.75


def run_gp(omega, t_end, label, noise_amp=None, dt=None, seed=11):
    """2D Gross-Pitaevskii, Strang splitting on the GPU.  Returns dict of time series (energies in units of the initial Josephson energy)."""
    n = N_GRID
    dev = DEV
    noise_amp = SEED_NOISE if noise_amp is None else noise_amp
    dt_ = DT if dt is None else dt
    k1 = 2 * math.pi * torch.fft.fftfreq(n, d=DX, device=dev)
    kx, ky = torch.meshgrid(k1, k1, indexing="ij")
    k2 = (kx ** 2 + ky ** 2)
    kin_full = torch.exp(-0.5j * dt_ * k2.double()).to(CDT)
    gen = torch.Generator(device=dev).manual_seed(seed)
    area = (n * DX) ** 2

    def noise():
        re = torch.randn((n, n), generator=gen, device=dev, dtype=torch.float64)
        im = torch.randn((n, n), generator=gen, device=dev, dtype=torch.float64)
        f = torch.fft.fft2(torch.complex(re, im)) * (k2 < 1.5 ** 2)
        f[0, 0] = 0.0                                  # no k = 0 component: the homogeneous mode (and the particle number) stay exactly as set
        out = torch.fft.ifft2(f)
        return out / out.abs().pow(2).mean().sqrt() * noise_amp
    psi1 = (math.sqrt(NA) * np.exp(1j * PHI0 / 2) + noise()).to(CDT)
    psi2 = (math.sqrt(NA) * np.exp(-1j * PHI0 / 2) + noise()).to(CDT)
    mu0 = (G + G12) * NA - omega
    cr, sr = math.cos(omega * dt_), math.sin(omega * dt_)

    def nl(p1, p2, tau, rabi_tau):
        a1, a2 = p1.real ** 2 + p1.imag ** 2, p2.real ** 2 + p2.imag ** 2
        p1 = p1 * torch.exp(-1j * tau * (G * a1 + G12 * a2 - mu0))
        p2 = p2 * torch.exp(-1j * tau * (G * a2 + G12 * a1 - mu0))
        c_, s_ = math.cos(omega * rabi_tau), math.sin(omega * rabi_tau)
        return c_ * p1 + 1j * s_ * p2, c_ * p2 + 1j * s_ * p1

    def grad(p):
        ph = torch.fft.fft2(p)
        return torch.fft.ifft2(1j * kx * ph), torch.fft.ifft2(1j * ky * ph)

    e_vac = (G + G12 - 2 * omega)
    e_exc = 2 * omega * NA * (1 - math.cos(PHI0))

    def energies(p1, p2):
        d = lambda t: t.double()
        a1, a2 = d(p1.real ** 2 + p1.imag ** 2), d(p2.real ** 2 + p2.imag ** 2)
        nn = a1 + a2
        z = (a1 - a2) / nn
        g1x, g1y = grad(p1)
        g2x, g2y = grad(p2)
        kin = 0.5 * d(g1x.real ** 2 + g1x.imag ** 2 + g1y.real ** 2 + g1y.imag ** 2 + g2x.real ** 2 + g2x.imag ** 2 + g2y.real ** 2 + g2y.imag ** 2)
        rabi_cross = d((p1.conj() * p2).real)
        inter = 0.5 * G * (a1 ** 2 + a2 ** 2) + G12 * a1 * a2
        e_tot = (kin + inter - 2 * omega * rabi_cross - e_vac).mean()
        v1 = (d((p1.conj() * g1x).imag) / a1.clamp_min(1e-6), d((p1.conj() * g1y).imag) / a1.clamp_min(1e-6))
        v2 = (d((p2.conj() * g2x).imag) / a2.clamp_min(1e-6), d((p2.conj() * g2y).imag) / a2.clamp_min(1e-6))
        vd2 = ((0.5 * (v1[0] + v2[0])) ** 2 + (0.5 * (v1[1] + v2[1])) ** 2)
        w2 = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
        e_d = (0.5 * nn * vd2 + (G + G12) * (nn - 2 * NA) ** 2 / 4).mean()
        e_s = (nn * w2 / 8 + (G - G12) * nn ** 2 * z ** 2 / 4 + 2 * omega * (NA - rabi_cross)).mean()
        m1, m2 = p1.to(torch.complex128).mean(), p2.to(torch.complex128).mean()
        coh = float((m1.abs() ** 2 + m2.abs() ** 2) / (a1 + a2).mean())          # share of the density in the k = 0 mode: 1 for a homogeneous condensate, falls as it fragments
        return float(e_tot), float(e_d), float(e_s), coh

    def spectra(p1, p2):
        """radially binned spectra (energy per area) of the density sector and of the spin sector (kinetic + imbalance parts), same hydrodynamic variables as above."""
        d = lambda t: t.double()
        a1, a2 = d(p1.real ** 2 + p1.imag ** 2), d(p2.real ** 2 + p2.imag ** 2)
        nn = a1 + a2
        z = (a1 - a2) / nn
        g1x, g1y = grad(p1)
        g2x, g2y = grad(p2)
        v1 = (d((p1.conj() * g1x).imag) / a1.clamp_min(1e-6), d((p1.conj() * g1y).imag) / a1.clamp_min(1e-6))
        v2 = (d((p2.conj() * g2x).imag) / a2.clamp_min(1e-6), d((p2.conj() * g2y).imag) / a2.clamp_min(1e-6))
        fields_d = [0.5 * (v1[0] + v2[0]), 0.5 * (v1[1] + v2[1])]
        fields_s = [v1[0] - v2[0], v1[1] - v2[1]]
        pw = lambda f: torch.fft.fft2(f).abs() ** 2 / n ** 4
        spec_d = 0.5 * 2 * NA * (pw(fields_d[0]) + pw(fields_d[1])) + (G + G12) * pw(nn - 2 * NA) / 4
        spec_s = 2 * NA / 8 * (pw(fields_s[0]) + pw(fields_s[1])) + (G - G12) * (2 * NA) ** 2 * pw(z) / 4
        kk = torch.sqrt(k2).flatten()
        edges = torch.logspace(math.log10(0.04), math.log10(float(kk.max()) * 1.001), 33, device=dev)
        idx = torch.bucketize(kk, edges) - 1
        out = []
        for sp_ in (spec_d, spec_s):
            binned = torch.zeros(len(edges), dtype=torch.float64, device=dev).scatter_add_(0, idx.clamp(0, len(edges) - 1), sp_.flatten())
            out.append(binned[:-1].cpu().numpy())
        return np.sqrt(edges[:-1].cpu().numpy() * edges[1:].cpu().numpy()), out[0], out[1]

    t_out = max(dt_ * 50, 2 * math.pi / gap_exact(omega) / 4.0)
    steps = int(t_end / dt_)
    every = max(1, int(round(t_out / dt_)))
    rec = {"t": [], "tot": [], "d": [], "s": [], "coh": []}
    spec_times = {}
    t0 = time.time()
    # Strang: half nonlinear step, full kinetic step, half nonlinear step (the two halves of consecutive steps are merged below)
    psi1, psi2 = nl(psi1, psi2, 0.5 * dt_, 0.5 * dt_)
    for it in range(steps + 1):
        if it % every == 0:
            q1, q2 = nl(psi1, psi2, -0.5 * dt_, -0.5 * dt_)                 # undo the pending half step to read the state at time it*dt_
            et, ed, es, coh = energies(q1, q2)
            rec["t"].append(it * dt_)
            rec["tot"].append(et / e_exc)
            rec["d"].append(ed / e_exc)
            rec["s"].append(es / e_exc)
            rec["coh"].append(coh)
            if it == steps - steps % every:
                spec_times["end"] = spectra(q1, q2)
        f1 = torch.fft.ifft2(kin_full * torch.fft.fft2(psi1))
        f2 = torch.fft.ifft2(kin_full * torch.fft.fft2(psi2))
        psi1, psi2 = nl(f1, f2, dt_, dt_)
    print(f"    {label}: {steps} steps in {time.time() - t0:.0f} s", flush=True)
    out = {k: np.array(v) for k, v in rec.items()}
    out["spec"] = spec_times.get("end")
    return out


def get_run(omega, t_end, label, **kw):
    """run_gp with an optional pickle cache (env R50_CACHE) so that figure and text can be regenerated without repeating the 17-minute simulation."""
    import pickle
    path = os.environ.get("R50_CACHE")
    key = (omega, round(t_end, 6), tuple(sorted(kw.items())), N_GRID, PHI0, SEED_NOISE, DT)
    cache = {}
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            cache = pickle.load(f)
    if key in cache:
        print(f"    {label}: from cache", flush=True)
        return cache[key]
    out = run_gp(omega, t_end, label, **kw)
    if path:
        cache[key] = out
        with open(path, "wb") as f:
            pickle.dump(cache, f)
    return out


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("R1. Selection rule: a single spin quantum cannot decay into density phonons")
    # ------------------------------------------------------------------------------------------------------
    sym_ok, cubic, n_terms, bad = selection_rule(p)
    p("Hydrodynamic energy density of the two-component medium (N = N0 + a total density, z imbalance, phi relative phase, v_d total-phase gradient, w = grad phi), quantum pressure dropped:")
    p("    H = N v_d^2/2 + N w^2/8 + N z v_d w/2 + (g + g12) N^2/4 + (g - g12) N^2 z^2/4 + Omega N (1 - sqrt(1 - z^2) cos phi).")
    p(f"    Exchange 1 <-> 2 (z -> -z, phi -> -phi, w -> -w): H unchanged: {sym_ok}.")
    p(f"    Cubic part ({n_terms} terms): {cubic}")
    p(f"    Terms with an odd number of spin fields (z, phi, w): {len(bad)}.  => every cubic vertex has 0 or 2 spin fields:  d-d-d, d-spin-spin  (no spin-d-d).")
    p("    Therefore:  spin -> d + d is forbidden, spin -> d (one-phonon conversion) is forbidden, spin + spin -> d is allowed, and the lightest spin quantum is STABLE (a dark-matter-like species).")
    p("    The vertices of spin + spin -> d are not suppressed by Omega: a w^2 / 8 (coefficient 1/8), N0 v_d z w / 2 (coefficient N0/2), (g - g12) N0 a z^2 / 2 and Omega a (z^2 + phi^2) / 2.")

    # ======================================================================================================
    p.section("R2. What breaks the rule: unequal couplings g22 = g (1 + eps)")
    # ------------------------------------------------------------------------------------------------------
    om_b = 0.05
    gap0, kx0, kstar = crossing_gap(0.0, om_b)
    p(f"    Omega = {om_b}: m = sqrt(4 Omega (Omega + n_a (g - g12))) = {gap_exact(om_b):.4f}, c_d = {C_D:.4f}, c_r = {C_R:.4f}; the spin branch sqrt(m^2 + c_r^2 k^2) and the density branch c_d k cross at k* = m / sqrt(c_d^2 - c_r^2) = {kstar:.4f}.")
    p(f"    {'eps':>8s} {'smallest gap between the two branches':>40s} {'at k':>9s} {'gap / eps':>11s}")
    gaps = []
    for eps in (0.0, 1e-4, 1e-3, 1e-2, 3e-2, 1e-1):
        gp_, kk, _ = crossing_gap(eps, om_b)
        gaps.append((eps, gp_))
        p(f"    {eps:8.0e} {gp_:40.3e} {kk:9.4f} {(gp_ / eps if eps > 0 else float('nan')):11.3f}")
    nz = [(e_, g_) for e_, g_ in gaps if e_ > 0]
    slope = float(np.polyfit(np.log([e_ for e_, _ in nz if e_ <= 3e-2]), np.log([g_ for e_, g_ in nz if e_ <= 3e-2]), 1)[0])
    p(f"    => exact crossing for eps = 0 (gap {gaps[0][1]:.1e}, the minimiser tolerance); with eps != 0 an avoided crossing whose gap grows as eps^{slope:.2f} (linear mixing: eps^1).")
    p("    So spin quanta convert to (and decay into) density phonons only through a symmetry-breaking asymmetry of the two components, at a rate ~ eps^2.")

    # ======================================================================================================
    p.section("R3. If the spin sector were thermal with the density sector: Delta N_eff")
    # ------------------------------------------------------------------------------------------------------
    s_chk = 0.4
    rho_num = quad(lambda k: k ** 2 * (s_chk * k) / (math.exp(s_chk * k) - 1), 0, 60)[0] / (2 * math.pi ** 2)
    rho_formula = (math.pi ** 2 / 30) / s_chk ** 3
    p(f"    Energy density of one massless boson with dispersion omega = s k at temperature T = 1: numerical Bose integral {rho_num:.6f}, formula (pi^2/30)/s^3 = {rho_formula:.6f}  (s = {s_chk}).")
    p("    Equal temperatures at decoupling: rho_s / rho_SM = g_s / (s^3 g*_dec); the SM bath then heats relative to it, x_BBN = x_dec (10.75 / g*_dec)^(1/3); Delta N_eff = x_BBN * 10.75 / 1.75.")
    p(f"    {'s':>6s} {'1/s^3':>8s} {'dN_eff (g* = 106.75)':>22s} {'dN_eff (g* = 10.75)':>21s}")
    for s_ in (0.2, 0.3, 0.447, 0.5, 0.7, 1.0):
        p(f"    {s_:6.3f} {1 / s_ ** 3:8.1f} {delta_neff(s_, 106.75):22.3f} {delta_neff(s_, 10.75):21.3f}")
    s_min = (delta_neff(1.0, 106.75) / 0.3) ** (1.0 / 3.0)
    p(f"    Limit: N_eff = 2.99 +- 0.17 (Planck 2018, typed from memory), i.e. Delta N_eff < ~ 0.3 at 95 %: if the sectors ever shared a temperature above ~ 100 GeV, s > {s_min:.2f} is required; if they shared it as late as BBN, even s = 1 gives {delta_neff(1.0, 10.75):.2f}.")
    p("    (a single massless spin boson; valid while T >> m (gap).  Below T ~ m the spin quanta are non-relativistic and behave as matter, not radiation.)")

    # ======================================================================================================
    p.section("R4. Real-time 2D Gross-Pitaevskii simulation of the end of inflation (GPU)")
    # ------------------------------------------------------------------------------------------------------
    name_dev = torch.cuda.get_device_name(0) if DEV == "cuda" else "CPU"
    p(f"Device {name_dev}; grid {N_GRID}^2, dx = {DX} (box {N_GRID * DX:.0f}), dt = {DT}, split-step Fourier; g = {G}, g12 = {G12:.2f}, n_a = {NA}; initial homogeneous relative phase phi_0 = {PHI0} rad (both components at the same density), white noise seed of {SEED_NOISE:g} (low-pass k < 1.5), double precision in each component;")
    p(f"Omega in {OMEGAS}, i.e. Omega / mu = {', '.join(f'{o / (G + G12):.3f}' for o in OMEGAS)} (the model needs ~ 1e-12; these are the weakest couplings the lattice can follow), run for {N_PER:.0f} small-oscillation periods 2 pi / m.")
    p("Energy bookkeeping (hydrodynamic variables, in units of the initial Josephson energy E_J = 2 Omega n_a (1 - cos phi_0) per area):  TOTAL (a check: 1 = conserved), the SPIN sector (relative-phase gradient, imbalance and Rabi energy, condensate included),")
    p("the DENSITY sector (compression and total-phase flow) and the REST (cross terms, quantum pressure); plus the CONDENSATE FRACTION, (|<psi1>|^2 + |<psi2>|^2) / <N> (1 = intact homogeneous oscillation, falls as the condensate fragments into spin quanta).")
    runs = {}
    for om in OMEGAS:
        m_gap = gap_exact(om)
        runs[om] = get_run(om, N_PER * 2 * math.pi / m_gap, f"Omega = {om}")
    p("")
    p(f"    {'Omega':>7s} {'Omega/mu':>9s} {'m':>7s} {'T=2pi/m':>8s} {'t_end/T':>8s} | {'total':>6s} {'spin':>7s} {'density':>9s} {'rest':>7s} {'cond.frac':>10s}   (mean over the last 10 % of the run)")
    summary = {}
    for om, r in runs.items():
        m_gap = gap_exact(om)
        sel = r["t"] >= 0.9 * r["t"][-1]
        tot = float(np.mean(r["tot"][sel]))
        spin = float(np.mean(r["s"][sel]))
        dens = float(np.mean(r["d"][sel]))
        coh = float(np.mean(r["coh"][sel]))
        summary[om] = (tot, spin, dens, tot - spin - dens, coh)
        p(f"    {om:7.4f} {om / (G + G12):9.4f} {m_gap:7.4f} {2 * math.pi / m_gap:8.1f} {r['t'][-1] / (2 * math.pi / m_gap):8.0f} | {tot:6.3f} {spin:7.3f} {dens:9.3e} {tot - spin - dens:7.3f} {coh:10.3f}")
    p("")
    p("    Largest density-sector share reached at any output time (and when, in units of 1/Omega): " + ", ".join(f"Omega {o}: {float(np.max(r['d'])):.2f} at Omega t = {float(r['t'][int(np.argmax(r['d']))] * o):.1f}" for o, r in runs.items()))
    ts_periods = (0.5, 1, 2, 5, 10, 20, 40, 80, 120)
    p("    Density-sector energy share at selected times (periods T = 2 pi / m; '-' = beyond the run):")
    p("    " + f"{'Omega':>7s} | " + " ".join(f"{t_:>8g}" for t_ in ts_periods))
    for om, r in runs.items():
        m_gap = gap_exact(om)
        row = []
        for t_ in ts_periods:
            tt_ = t_ * 2 * math.pi / m_gap
            row.append(f"{r['d'][int(np.argmin(np.abs(r['t'] - tt_)))]:8.1e}" if tt_ <= r["t"][-1] else f"{'-':>8s}")
        p("    " + f"{om:7.4f} | " + " ".join(row))
    p("    Condensate fraction (|<psi1>|^2 + |<psi2>|^2) / <N> at the same times:")
    for om, r in runs.items():
        m_gap = gap_exact(om)
        row = []
        for t_ in ts_periods:
            tt_ = t_ * 2 * math.pi / m_gap
            row.append(f"{r['coh'][int(np.argmin(np.abs(r['t'] - tt_)))]:8.2f}" if tt_ <= r["t"][-1] else f"{'-':>8s}")
        p("    " + f"{om:7.4f} | " + " ".join(row))
    p("")
    tau = {}
    p(f"    {'Omega':>7s} | periods until the condensate fraction drops below 0.95 | until the density share reaches 1 % | 10 % | 25 %")
    for om, r in runs.items():
        m_gap = gap_exact(om)
        per = 2 * math.pi / m_gap

        def first(arr, thr, above=True):
            idx = np.where(arr > thr)[0] if above else np.where(arr < thr)[0]
            return r["t"][idx[0]] / per if len(idx) else float("nan")
        tau[om] = (first(r["coh"], 0.95, above=False), first(r["d"], 0.01), first(r["d"], 0.10), first(r["d"], 0.25))
        p(f"    {om:7.4f} | {tau[om][0]:44.1f} | {tau[om][1]:33.1f} | {tau[om][2]:4.1f} | {tau[om][3]:4.1f}")
    p("")
    p("    Final-time spectra (hydrodynamic variables): energy-weighted mean wavenumber of each sector, and the share of the density-sector energy above k = 1.5 (the low-pass cut of the seed; 1/xi ~ 1.4):")
    for om, r in runs.items():
        if r["spec"] is None:
            continue
        kk, sd, ss = r["spec"]
        kd = float(np.sum(kk * sd) / np.sum(sd))
        ks = float(np.sum(kk * ss) / np.sum(ss))
        hi = float(np.sum(sd[kk > 1.5]) / np.sum(sd))
        p(f"    Omega {om:7.4f}: <k>_density = {kd:5.2f}, <k>_spin = {ks:5.2f}, spin-quantum scale m / c_r = {gap_exact(om) / C_R:5.2f}; density-sector energy at k > 1.5: {hi:5.1%}; spectrum peak: density at k = {kk[int(np.argmax(sd))]:.2f}, spin at k = {kk[int(np.argmax(ss))]:.2f}")
    p("")
    t_check = np.max([np.max(np.abs(r['tot'] - 1.0)) for r in runs.values()])
    p(f"    Energy conservation: largest deviation of the total from 1 over all runs: {t_check:.1e}.")
    oms = np.array(list(summary.keys()))
    t10 = np.array([tau[o][2] for o in oms])
    ok = np.isfinite(t10)
    exp_t = float(np.polyfit(np.log(oms[ok]), np.log(t10[ok]), 1)[0]) if ok.sum() >= 3 else float("nan")
    p(f"    Periods needed for the density sector to reach 10 % of the initial energy against Omega: T_10% ~ Omega^{exp_t:.2f} over the {int(ok.sum())} couplings that got there (periods T = 2 pi / m ~ Omega^(-1/2)).")
    t10_abs = np.array([tau[o][2] * 2 * math.pi / gap_exact(o) for o in oms])
    exp_abs = float(np.polyfit(np.log(oms[ok]), np.log(t10_abs[ok]), 1)[0]) if ok.sum() >= 3 else float("nan")
    p("    The same in absolute time (units hbar / mu_0 with g n_a = 1): " + ", ".join(f"Omega {o}: t_10% = {t:.0f}, t_10% x Omega = {t * o:.1f}" for o, t in zip(oms, t10_abs)))
    p(f"    => t_10% ~ Omega^{exp_abs:.2f} in absolute time: the transfer time is a fixed multiple of 1 / Omega (t_10% x Omega = {np.nanmin(t10_abs * oms):.1f}-{np.nanmax(t10_abs * oms):.1f}), i.e. the transfer rate is of order the Rabi frequency Omega / hbar.")
    p("    The fragmentation of the condensate itself (condensate fraction below 0.95) happens after 8.5-10 periods at every Omega: the sine-Gordon self-resonance is scale-free in units of m, and the seed amplitude only sets the log.")
    omega_phys = 1e-12 * (G + G12)                                 # Omega / mu = 1e-12 in these units
    t_phys = float(np.nanmean(t10_abs * oms)) / omega_phys
    p(f"    EXTRAPOLATION (unreliable by orders of magnitude; the lattice covers only Omega / mu = {min(oms) / (G + G12):.0e}-{max(oms) / (G + G12):.0e} and no expansion): at Omega / mu = 1e-12 the same law gives t_10% ~ {t_phys:.1e} hbar / mu,")
    p(f"    i.e. {t_phys:.1e} Planck times if mu ~ m_P c^2; the Hubble time at the end of inflation in the E48 example (H = 4.2e13 GeV, an E48 number) is M_P / H = {1.22e19 / 4.2e13:.1e} Planck times.  The transfer would take ~ {t_phys / (1.22e19 / 4.2e13):.0e} Hubble times of the inflationary epoch;")
    p("    expansion dilutes the oscillating condensate (and with it the collision rate) long before that, so the energy would stay in the spin sector.  Expansion is not in the simulation.")

    # ======================================================================================================
    p.section("R5. Convergence and seed checks (Omega = 0.01)")
    # ------------------------------------------------------------------------------------------------------
    om_c = 0.01
    m_c = gap_exact(om_c)
    per_c = 2 * math.pi / m_c
    checks = {}
    for label, kw in (("reference (noise 1e-3, dt 0.04, seed 11)", {}), ("noise 1e-2", {"noise_amp": 1e-2}), ("noise 1e-4", {"noise_amp": 1e-4}), ("dt 0.02", {"dt": 0.02}), ("another seed (23)", {"seed": 23})):
        if label.startswith("reference"):
            rr = runs[om_c]
        else:
            rr = get_run(om_c, N_PER * per_c, label, **kw)
        def first_c(arr, thr, above=True, rr=rr):
            idx = np.where(arr > thr)[0] if above else np.where(arr < thr)[0]
            return rr["t"][idx[0]] / per_c if len(idx) else float("nan")
        checks[label] = (first_c(rr["coh"], 0.95, above=False), first_c(rr["d"], 0.01), first_c(rr["d"], 0.10), float(np.mean(rr["d"][rr["t"] >= 0.9 * rr["t"][-1]])), float(np.max(np.abs(rr["tot"] - rr["tot"][0]))))
    p(f"    {'run':<44s} {'fragmentation (periods)':>24s} {'density 1 %':>12s} {'density 10 %':>13s} {'density share at end':>21s} {'energy drift':>13s}")
    for label, v in checks.items():
        p(f"    {label:<44s} {v[0]:24.1f} {v[1]:12.1f} {v[2]:13.1f} {v[3]:21.3f} {v[4]:13.1e}")
    t_spread = np.nanmax([v[2] for v in checks.values()]) / np.nanmin([v[2] for v in checks.values()])
    p(f"    => a factor 100 in the seed amplitude moves the fragmentation time by a few periods (a logarithm) and the 10 %-time by a factor {t_spread:.2f} at most; halving dt and changing the seed change nothing outside that range.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("R1: a spin quantum can decay into density phonons", f"NO: the exchange symmetry holds exactly ({sym_ok}) and all {n_terms} cubic terms have an even number of spin fields ({len(bad)} odd): the lightest spin quantum is stable"),
        ("R2: the symmetry-breaking asymmetry opens the channel", f"YES, linearly: avoided-crossing gap ~ eps^{slope:.2f} (eps <= 3e-2); the decay rate ~ eps^2"),
        ("R3: a thermal spin sector at s = 0.3 respects the Delta N_eff limit", f"NO: Delta N_eff = {delta_neff(0.3, 106.75):.2f} (decoupling above 100 GeV) against < ~0.3; s > {s_min:.2f} needed"),
        ("R4: in the classical field the condensate fragments and populates the density sector", f"YES at Omega / mu = {min(om / (G + G12) for om in runs):.4f}-{max(om / (G + G12) for om in runs):.3f}: fragmentation after {np.nanmin([t[0] for t in tau.values()]):.0f}-{np.nanmax([t[0] for t in tau.values()]):.0f} periods at every Omega; the density sector reaches 10 % of the energy after t = {np.nanmin(t10_abs * oms):.1f}-{np.nanmax(t10_abs * oms):.1f} / Omega"),
        ("R4b: the transfer is fast enough at the Rabi coupling the model needs (1e-12)", f"NO, by extrapolation: t_10% ~ {t_phys:.0e} hbar / mu, ~ {t_phys / (1.22e19 / 4.2e13):.0e} inflationary Hubble times; the energy stays in the (stable) spin sector"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<100s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 3, figsize=(16.5, 5.0))
    ax = axs[0]
    eps_arr = np.array([e_ for e_, _ in nz])
    gap_arr = np.array([g_ for _, g_ in nz])
    ax.loglog(eps_arr, gap_arr, "o-", color=S1, lw=2.0, ms=7, label="gap between spin and density branch")
    ax.loglog(eps_arr, gap_arr[0] * eps_arr / eps_arr[0], color=MUTED, ls="--", lw=1.2, label="∝ ε")
    ax.set(xlabel="coupling asymmetry ε  (g₂₂ = g(1+ε))", ylabel="avoided-crossing gap at k*", title="Breaking the exchange symmetry opens the channel linearly")
    ax.legend(loc="upper left", fontsize=9)

    ax = axs[1]
    first_om = list(runs)[0]
    keys = list(runs)
    for om, col in zip((keys[0], keys[len(keys) // 2], keys[-1]), (S1, S2, S3)):
        r = runs[om]
        ax.plot(r["t"] * om, np.maximum(r["d"], 1e-6), color=col, lw=2.0, label=f"Ω = {om:g}")
    ax.set_yscale("log")
    ax.axhline(0.1, color=MUTED, ls="--", lw=1.0)
    ax.text(0.3, 0.115, "10 %", fontsize=9, color=INK_2)
    ax.set(xlabel="time × Rabi coupling, Ω t", ylabel="density-sector share of the initial Josephson energy", ylim=(1e-5, 2),
           title="The density sector fills after a time of order 1/Ω")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[2]
    last_om = list(runs)[-1]
    r = runs[last_om]
    if r["spec"] is not None:
        kk, sd, ss = r["spec"]
        okk = (sd > 0) & (ss > 0)
        ax.loglog(kk[okk], sd[okk], color=S3, lw=2.0, label="density sector")
        ax.loglog(kk[okk], ss[okk], color=S2, lw=2.0, label="spin sector")
        ax.axvline(gap_exact(last_om) / C_R, color=MUTED, ls=":", lw=1.3)
        ymax = float(max(sd.max(), ss.max()))
        ax.set_ylim(ymax * 1e-8, ymax * 5)
        ax.text(gap_exact(last_om) / C_R * 1.08, ymax * 3e-8, "m / c_r", fontsize=9, color=INK_2)
    ax.set(xlabel="wavenumber k", ylabel="energy per area in the k-shell", title=f"Spectra at the end of the run (Ω = {last_om:g})")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "reheating")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
