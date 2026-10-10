"""
r08 - How gravity could come into existence in the substrate  (LAB_NOTEBOOK.md entry E12)

Question (user): "How would gravity be happening and come into existence and behave in our
universal substrate ... how would a particle affect the substrate?"

Hypothesis tested here (not assumed true): trapped energy makes the substrate locally
'softer', lowering its local wave speed c(x).  Writing c(x)^2 = c^2 (1 + 2 Phi(x)/c^2):

A. Universal free fall.  Two different particle species (kinks of a sine-Gordon substrate with
   internal frequency w0 = 1 and w0 = 3, so rest energies 8 and 24) are released in the same
   'slow' region.  Kink energy = 8 w0 c(x), so force = -8 w0 c', inertial mass = 8 w0 / c and
   acceleration = -c c' = -Phi'  -- independent of w0.  Simulated vs point-particle prediction.
B. Light delay.  A massless pulse crossing the same region arrives late by int (1/c - 1) dx
   (the 1D analogue of the Shapiro delay).
C. Gravity between particles.  Each particle lowers c around itself in proportion to its
   energy (a long-range kernel of range L, PUT IN BY HAND here).  Two species attract; check
   that each acceleration is set by the OTHER particle's energy (Newton) and M1 a1 = M2 a2.
D. 3D: why light bends by the full GR amount.  If trapped energy changes the substrate's
   electric AND magnetic stiffness equally (eps = mu = K), light bends 1.75" and the local
   impedance (hence alpha) is unchanged.  If only one changes, light bends half as much and
   alpha would vary with gravitational potential -- excluded by atomic clocks.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.signal import lfilter  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import G0, INK_2, MUTED, S1, S2, S3, Report, c, save_fig, style  # noqa: E402

NAME = "r08_gravity_from_wave_speed"
H, DT = 0.05, 0.02
X = np.arange(-150.0, 150.0, H)
XH = 0.5 * (X[1:] + X[:-1])


def div_c2_grad(p, c2h):
    flux = c2h * (p[1:] - p[:-1]) / H
    out = np.zeros_like(p)
    out[1:-1] = (flux[1:] - flux[:-1]) / H
    return out


def kink_pos(p):
    i = np.where((p[:-1] - np.pi) * (p[1:] - np.pi) < 0)[0]
    if len(i) == 0:
        return np.nan
    i = i[0]
    return X[i] + H * (np.pi - p[i]) / (p[i + 1] - p[i])


def static_kink(w0, x0, c2_at):
    return 4 * np.arctan(np.exp(w0 * (X - x0) / math.sqrt(c2_at)))


# ---------------------------------------------------------------- A, B: imposed slow region
EPS, W = 0.01, 20.0


def Phi(x):
    return -EPS * np.exp(-x ** 2 / (2 * W * W))


def dPhi(x):
    return EPS * x / W ** 2 * np.exp(-x ** 2 / (2 * W * W))


def fall(w0, x0=30.0, T=300.0):
    c2h = 1 + 2 * Phi(XH)
    phi = static_kink(w0, x0, 1 + 2 * Phi(x0))
    dphi = np.zeros_like(X)
    a = div_c2_grad(phi, c2h) - w0 ** 2 * np.sin(phi)
    ts, xs = [], []
    for n in range(int(T / DT) + 1):
        if n % 50 == 0:
            ts.append(n * DT)
            xs.append(kink_pos(phi))
        dphi += 0.5 * DT * a
        phi += DT * dphi
        a = div_c2_grad(phi, c2h) - w0 ** 2 * np.sin(phi)
        dphi += 0.5 * DT * a
    return np.array(ts), np.array(xs)


def particle(x0=30.0, T=300.0):
    xx, v, ts, xs = x0, 0.0, [], []
    for n in range(int(T / DT) + 1):
        if n % 50 == 0:
            ts.append(n * DT)
            xs.append(xx)
        v -= dPhi(xx) * DT
        xx += v * DT
    return np.array(ts), np.array(xs)


def pulse_arrival(with_region):
    c2h = 1 + 2 * Phi(XH) if with_region else np.ones_like(XH)
    u = np.exp(-((X + 100) / 2.0) ** 2)
    du = -np.gradient(u, H)                       # right-moving pulse
    a = div_c2_grad(u, c2h)
    probe = np.argmin(abs(X - 100))
    best, tbest = 0.0, 0.0
    for n in range(int(220 / DT)):
        du += 0.5 * DT * a
        u += DT * du
        a = div_c2_grad(u, c2h)
        du += 0.5 * DT * a
        if u[probe] > best:
            best, tbest = u[probe], (n + 1) * DT
    return tbest


# ---------------------------------------------------------------- C: self-consistent attraction
def smooth_exp(e, L):
    """Convolution with K(s) = exp(-|s|/L)/(2L) via two exact recursive passes (O(N))."""
    r = math.exp(-H / L)
    b = [H / (2 * L)]
    fwd = lfilter(b, [1, -r], e)
    bwd = lfilter(b, [1, -r], e[::-1])[::-1]
    return fwd + bwd - e * H / (2 * L)


def mutual(kappa=0.2, L=60.0, d=40.0, T=150.0):
    w = (1.0, 3.0)
    x0 = (-d / 2, d / 2)
    phis = [static_kink(w[i], x0[i], 1.0) for i in range(2)]
    dphis = [np.zeros_like(X) for _ in range(2)]

    def energy_density(c2):
        e = np.zeros_like(X)
        for i in range(2):
            gx = np.gradient(phis[i], H)
            e += 0.5 * dphis[i] ** 2 + 0.5 * c2 * gx ** 2 + w[i] ** 2 * (1 - np.cos(phis[i]))
        return e

    c2 = np.ones_like(X)
    for _ in range(5):                            # settle the initial self-consistent field
        Psi = -kappa * smooth_exp(energy_density(c2), L)
        c2 = 1 + 2 * Psi
    for i in range(2):
        phis[i] = static_kink(w[i], x0[i], np.interp(x0[i], X, c2))
    out = []
    accs = [None, None]
    for n in range(int(T / DT) + 1):
        if n % 5 == 0:
            Psi = -kappa * smooth_exp(energy_density(c2), L)
            c2 = 1 + 2 * Psi
            c2h = 0.5 * (c2[1:] + c2[:-1])
        if n % 50 == 0:
            E = [np.sum(0.5 * dphis[i] ** 2 + 0.5 * c2 * np.gradient(phis[i], H) ** 2
                        + w[i] ** 2 * (1 - np.cos(phis[i]))) * H for i in range(2)]
            out.append((n * DT, kink_pos(phis[0]), kink_pos(phis[1]), E[0], E[1]))
        for i in range(2):
            if accs[i] is None:
                accs[i] = div_c2_grad(phis[i], c2h) - w[i] ** 2 * np.sin(phis[i])
            dphis[i] += 0.5 * DT * accs[i]
            phis[i] += DT * dphis[i]
            accs[i] = div_c2_grad(phis[i], c2h) - w[i] ** 2 * np.sin(phis[i])
            dphis[i] += 0.5 * DT * accs[i]
    return np.array(out)


def main():
    p = Report(NAME)
    style(plt)

    p.section("A. Universal free fall in a region where the substrate's wave speed is lower")
    p(f"slow region: c^2 = 1 + 2 Phi, Phi = -{EPS} exp(-x^2 / 2 {W:g}^2)  (imposed here)")
    falls = {}
    for w0 in (1.0, 3.0):
        falls[w0] = fall(w0)
        p(f"species w0 = {w0:g} (rest energy {8 * w0:g}, mass ratio {w0:g}): position at t = 300: {falls[w0][1][-1]:.4f}")
    tp, xp = particle()
    diff = np.nanmax(np.abs(falls[1.0][1] - falls[3.0][1]))
    p(f"largest difference between the two species' paths: {diff:.1e}  (fall distance {30 - falls[1.0][1][-1]:.2f})")
    p(f"point particle with acceleration -dPhi/dx: position at t = 300: {xp[-1]:.4f}")
    p("=> every particle made of substrate waves falls the same way, whatever its mass: the")
    p("   equivalence principle EMERGES, because a particle's energy and its inertia both scale with c(x).")
    p("   The effective potential is Phi = (c(x)^2 - c^2)/2, i.e. gravity = a map of the local wave speed.")

    p.section("B. A massless pulse crossing the slow region arrives late")
    t0, t1 = pulse_arrival(False), pulse_arrival(True)
    pred = quad(lambda x: 1 / math.sqrt(1 + 2 * Phi(x)) - 1, -100, 100)[0]
    p(f"arrival without / with the slow region: {t0:.3f} / {t1:.3f} -> delay {t1 - t0:.3f}; "
      f"prediction int(1/c - 1)dx = {pred:.3f}")
    p("   (1D analogue of the Shapiro delay; in 3D the same idea gives the measured 247 us for Mars radar, r01)")

    p.section("C. Gravity between two particles: each particle slows the substrate around itself")
    kappa, L, d = 0.2, 60.0, 40.0
    m = mutual(kappa, L, d)
    t, x1, x2, E1, E2 = m.T
    early = t <= 80
    a1 = 2 * np.polyfit(t[early], x1[early], 2)[0]
    a2 = 2 * np.polyfit(t[early], x2[early], 2)[0]
    E1m, E2m = E1[early].mean(), E2[early].mean()
    pa1 = kappa * E2m * math.exp(-d / L) / (2 * L * L)
    pa2 = kappa * E1m * math.exp(-d / L) / (2 * L * L)
    p(f"kernel strength kappa = {kappa}, range L = {L:g} (put in by hand), initial separation {d:g}")
    p(f"particle 1 (rest energy {E1m:.2f}): acceleration {a1:+.2e}  (prediction from particle 2's energy: +{pa1:.2e})")
    p(f"particle 2 (rest energy {E2m:.2f}): acceleration {a2:+.2e}  (prediction from particle 1's energy: -{pa2:.2e})")
    p(f"each is pulled TOWARD the other; a1/a2 = {abs(a1 / a2):.2f} vs E2/E1 = {E2m / E1m:.2f}  (Newton: the pull on")
    p(f"each body is set by the OTHER body's mass);  M1 a1 + M2 a2 = {E1m * a1 + E2m * a2:+.1e} (action = reaction)")
    p("Honest limits: the long-range kernel is imposed (a gapless mediator is needed, r09), and this is a")
    p("scalar model: it gives Newtonian gravity and clock slowing, not spin-2 waves (r03) or the factor 2 below.")

    p.section("D. 3D: the full light bending requires eps = mu (impedance matching)")
    GM = G0 * 1.98847e30 / c ** 2
    b = 6.957e8
    rad2as = 180 / math.pi * 3600

    def deflect(k):
        # n(r) = 1 + k GM/(r c^2); deflection = int dn/db dz along the straight path
        # substitute z = b u so the integrand is O(1): int b dz/(b^2+z^2)^1.5 = (1/b) int du/(1+u^2)^1.5
        return k * GM / b * quad(lambda u: (1 + u * u) ** -1.5, -np.inf, np.inf)[0] * rad2as
    p(f"eps = mu = K = 1 + 2GM/rc^2 -> n = K:        deflection {deflect(2):.4f} arcsec (GR: 1.7512; VLBI confirms GR to ~1e-4)")
    p(f"eps = K, mu = 1           -> n = sqrt(K):  deflection {deflect(1):.4f} arcsec (half: excluded)")
    U = G0 * 1.98847e30 / c ** 2 * (1 / 1.471e11 - 1 / 1.521e11)
    p("local impedance Z = Z0 sqrt(mu/eps): unchanged if eps = mu, so local physics (alpha = e^2 Z0/2h) is")
    p("identical everywhere -- that IS the equivalence principle for electromagnetically bound matter.")
    p(f"if eps != mu: alpha would track the Sun's potential at Earth, which changes by {U:.1e} over the year;")
    p("  atomic-clock comparisons bound that coupling at the ~1e-6 level or below (e.g. Leefer et al. 2013),")
    p("  so a mismatched response (coupling ~1) is excluded by about a million.")
    p("=> requirement on the substrate: trapped energy must change its electric and magnetic stiffness")
    p("   equally. Conjecture: this is automatic if the loop condensate is symmetric between electric and")
    p("   magnetic loops (electric-magnetic duality). In GR the same fact is Plebanski's (1960) result that")
    p("   gravity acts on light like a medium with eps_ij = mu_ij.")

    # ---------- figures
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))
    axs[0].plot(tp, xp, color=MUTED, lw=4, alpha=0.6, label="point particle, a = -dPhi/dx")
    axs[0].plot(falls[1.0][0], falls[1.0][1], color=S1, label="particle species 1 (mass 8)")
    axs[0].plot(falls[3.0][0], falls[3.0][1], color=S2, ls=(0, (4, 3)), label="species 2 (mass 24, 3x heavier)")
    axs[0].set(xlabel="time", ylabel="position", title="Different masses fall identically")
    axs[0].legend(loc="lower left", fontsize=8.5)
    tt = t
    axs[1].plot(tt, x1 - x1[0], color=S1, label=f"particle 1 (energy {E1m:.0f})")
    axs[1].plot(tt, x2 - x2[0], color=S2, label=f"particle 2 (energy {E2m:.0f})")
    axs[1].plot(tt, 0.5 * pa1 * tt ** 2, color=S1, ls=":", lw=1.5)
    axs[1].plot(tt, -0.5 * pa2 * tt ** 2, color=S2, ls=":", lw=1.5)
    axs[1].axhline(0, color=MUTED, lw=0.8)
    axs[1].set(xlabel="time", ylabel="displacement (1 moves right, 2 moves left)",
               title="Two particles attract (dotted: Newton-type prediction)")
    axs[1].legend(loc="lower left", fontsize=8.5)
    vals = [deflect(1), deflect(2)]
    axs[2].bar([0, 1], vals, color=[MUTED, S3], width=0.55)
    axs[2].axhline(1.7512, color=MUTED, ls="--", lw=1)
    axs[2].text(-0.27, 1.79, "measured 1.751\"", color=INK_2, fontsize=9, ha="left")
    for i, v in enumerate(vals):
        axs[2].text(i, v / 2, f"{v:.3f}\"", ha="center", color="white", fontweight="bold")
    axs[2].set_xticks([0, 1])
    axs[2].set_xticklabels(["only electric stiffness\nchanges (eps = K, mu = 1)", "both change equally\n(eps = mu = K)"])
    axs[2].set(ylabel="light bending at the Sun's edge (arcsec)", ylim=(0, 2.1),
               title="Full bending needs eps = mu")
    axs[2].grid(axis="x", visible=False)
    fig.tight_layout()
    save_fig(fig, NAME, "emergent_gravity")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
