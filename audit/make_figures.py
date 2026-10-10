"""
Figures for the audit (written to audit/figures/).

Every curve is computed here from the audit modules; nothing is typed in.
  fig_light_speed_anisotropy.png  long-wavelength transverse speed vs direction (FCC, HCP)
  fig_phonon_dispersion.png       FCC [100] branches: longitudinal mode is gapless
  fig_formula_sigma.png           mass/ratio formulas vs measurement, in standard deviations
  fig_look_elsewhere.png          how many same-shape formulas hit random targets
  fig_bell_chsh.png               CHSH for local / nonlocal vortex-cord models
  fig_cavity_range.png            Gross-Pitaevskii cavity: screened, not 1/r
  fig_audit_overview.png          all six panels on one page
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a01_lattice_dynamics as a01  # noqa: E402
import a02_numerology as a02  # noqa: E402
import a03_bell_models as a03  # noqa: E402
import a04_mechanics_checks as a04  # noqa: E402
from common import (alpha, c, eV, m_e_kg, m_e_MeV, m_mu_MeV, m_tau_MeV, mu_pe,  # noqa: E402
                    omega_b_h2, omega_c_h2, planck_mass)

OUT = os.path.join(HERE, "figures")
RED, GREEN, BLUE, GREY, ORANGE = "#c0392b", "#27ae60", "#2c6fbb", "#7f8c8d", "#e67e22"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def lattice_data():
    C11, C12, C44 = a01.fcc_elastic_constants()
    mu_V = (C11 - C12 + 3 * C44) / 5
    v_ref = math.sqrt(mu_V / math.sqrt(2.0))       # the documents set this equal to c
    th = np.linspace(0, 2 * math.pi, 361)
    # FCC: the (1-10) plane contains [001], [111] and [110], i.e. all extreme directions
    u_fcc = np.stack([np.sin(th) / math.sqrt(2), np.sin(th) / math.sqrt(2), np.cos(th)], 1)
    # HCP: elastically transversely isotropic, so a plane through the c-axis shows everything
    u_hcp = np.stack([np.sin(th), np.zeros_like(th), np.cos(th)], 1)
    v_fcc = a01.acoustic_speeds("fcc", u_fcc) / v_ref
    v_hcp = a01.acoustic_speeds("hcp", u_hcp) / v_ref
    # dispersion along FCC [100]
    nbrs = a01.fcc_neighbours()
    zb = 2 * math.pi / math.sqrt(2)
    qf = np.linspace(0, 1, 300)
    w = np.array([np.sqrt(np.clip(np.linalg.eigvalsh(a01.dyn_fcc(np.array([f * zb, 0, 0]), nbrs)), 0, None))
                  for f in qf])
    return dict(th=th, v_fcc=v_fcc, v_hcp=v_hcp, qf=qf, w=w / w[:, 2].max())


def sigma_data():
    """Pull of each formula against measurement, |prediction - measured| / sigma."""
    a = alpha[0]
    mP, dmP = planck_mass()
    me, dme = m_e_kg
    dS = math.hypot(dmP / mP, dme / me)
    rows = []
    for label, pref, S in [
        ("m_e = m_P exp(-3/8a)", 1.0, 3 / (8 * a)),
        ("  x sqrt3/2  (fitted)", math.sqrt(3) / 2, 3 / (8 * a)),
        ("  x exp(+a sqrt12/2pi)  (fitted)", math.sqrt(3) / 2, 3 / (8 * a) - a / (2 * math.pi) * math.sqrt(12)),
    ]:
        rows.append((label, abs(math.log(mP * pref * math.exp(-S) / me)) / dS))
    mu, dmu = mu_pe
    rows.append(("m_p/m_e = 6pi^5 + 3pi a/2", abs(6 * math.pi ** 5 + 1.5 * math.pi * a - mu) / dmu))
    # Koide parametrisation, electron = k=1, muon = k=2, tau = k=0
    e, m, t = m_e_MeV[0], m_mu_MeV, m_tau_MeV

    def from_e(d):
        f = [1 + math.sqrt(2) * math.cos(d + 2 * math.pi * k / 3) for k in (0, 1, 2)]
        v0 = math.sqrt(e) / f[1]
        return (v0 * f[2]) ** 2, (v0 * f[0]) ** 2
    rows.append(("m_mu with delta = 2/9", abs(from_e(2 / 9)[0] - m[0]) / m[1]))
    lo, hi = 0.20, 0.24
    for _ in range(200):
        mid = (lo + hi) / 2
        if (from_e(mid)[0] - m[0]) * (from_e(lo)[0] - m[0]) <= 0:
            hi = mid
        else:
            lo = mid
    rows.append(("m_tau from Koide Q = 2/3", abs(from_e((lo + hi) / 2)[1] - t[0]) / t[1]))

    def Q(tt):
        return (e + m[0] + tt) / (math.sqrt(e) + math.sqrt(m[0]) + math.sqrt(tt)) ** 2
    rows.append(("Koide Q = 2/3 (measured)", abs(Q(t[0]) - 2 / 3) / abs(Q(t[0] + t[1]) - Q(t[0]))))
    R = omega_c_h2[0] / omega_b_h2[0]
    dR = R * math.hypot(omega_c_h2[1] / omega_c_h2[0], omega_b_h2[1] / omega_b_h2[0])
    rows.append(("Omega_c/Omega_b = 5 + 3/8", abs(5.375 - R) / dR))
    return rows


def look_elsewhere_data():
    _, _, T2, base = a02.formula_family()
    rng = np.random.default_rng(1)
    targets = rng.uniform(38, 52, 400)
    rnd = np.array([a02.count_hits(base, T2, x) for x in targets])
    mP, _ = planck_mass()
    MeV = 1e6 * eV / c ** 2
    named = {"e": m_e_MeV[0], r"$\mu$": m_mu_MeV[0], r"$\tau$": m_tau_MeV[0], "p": 938.27208943,
             "W": 80369.2, "Z": 91188.0, "H": 125200.0}
    pts = {k: (math.log(mP / (v * MeV)), a02.count_hits(base, T2, math.log(mP / (v * MeV)))) for k, v in named.items()}
    return targets, rnd, pts


def bell_data():
    th = np.linspace(0, math.pi, 25)
    E_loc = np.array([a03.E_local(0.0, x) for x in th])
    S = [("local phase-locked\nvortex (computed)", a03.chsh(a03.E_local)),
         ("nonlocal cord +\nQM rule typed in", a03.chsh(a03.E_cord_qm)),
         ("nonlocal cord +\nother rule", a03.chsh(a03.E_cord_pr)),
         ("paper's own\narithmetic", a03.chsh(lambda x, y: -math.cos(x - y), a03.PAPER_B_ANG))]
    return th, E_loc, S


def cavity_data():
    sol = a04.solve_gp_cavity()
    r = np.linspace(0.5, 18, 600)
    drho = sol.sol(r)[0] ** 2 - 1
    tail = (r > 5) & (r < 16)
    k, b = np.polyfit(r[tail], np.log(-drho[tail] * r[tail]), 1)
    return r, drho, k, b


# ---------------------------------------------------------------------------
# Panels (each draws into a given axis)
# ---------------------------------------------------------------------------
def panel_anisotropy(ax, L, which="fcc"):
    v = L["v_fcc"] if which == "fcc" else L["v_hcp"]
    th = L["th"]
    ax.plot(th, np.ones_like(th), color=GREY, ls="--", lw=1.4, label="what Lorentz invariance needs (= c)")
    ax.plot(th, v[:, 0], color=RED, lw=2, label="slow transverse wave")
    ax.plot(th, v[:, 1], color=ORANGE, lw=2, label="fast transverse wave")
    ax.set_rlim(0.6, 1.2)
    ax.set_rticks([0.8, 1.0, 1.2])
    ax.set_yticklabels(["0.8c", "c", "1.2c"], fontsize=8)
    ax.set_xticklabels([])
    lo, hi = v[:, :2].min(), v[:, :2].max()
    name = "FCC" if which == "fcc" else "HCP"
    ax.set_title(f"{name} Planck lattice: speed of 'light' by direction\n"
                 f"{lo:.2f}c to {hi:.2f}c (bound on anisotropy: ~1e-17)", fontsize=10, fontweight="bold")


def panel_dispersion(ax, L):
    qf, w = L["qf"], L["w"]
    ax.plot(qf, w[:, 2], color=RED, lw=2.2, label="longitudinal (compression)")
    ax.plot(qf, w[:, 0], color=BLUE, lw=2.2, label="transverse x2 ('light')")
    ax.axhline(1.0, color=GREY, ls=":", lw=1.2)
    ax.text(0.02, 1.03, "band TOP = 4.2e19 GeV (called a 'gap' in the paper)", fontsize=8, color=GREY)
    ax.annotate("no gap: frequency -> 0\nas wavelength grows", xy=(0.01, 0.01), xytext=(0.06, 0.66),
                arrowprops=dict(arrowstyle="->", color=RED), fontsize=8.5, color=RED, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel(r"wavevector $q/q_X$ along [100]")
    ax.set_ylabel(r"frequency $\omega/\omega_{max}$")
    ax.set_title("Phonon branches: the longitudinal mode is gapless\n"
                 "(a 500 nm longitudinal wave would carry ~4.3 eV)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)


def panel_sigma(ax, rows):
    labels = [r[0] for r in rows][::-1]
    vals = np.array([r[1] for r in rows][::-1])
    cols = [GREEN if v < 1 else (ORANGE if v < 5 else RED) for v in vals]
    y = np.arange(len(vals))
    ax.barh(y, np.maximum(vals, 0.05), color=cols)
    for yi, v in zip(y, vals):
        ax.text(max(v, 0.05) * 1.15, yi, f"{v:,.2f}" if v < 10 else f"{v:,.0f}", va="center", fontsize=8)
    ax.axvline(1, color=GREEN, ls="--", lw=1)
    ax.axvline(5, color=RED, ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_xlim(0.05, 1e5)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("distance from measurement (standard deviations)")
    ax.set_title("Mass formulas vs measurement\n(green < 1 sigma, red > 5 sigma = excluded)",
                 fontsize=10, fontweight="bold")


def panel_look_elsewhere(ax, targets, rnd, pts):
    ax.scatter(targets, rnd, s=9, color=GREY, alpha=0.55, label="400 random numbers")
    for k, (x, n) in pts.items():
        ax.scatter([x], [n], s=60, color=RED, zorder=5)
        ax.annotate(k, (x, n), xytext=(4, 4), textcoords="offset points", fontsize=10, color=RED)
    ax.set_xlabel(r"target $\ln(m_P/m)$")
    ax.set_ylabel("formulas of the USRT shape that 'hit' it")
    frac = 100 * np.mean(rnd > 0)
    ax.set_title(f"Look-elsewhere test: 3.2 million same-shape formulas\n"
                 f"{frac:.0f}% of RANDOM numbers also get a 'derivation'", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)


def panel_bell(ax, S):
    names = [s[0] for s in S]
    vals = [s[1] for s in S]
    cols = [BLUE, ORANGE, RED, GREY]
    ax.bar(range(len(vals)), vals, color=cols, width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(2.0, color="k", ls="--", lw=1)
    ax.axhline(2 * math.sqrt(2), color=GREEN, ls="--", lw=1.2)
    ax.text(3.05, 2.08, "local (classical)\nlimit 2", fontsize=8, ha="center")
    ax.text(3.05, 2 * math.sqrt(2) + 0.08, "quantum\nmechanics 2.83", fontsize=8, ha="center", color=GREEN)
    ax.set_xlim(-0.5, 3.7)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(names, fontsize=7.5)
    ax.set_ylim(0, 4.5)
    ax.set_ylabel("CHSH  S")
    ax.set_title("Bell test of the vortex-cord idea (Monte Carlo)\n(2.83 only appears when QM is typed in)",
                 fontsize=10, fontweight="bold")


def panel_bell_curve(ax, th, E_loc):
    x = np.linspace(0, math.pi, 200)
    ax.plot(x, -np.cos(x), color=GREEN, lw=2.2, label=r"quantum mechanics $-\cos\theta$ (experiment)")
    ax.plot(th, E_loc, "o", color=BLUE, ms=5, label="local vortex model (simulated)")
    ax.set_xlabel(r"angle between detectors $\theta$")
    ax.set_ylabel(r"correlation $E(\theta)$")
    ax.set_xticks([0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi])
    ax.set_xticklabels(["0", r"$\pi/4$", r"$\pi/2$", r"$3\pi/4$", r"$\pi$"])
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
    ax.set_title("Correlation curves", fontsize=10, fontweight="bold")


def panel_cavity(ax, r, drho, k, b):
    ax.semilogy(r, -drho, color=BLUE, lw=2.4, label="Gross-Pitaevskii cavity (solved)")
    ax.semilogy(r, np.exp(b + k * r) / r, color=RED, ls="--", lw=1.4,
                label=rf"fit $e^{{{k:.3f}\,r}}/r$  (theory $-\sqrt{{2}}$)")
    ref = -drho[np.argmin(abs(r - 2))] * 2 / r
    ax.semilogy(r, ref, color=GREEN, ls=":", lw=2, label="1/r (what Newtonian gravity needs)")
    ax.set_ylim(1e-9, 2)
    ax.set_xlabel("distance r (healing lengths)")
    ax.set_ylabel(r"density dip $|\delta\rho|/\rho_0$")
    ax.set_title("'Cavitation gravity': the dip is screened\n(short range, not Newton's 1/r)",
                 fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.3, which="both")


# ---------------------------------------------------------------------------
def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(path, os.path.dirname(HERE)))


def main():
    os.makedirs(OUT, exist_ok=True)
    plt.rcParams.update({"font.size": 9})
    L = lattice_data()
    rows = sigma_data()
    targets, rnd, pts = look_elsewhere_data()
    th, E_loc, S = bell_data()
    r, drho, k, b = cavity_data()

    fig = plt.figure(figsize=(11, 5))
    panel_anisotropy(fig.add_subplot(1, 2, 1, projection="polar"), L, "fcc")
    panel_anisotropy(ax := fig.add_subplot(1, 2, 2, projection="polar"), L, "hcp")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(-0.1, -0.05), ncol=3)
    save(fig, "fig_light_speed_anisotropy.png")

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    panel_dispersion(ax, L)
    save(fig, "fig_phonon_dispersion.png")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    panel_sigma(ax, rows)
    save(fig, "fig_formula_sigma.png")

    fig, ax = plt.subplots(figsize=(7, 4.8))
    panel_look_elsewhere(ax, targets, rnd, pts)
    save(fig, "fig_look_elsewhere.png")

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    panel_bell_curve(axs[0], th, E_loc)
    panel_bell(axs[1], S)
    save(fig, "fig_bell_chsh.png")

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    panel_cavity(ax, r, drho, k, b)
    save(fig, "fig_cavity_range.png")

    fig = plt.figure(figsize=(18, 10.5))
    panel_anisotropy(ax := fig.add_subplot(2, 3, 1, projection="polar"), L, "hcp")
    ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    panel_dispersion(fig.add_subplot(2, 3, 2), L)
    panel_cavity(fig.add_subplot(2, 3, 3), r, drho, k, b)
    panel_sigma(fig.add_subplot(2, 3, 4), rows)
    panel_look_elsewhere(fig.add_subplot(2, 3, 5), targets, rnd, pts)
    panel_bell(fig.add_subplot(2, 3, 6), S)
    fig.suptitle("USRT independent audit: what the computations actually give", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save(fig, "fig_audit_overview.png")


if __name__ == "__main__":
    main()
