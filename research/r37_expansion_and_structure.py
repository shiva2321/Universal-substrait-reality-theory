"""
r37 - Expansion and structure: do the medium's own fluctuations freeze into a sky-like pattern?
(LAB_NOTEBOOK.md entry E46, test F5)

Question (user): "a" (stage 2 of the fluid-space programme: expansion and structure): after the quench (r35) the medium expands;
do the quantum fluctuations of its phonons, frozen at the sound horizon, give a nearly scale-invariant spectrum with the
observed tilt n_s = 0.965 +- 0.004?  Does the medium's graininess (Bogoliubov dispersion) spoil it?  Can the medium drive the
expansion itself?

Physics: a phonon field delta in a medium expanding with scale factor a(eta) (conformal time eta) has v = a delta obeying
        v'' + [ c^2 k^2 (1 + k^2 xi^2 / 2 a^2) - a''/a ] v = 0 ,
(the term in xi is the Bogoliubov dispersion at fixed physical healing length xi), with the vacuum (adiabatic) initial state
v -> exp(-i int omega d eta) / sqrt(2 omega) at early times: in a superfluid this is the medium's actual ground state, so there
is no free choice of initial state (Unruh 1995; Corley & Jacobson 1996).  Modes freeze when the comoving sound horizon c/(k) falls
below the comoving Hubble radius 1/(aH): that needs accelerating expansion (the comoving Hubble radius shrinks).
  * power-law a ~ t^p: spectrum P(k) ~ k^(n_s - 1) with n_s - 1 = -2/(p - 1);
  * de Sitter: a = -1/(H eta) and the equation depends only on tau = -c k eta and lambda = H xi / c:
        v_tautau + [ 1 + (lambda^2 / 2) tau^2 - 2 / tau^2 ] v = 0 ,   exactly scale invariant for any lambda.

Method:
  A. Validate the mode integrator against the exact Hankel solution, then measure the tilt for power-law expansions.
  B. Graininess: amplitude of the frozen mode against lambda, adiabatic initial state.
  C. What drives the expansion?  Equation of state of the medium, the tilt and tensor limits, the Hubble rate and energy scale.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import hankel1

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, hbar, lP, save_fig, style  # noqa: E402

NAME = "r37_expansion_and_structure"
A_S = 2.10e-9                     # Planck 2018 scalar amplitude
NS, NS_ERR = 0.9649, 0.0042       # Planck 2018 tilt
R_LIMIT = 0.036                   # BICEP/Keck 2021 tensor-to-scalar ratio limit (95 %), typed from memory
M_PL_REDUCED_GEV = 2.435e18
E_PLANCK_GEV = 1.221e19


def integrate_mode(omega2, x_start, x_end, rtol=1e-11):
    """Integrate u'' = -omega2(x) u from x_start to x_end.  Here x = -c k eta falls as time passes, so x_start > x_end.
    Initial state: adiabatic vacuum u = exp(-i int omega dt) / sqrt(2 omega); written in x = -t this is
    u' = (+i omega - omega'/(2 omega)) u.  (The complex conjugate state, which I use below, has the same modulus at all later x
    because the equation is real, and the modulus is all that enters the power spectrum.)"""
    w0 = math.sqrt(omega2(x_start))
    h = 1e-5 * max(1.0, abs(x_start))
    dw = (math.sqrt(omega2(x_start + h)) - math.sqrt(omega2(x_start - h))) / (2 * h)
    u0 = 1.0 / math.sqrt(2.0 * w0) + 0j
    up0 = (-1j * w0 - dw / (2.0 * w0)) * u0

    # complex u split into real and imaginary parts: y = [Re u, Re u', Im u, Im u']
    def rhs_real(x, y):
        w2 = omega2(x)
        return [y[1], -w2 * y[0], y[3], -w2 * y[2]]

    sol = solve_ivp(rhs_real, (x_start, x_end), [u0.real, up0.real, u0.imag, up0.imag], method="DOP853",
                    rtol=rtol, atol=1e-14, dense_output=True)
    return sol


def mode_amplitude(sol, x):
    y = sol.sol(x)
    return math.hypot(y[0], y[2])


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("A. The integrator against the exact solution, and the tilt of power-law expansions")
    # ------------------------------------------------------------------------------------------------------
    p("For a ~ t^p the mode equation in x = -c k eta is u'' + [1 - (nu^2 - 1/4)/x^2] u = 0, nu = (3p - 1) / (2 (p - 1)); the exact")
    p("vacuum solution is u = sqrt(pi x) H_nu^(1)(x) / 2.  The frozen spectrum goes as P(k) ~ k^(3 - 2 nu), so n_s - 1 = -2 / (p - 1).")
    p(f"    {'p':>7s} {'nu':>7s} {'max |u|^2 error':>16s} {'n_s - 1 measured':>17s} {'-2/(p-1)':>10s}")
    tilt_rows = []
    for pp in (10.0, 20.0, 57.0, 200.0, 1000.0):
        nu = (3 * pp - 1) / (2 * (pp - 1))
        q = nu ** 2 - 0.25
        sol = integrate_mode(lambda xx, q=q: 1.0 - q / xx ** 2, 300.0, 1e-4)
        xs = np.geomspace(1e-4, 1.0, 30)
        err = max(abs(mode_amplitude(sol, xx) ** 2 / (math.pi * xx / 4.0 * abs(hankel1(nu, xx)) ** 2) - 1.0) for xx in xs[5:])
        # Dimensionless spectrum P(k) = k^3 |v_k|^2 / (2 pi^2 a^2) with v_k = u(x)/sqrt(c k) and x = k |eta_f| at the common final
        # time eta_f = -1e-4 (a(eta_f) is the same for every k), so P(k) ~ k^2 |u(k |eta_f|)|^2 and n_s - 1 = d ln P / d ln k.
        kk = np.geomspace(1.0, 30.0, 25)
        pk = np.array([k ** 2 * mode_amplitude(sol, k * 1e-4) ** 2 for k in kk])
        tilt_rows.append((pp, nu, err, np.polyfit(np.log(kk), np.log(pk), 1)[0], -2.0 / (pp - 1.0)))
    for pp, nu, err, meas, ana in tilt_rows:
        p(f"    {pp:7.0f} {nu:7.3f} {err:16.1e} {meas:17.5f} {ana:10.5f}")
    worst_tilt = max(abs(r[3] - r[4]) for r in tilt_rows)
    worst_err = max(r[2] for r in tilt_rows)
    p(f"    => the integrator matches the exact Hankel solution to {worst_err:.0e} and the measured tilt agrees with -2/(p-1) to {worst_tilt:.1e}.")
    eps_needed = (1.0 - NS) / (2.0 + (1.0 - NS))
    p_needed = 1.0 / eps_needed
    n_s_lo = NS - NS_ERR
    p(f"    The observed n_s = {NS} +- {NS_ERR} needs a ~ t^p with p = {p_needed:.0f} (epsilon = 1/p = {eps_needed:.4f}), i.e. w = -1 + 2 epsilon / 3 = {-1 + 2 * eps_needed / 3:.4f}.")
    p("    (Slow roll, a quasi-exponential expansion, is required: modes freeze only if the comoving Hubble radius shrinks.)")

    # ======================================================================================================
    p.section("B. Does the medium's graininess spoil it?  de Sitter expansion with the Bogoliubov dispersion")
    # ------------------------------------------------------------------------------------------------------
    p("tau = -c k eta, lambda = H xi / c:  v'' + [1 + (lambda^2/2) tau^2 - 2/tau^2] v = 0 ; adiabatic vacuum imposed at tau_i = max(200, 40/lambda);")
    p("amplitude |v|^2 at tau_f = 0.01, divided by the lambda = 0 result (exact value (1 + 1/tau_f^2)/2).")
    tau_f = 0.01
    exact0 = 0.5 * (1.0 + 1.0 / tau_f ** 2)
    sol0 = integrate_mode(lambda t: 1.0 - 2.0 / t ** 2, 200.0, tau_f)
    amp0 = mode_amplitude(sol0, tau_f) ** 2
    p(f"    lambda = 0: numerical |v|^2 = {amp0:.6f}, exact {exact0:.6f} (difference {abs(amp0 / exact0 - 1):.1e}).")
    lams = [0.5, 0.3, 0.2, 0.1, 0.05, 0.02]
    corr = []
    p(f"    {'lambda':>8s} {'tau_i':>8s} {'|v|^2 / |v_0|^2 - 1':>20s}")
    for lam in lams:
        tau_i = max(200.0, 40.0 / lam)
        sol = integrate_mode(lambda t, lam=lam: 1.0 + 0.5 * lam ** 2 * t ** 2 - 2.0 / t ** 2, tau_i, tau_f)
        r = mode_amplitude(sol, tau_f) ** 2 / amp0 - 1.0
        corr.append(r)
        p(f"    {lam:8.2f} {tau_i:8.0f} {r:20.3e}")
    lam_arr, corr_arr = np.array(lams), np.array(corr)
    slope_l = np.polyfit(np.log(lam_arr[-4:]), np.log(np.abs(corr_arr[-4:])), 1)[0]
    p(f"    => for small lambda the correction goes as lambda^{slope_l:.1f}; because tau = -c k eta is the only variable, every mode is")
    p("       changed by the same factor: the spectrum stays exactly scale invariant and only the amplitude moves.")
    p("       With the adiabatic (medium ground state) initial condition there is no trans-Planckian ambiguity to tune.")

    # ======================================================================================================
    p.section("C. What drives the expansion?  The medium's own equation of state, the tensors, the energy scale")
    # ------------------------------------------------------------------------------------------------------
    p("Medium alone (repulsive condensate): P = m n c_s^2 / 2 >= 0 and rho c^2 = m n c^2 + m n c_s^2 / 2, so w = P / rho c^2 >= 0.")
    p(f"    {'c_s / c':>8s} {'w':>9s} {'epsilon = 3(1+w)/2':>20s}")
    w_rows = []
    for ratio in (0.1, 0.3, 0.5, 0.8, 1.0):
        w = (ratio ** 2 / 2.0) / (1.0 + ratio ** 2 / 2.0)
        w_rows.append((ratio, w))
        p(f"    {ratio:8.2f} {w:9.4f} {1.5 * (1 + w):20.3f}")
    p("    Accelerated expansion needs w < -1/3 (epsilon < 1); the tilt needs w = -0.988.  A medium with P >= 0 decelerates: its comoving")
    p("    sound horizon grows and no mode ever freezes.  Tension (P < 0, a stretched liquid) would be needed, and a stretched liquid cavitates.")
    r_power = 16.0 * eps_needed
    h_power = math.pi * M_PL_REDUCED_GEV * math.sqrt(A_S * r_power / 2.0)
    v14_power = (1.5 * math.pi ** 2 * A_S * r_power) ** 0.25 * M_PL_REDUCED_GEV
    r_star = 12.0 / 57.0 ** 2
    h_star = math.pi * M_PL_REDUCED_GEV * math.sqrt(A_S * r_star / 2.0)
    v14_star = (1.5 * math.pi ** 2 * A_S * r_star) ** 0.25 * M_PL_REDUCED_GEV
    c_s_max = R_LIMIT / r_power
    p(f"Tensors (gravitational waves of the expansion), r = 16 epsilon c_s: the pure power law above gives r = {r_power:.2f} for c_s = c, against r < {R_LIMIT}")
    p(f"    (typed from memory, BICEP/Keck 2021); that needs c_s < {c_s_max:.2f} c, but the medium's sound speed is c.  A plateau with the same tilt, n_s - 1 = -2/N,")
    p(f"    N = 57, gives r = {r_star:.4f}: allowed.  So the tilt alone does not fix the expansion; its shape (small epsilon, larger eta) does.")
    p("    Caveat: these H and V^1/4 assume that the fluctuating field is the one driving the expansion (as in k-inflation, where the")
    p("    phonon of a P(X) fluid is the inflaton).  If the medium's phonons are only spectators of an expansion driven by something else,")
    p("    turning them into curvature perturbations needs an extra conversion step (curvaton-like) that is not computed here.")
    lam_power = h_power / E_PLANCK_GEV
    lam_star = h_star / E_PLANCK_GEV
    p(f"Amplitude A_s = {A_S:.2e}:  H = pi M_Pl sqrt(A_s r / 2):  power law H = {h_power:.1e} GeV (V^1/4 = {v14_power:.1e} GeV);  plateau H = {h_star:.1e} GeV (V^1/4 = {v14_star:.1e} GeV).")
    p(f"    Graininess parameter lambda = H xi / c = alpha H t_P = {lam_power:.1e} alpha (power law) or {lam_star:.1e} alpha (plateau) for xi = alpha l_P;")
    p(f"    lambda^{slope_l:.0f} corrections of order {lam_star ** slope_l:.0e}: negligible.")
    p("    E-folds: the ~67 that r35 needs to dilute the quench's strings is of the same size as the ~50-60 a standard inflation needs for the")
    p("    horizon problem and the observable modes: one period of quasi-exponential stretching can do both, but nothing here derives it.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    verdict = [
        ("F5a: frozen phonon fluctuations give a scale-invariant spectrum",
         f"CONFIRMED: de Sitter is exactly scale invariant; power laws give n_s - 1 = -2/(p-1) (checked to {worst_tilt:.0e}); needs p = {p_needed:.0f} for the observed tilt"),
        ("F5b: the medium's graininess spoils it",
         f"NO: amplitude correction ~ lambda^{slope_l:.1f}, about {lam_star ** slope_l:.0e} for a Planck-length medium; adiabatic vacuum is the medium's own ground state"),
        ("F5c: the medium itself drives the expansion",
         f"NO: its equation of state has w >= 0 (0 to {w_rows[-1][1]:.2f}); tilt needs w = {-1 + 2 * eps_needed / 3:.3f}; a separate driver or a stretched medium is required"),
        ("F5d: a power-law expansion with the observed tilt fits the CMB",
         f"NO: r = {r_power:.2f} > {R_LIMIT}; a plateau (r = {r_star:.4f}) is needed, with H = {h_star:.0e} GeV"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<66s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 9.6))

    ax = axs[0, 0]
    taus = np.geomspace(300.0, 0.01, 600)
    for lam, col, lab in ((0.0, S1, "λ = 0 (no graininess)"), (0.3, S2, "λ = 0.3")):
        tau_i = max(200.0, 40.0 / lam) if lam > 0 else 400.0
        sol = integrate_mode((lambda t, lam=lam: 1.0 + 0.5 * lam ** 2 * t ** 2 - 2.0 / t ** 2), tau_i, 0.01)
        vals = np.array([mode_amplitude(sol, t) * t for t in taus if t <= tau_i])
        ax.plot(taus[taus <= tau_i], vals, color=col, lw=1.6, label=lab)
    ax.set(xscale="log", yscale="log", xlabel="τ = −c k η   (time runs to the right)",
           ylabel="amplitude of the phonon field |δ| (arbitrary units)", title="A fluctuation's amplitude falls, then freezes at the sound horizon")
    ax.invert_xaxis()
    ax.axvline(1.0, color=MUTED, ls=":", lw=1.2)
    ax.text(0.9, 0.04, "sound horizon", transform=ax.get_xaxis_transform(), fontsize=9, color=INK_2, rotation=90, va="bottom", ha="right")
    ax.legend(loc="lower left", fontsize=9)

    ax = axs[0, 1]
    ana = np.array([r[4] for r in tilt_rows])
    mea = np.array([r[3] for r in tilt_rows])
    ax.plot(ana, mea, "o", color=S1, ms=8, label="mode integration")
    xx = np.linspace(min(ana) * 1.05, 0.0, 10)
    ax.plot(xx, xx, color=MUTED, ls="--", lw=1.2, label="n_s − 1 = −2/(p − 1)")
    ax.axhspan(NS - 1 - NS_ERR, NS - 1 + NS_ERR, color=S3, alpha=0.25, lw=0)
    ax.text(-0.205, NS - 1 + 0.012, "observed (Planck 2018)", fontsize=9, color=S3)
    ax.set(xlabel="expected tilt −2/(p − 1) for a ∝ t^p", ylabel="measured tilt n_s − 1",
           title="The mode integration reproduces the tilt formula")
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[1, 0]
    ax.plot(lam_arr, np.abs(corr_arr), "o-", color=S1, ms=7, label="amplitude change")
    ll = np.geomspace(1e-6, 0.7, 40)
    ax.plot(ll, np.abs(corr_arr[-3]) * (ll / lam_arr[-3]) ** slope_l, color=MUTED, ls="--", lw=1.2, label=f"∝ λ^{slope_l:.1f} (extrapolated)")
    ax.axvline(lam_star, color=S2, lw=1.4)
    ax.set(xscale="log", yscale="log", xlim=(5e-7, 1.0), xlabel="graininess λ = Hξ/c",
           ylabel="|change in frozen amplitude|", title="The medium's graininess changes the amplitude only slightly")
    ax.text(lam_star * 1.3, 1e-3, "Planck-length medium\n(plateau expansion)", fontsize=9, color=S2)
    ax.legend(loc="lower right", fontsize=9)

    ax = axs[1, 1]
    cs = np.linspace(0.0, 1.0, 100)
    wgp = (cs ** 2 / 2.0) / (1.0 + cs ** 2 / 2.0)
    ax.plot(cs, wgp, color=S1, lw=2.0, label="repulsive condensate")
    ax.axhspan(-1.05, -1.0 / 3.0, color=S3, alpha=0.18, lw=0)
    ax.axhline(-1 + 2 * eps_needed / 3, color=S2, lw=1.4)
    ax.text(0.02, -0.93, "accelerating expansion (w < −1/3)", fontsize=9, color=S3)
    ax.text(0.02, -1.03, "w = −0.988 needed for the observed tilt", fontsize=9, color=S2, va="top")
    ax.set(xlabel="sound speed of the medium ÷ c", ylabel="equation of state w = P/ρ", ylim=(-1.15, 0.45),
           title="The medium's own pressure cannot drive the expansion")
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    save_fig(fig, NAME, "expansion")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
