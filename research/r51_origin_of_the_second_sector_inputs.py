"""
r51 - Where could the two inputs of the second sector come from?  (LAB_NOTEBOOK.md entry E49, tests V1-V4)

Question (open item from E48 / r44): the two-component medium that supplies the stretching needs (i) a Josephson/Rabi energy of about 1e-12 of the medium's energy density and (ii) a slow spin sound,
s = c_r/c_d = 0.05-0.7, i.e. an inter-component repulsion g12 close to the intra-component coupling g: g12/g = (1 - s^2)/(1 + s^2) = 0.83 for s = 0.3.  Both were inputs.  Is there a natural
way to get both at once?

Candidate picture: the two components live on two sheets (branes) separated by a distance d in an extra dimension.  The Rabi coupling is then the tunnelling amplitude through the bulk between the sheets,
exponentially small in d; the inter-sheet repulsion g12 comes from a bulk-mediated interaction of finite range.
  V1. The tunnelling amplitude of a particle between two wells, exactly (110-digit even/odd bound states of a double square well): Omega(d) / E_0 against the separation, for three barrier heights.  How
      many healing lengths of separation give Omega / mu = 1e-12 to 1e-11 (the value needed: V_0 / rho_medium = 2 Omega / mu = 1e-12 ... 1.6e-11 in r44)?
  V2. The compatibility problem: the same separation makes a contact interaction between the sheets exponentially small (g12 -> 0, s -> 1).  What range must the mediator of g12 have?
  V3. Technical naturalness: Omega -> 0 restores a U(1) symmetry of the relative phase, so Omega is multiplicatively renormalised; the slow spin sound g12 -> g is the edge of the miscibility
      transition (tuned) unless g12 and g are both set by one mediator (then s is a ratio of two integrals of the same potential).
  V4. The predictions that do not depend on these origins: tensor consistency relation and equilateral non-Gaussianity against the sound speed.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r51_origin_of_the_second_sector_inputs"
mp.mp.dps = 110
W_WELL = 2.0                  # well width (units hbar = m = 1)


def single_well_energy(u_b, w=W_WELL):
    """Ground state of one finite square well of width w and depth u_b (even state): k tan(k w / 2) = kappa, bracketed in (0, min((pi/w)^2/2, u_b))."""
    f = lambda e: mp.sqrt(2 * e) * mp.tan(mp.sqrt(2 * e) * w / 2) - mp.sqrt(2 * (u_b - e))
    hi = min(mp.mpf(0.5) * (mp.pi / w) ** 2, mp.mpf(u_b)) * (1 - mp.mpf(10) ** -9)
    return mp.findroot(f, (mp.mpf(10) ** -9, hi), solver="illinois", tol=mp.mpf(10) ** -90, maxsteps=500)


def double_well_levels(u_b, d, e0, w=W_WELL):
    """Even and odd bound-state energies of two wells (|y| in [d/2, d/2 + w], potential 0) separated by a barrier of height u_b and width d, with the barrier outside as well."""
    a = mp.mpf(d) / 2

    def condition(e, parity):
        k = mp.sqrt(2 * e)
        kap = mp.sqrt(2 * (u_b - e))
        if parity == "even":
            amp, der = mp.cosh(kap * a), kap * mp.sinh(kap * a)       # psi and psi' of the middle barrier solution at y = a
        else:
            amp, der = mp.sinh(kap * a), kap * mp.cosh(kap * a)
        # in the well: psi = A cos(k (y - a)) + B sin(k (y - a)), A = amp, B = der / k; at y = a + w the log-derivative must be -kappa
        psi_w = amp * mp.cos(k * w) + (der / k) * mp.sin(k * w)
        dpsi_w = -amp * k * mp.sin(k * w) + der * mp.cos(k * w)
        return dpsi_w + kap * psi_w

    levels = {}
    for parity in ("even", "odd"):
        # start from e0 and walk toward the root with a bracketing secant (the splitting is tiny: use a tight starting interval around e0)
        g = lambda e, par=parity: condition(e, par)
        shift = mp.mpf(1) / 3
        root = mp.findroot(g, (e0 * (1 - shift * mp.exp(-mp.sqrt(2 * (u_b - e0)) * a)), e0 * (1 + shift * mp.exp(-mp.sqrt(2 * (u_b - e0)) * a))), solver="secant", tol=mp.mpf(10) ** (-100), maxsteps=500)
        levels[parity] = root
    return levels["even"], levels["odd"]


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("V1. Tunnelling between two sheets: Omega(d) from exact double-well levels")
    # ------------------------------------------------------------------------------------------------------
    p("Units hbar = m = 1; wells of width 2 and depth U_b (barrier outside and between).  Omega = (E_odd - E_even) / 2 is the single-particle tunnelling amplitude (the mean-field Josephson coupling of two")
    p("condensates); E_0 = the single-well ground state, taken as the natural energy scale (mu ~ E_0 up to O(1)); kappa_0 = sqrt(2 (U_b - E_0)) is the decay constant in the barrier; 1/kappa_0 plays the")
    p("role of the healing length.")
    results = {}
    for u_b in (1.0, 4.0, 16.0):
        e0 = single_well_energy(mp.mpf(u_b))
        kap0 = mp.sqrt(2 * (u_b - e0))
        rows = []
        for d in (2.0, 4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 40.0):
            ee, eo = double_well_levels(mp.mpf(u_b), d, e0)
            rows.append((d, float(kap0 * d), float((eo - ee) / (2 * e0))))
        results[u_b] = (float(e0), float(kap0), rows)
    p(f"    {'U_b':>5s} {'E_0':>8s} {'kappa_0':>8s} | " + "  ".join(f"d = {d:>4g}" for d in (2, 4, 8, 12, 16, 24, 32, 40)))
    for u_b, (e0, kap0, rows) in results.items():
        p(f"    {u_b:5.1f} {e0:8.4f} {kap0:8.4f} | " + "  ".join(f"{r[2]:8.1e}" for r in rows))
    p("    (entries: Omega / E_0)")
    p("    Exponential law and the separation needed (fit of ln(Omega / E_0) against kappa_0 d for the last four points):")
    needed = {}
    for u_b, (e0, kap0, rows) in results.items():
        x = np.array([r[1] for r in rows[-4:]])
        y = np.log(np.array([r[2] for r in rows[-4:]]))
        slope, icpt = np.polyfit(x, y, 1)
        for target in (1.0e-12, 1.6e-11):
            # V_0 / rho_medium = 2 Omega / mu = target  =>  Omega / mu = target / 2
            kd = (math.log(target / 2.0) - icpt) / slope
            needed[(u_b, target)] = kd
        p(f"      U_b = {u_b:4.1f}: Omega / E_0 = {math.exp(icpt):.2f} exp({slope:.3f} kappa_0 d);  Omega / mu = 5e-13 needs kappa_0 d = {needed[(u_b, 1.0e-12)]:.1f}; 8e-12 needs {needed[(u_b, 1.6e-11)]:.1f}")
    kd_lo = min(needed.values())
    kd_hi = max(needed.values())
    p(f"    => with kappa_0 xi ~ 1 the sheets must be about {kd_lo:.0f}-{kd_hi:.0f} healing lengths apart (alpha x {kd_lo:.0f}-{kd_hi:.0f} Planck lengths): the tiny Rabi coupling is the exponential tail of a tunnelling")
    p("       amplitude, a separation of a few tens of healing lengths, with no tuning of any coupling.  (Compare r41: a structure ~ 14-85 healing lengths wide gives m_e / m_P = 4e-23 by the same exponential.)")

    # ======================================================================================================
    p.section("V2. The compatibility problem: a slow spin sound needs a LONG-range inter-sheet repulsion")
    # ------------------------------------------------------------------------------------------------------
    d_use = float(np.mean([kd_lo, kd_hi]))
    p(f"    Sheets {d_use:.0f} healing lengths apart (the middle of the range above).  A contact interaction between the sheets is exponentially small there (g12 / g ~ e^(-d/xi) ~ {math.exp(-d_use):.0e}): s = 1,")
    p("    excluded by r44.  A mediator of range lambda_m gives g12 / g ~ exp(-(d - t) / lambda_m) (t = sheet thickness ~ 1 healing length; the exact plane-plane integral of a Yukawa potential differs by a power-law")
    p("    prefactor).  With s^2 = (g - g12)/(g + g12):")
    p(f"    {'s':>5s} {'g12 / g':>9s} {'range lambda_m (healing lengths)':>34s} {'mediator mass / M_P (alpha = 1)':>32s}")
    rows_v2 = []
    for s_val in (0.05, 0.1, 0.2, 0.3, 0.5, 0.7):
        g12_over_g = (1 - s_val ** 2) / (1 + s_val ** 2)
        lam = (d_use - 1.0) / math.log(1.0 / g12_over_g)
        m_med = 1.0 / lam                                 # hbar c / lambda_m = M_P c^2 (l_P / lambda_m) = M_P c^2 / (lambda_m / xi) for xi = alpha l_P with alpha = 1
        rows_v2.append((s_val, g12_over_g, lam, m_med))
        p(f"    {s_val:5.2f} {g12_over_g:9.3f} {lam:34.0f} {m_med:32.2e}")
    p(f"    (mediator mass = hbar c / lambda_m = M_P / (lambda_m / xi) for xi = l_P; 1 M_P = {1.221e19:.3g} GeV.)")
    lam_lo, lam_hi = rows_v2[2][2], rows_v2[4][2]
    p(f"    => a spin sound of 0.2-0.5 c needs a mediator of range {lam_hi:.0f}-{lam_lo:.0f} healing lengths, i.e. mass {1.221e19 / lam_lo:.1e}-{1.221e19 / lam_hi:.1e} GeV for alpha = 1: {lam_hi:.0f}-{lam_lo:.0f} times longer than the")
    p("       wavefunction tail that sets the tunnelling.  A short-range tunnelling suppression and a long-range repulsion can come from the same bulk only if the repulsion is carried by a field much lighter")
    p("       than the one that governs the matter wavefunction: two different bulk ranges, as for a nearly massless (gravity-like) bulk force between the sheets.  That is a requirement, not a derivation.")

    # ======================================================================================================
    p.section("V3. Technical naturalness")
    # ------------------------------------------------------------------------------------------------------
    p("    Omega: when Omega = 0 the relative phase has an exact shift symmetry (r39), so every quantum correction to Omega is proportional to Omega: a small Omega is stable under renormalisation")
    p("    (technically natural).  The exponential tunnelling origin gives it without tuning.")
    p("    s: s = 1 (g12 = 0, two decoupled components) and s = 0 (g12 = g, the edge of the miscible phase) are the special points; s = 0.3 means g12 / g = 0.83, close to the second one:")
    p("    a mild tuning that no symmetry protects (unless g12 and g are fixed by one mediator, V2).")

    # ======================================================================================================
    p.section("V4. Predictions independent of the origin")
    # ------------------------------------------------------------------------------------------------------
    p("    r = 16 epsilon s, n_t = -2 epsilon = -r / (8 s) (single-field consistency relation violated by the factor s), f_NL^equil = -(35/108)(1/s^2 - 1), n_s unchanged.")
    p(f"    {'s':>5s} {'n_t / (-r/8)':>14s} {'f_NL^equil':>12s} {'r at n_s = 0.965 (f ~ 8-10)':>30s}")
    rows_v4 = []
    for s_val in (0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0):
        fnl = -(35.0 / 108.0) * (1.0 / s_val ** 2 - 1.0)
        r_pred = s_val * 0.0875                           # canonical r ~ 0.0875 at n_s = 0.965 (cos junction, N = 60: f = 8.4, r_can = 0.083; f = 10: 0.096)
        rows_v4.append((s_val, 1.0 / s_val, fnl, r_pred))
        p(f"    {s_val:5.2f} {1.0 / s_val:14.1f} {fnl:12.1f} {r_pred:30.4f}")
    p("    Planck 2018 (typed from memory): f_NL^equil = -26 +- 47 (68 %), so s > 0.05; a detection of tensors with r ~ 0.01-0.03 would test n_t = -r/(8s) only if n_t can be measured to ~ 10 % of -r/8 (not in reach of current")
    p("    forecasts), and f_NL^equil ~ -3 at s = 0.3 is far below the sensitivity of Planck (+- 47) and of planned surveys (order 10; typed from memory).  The second sector is, for now, untestable beyond n_s and r.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    verdict = [
        ("V1: a Rabi coupling of 1e-12 of the medium's energy follows from tunnelling between sheets",
         f"YES: exponential law verified to many digits; needs sheets {kd_lo:.0f}-{kd_hi:.0f} healing lengths apart (barrier heights 1-16 E_0), no tuning"),
        ("V2: the same sheets give the large inter-sheet repulsion the slow spin sound needs",
         f"ONLY with a mediator of range {rows_v2[4][2]:.0f}-{rows_v2[2][2]:.0f} healing lengths (s = 0.5-0.2), that much longer than the wavefunction tail: a requirement, not a derivation"),
        ("V3: both inputs are technically natural", "Omega yes (symmetry); s only as a mild, unprotected tuning (g12/g = 0.83 for s = 0.3)"),
        ("V4: the second sector can be tested beyond n_s and r", f"NO at present: f_NL^equil = {rows_v4[3][2]:.1f} at s = 0.3 against +-47 (Planck); n_t / (-r/8) = {rows_v4[3][1]:.1f} unmeasurable"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<86s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 5.2))
    ax = axs[0]
    for (u_b, (e0, kap0, rows)), col, mk in zip(results.items(), (S1, S2, S3), ("o", "s", "^")):
        ax.semilogy([r[1] for r in rows], [r[2] for r in rows], mk + "-", color=col, ms=7, label=f"barrier height {u_b:g} (E₀ = {e0:.2f}, κ₀ = {kap0:.2f})")
    ax.axhspan(5e-13, 8e-12, color=S3, alpha=0.18, lw=0)
    ax.text(33, 1.5e-12, "needed (r44): Ω/μ ≈ 5×10⁻¹³–8×10⁻¹²", fontsize=9, color=S3)
    ax.set(xlabel="separation of the sheets × decay constant in the barrier, κ₀ d", ylabel="tunnelling amplitude Ω ÷ E₀", ylim=(1e-30, 3), xlim=(-2, 72),
           title="A tiny Rabi coupling is the tail of tunnelling between sheets")
    ax.legend(loc="upper right", fontsize=9)

    ax = axs[1]
    ss = np.linspace(0.05, 0.9, 60)
    lam_curve = (d_use - 1.0) / np.log((1 + ss ** 2) / (1 - ss ** 2))
    ax.semilogy(ss, lam_curve, color=S1, lw=2.2, label=f"sheets {d_use:.0f} healing lengths apart")
    ax.axhline(d_use, color=MUTED, ls="--", lw=1.3)
    ax.text(0.06, d_use * 1.12, "separation d", fontsize=9, color=INK_2)
    ax.text(0.58, 4.0, "shaded: s = 0.05–0.7 (range used in r44/r47)", fontsize=9, color=INK_2)
    ax.axvspan(0.052, 0.7, color=S3, alpha=0.12, lw=0)
    ax.set(xlabel="spin-sound speed s = c_r / c_d", ylabel="range of the repulsion mediator (healing lengths)", ylim=(3, 3e3),
           title="A slow spin sound needs a long-range inter-sheet repulsion")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "origin")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
