"""
r39 - What could drive the long, near-exponential stretching?  (LAB_NOTEBOOK.md entry E47, tests G1-G4)

Question (user): "need much deeper research and exploration" on the open row of the stage-2 table: "Long, near-exponential stretching -
needed, but the medium can't supply it".  r37 only showed that the medium's own pressure gives w >= 0.  Here we ask what kind of
medium COULD give w = -0.988 for ~50-60 e-folds, with a spectrum that fits the sky.

Four independent questions, each a computation:
  G1. A single barotropic medium (pressure fixed by density alone: any zero-temperature superfluid is one) that heads for w = -1.
      Exact identity: d ln(eps)/dN = -3 (c_s^2 - w), eps = 3(1+w)/2, N = ln a.  So slow roll (|d ln eps/dN| << 1) needs c_s^2 = w = -1,
      an imaginary sound speed.  What spectrum does such a medium make instead?  The full mode equation is integrated (not assumed).
  G2. A stretched liquid (tension, pressure < 0).  How negative can w get before the liquid cavitates (spinodal), for a medium whose
      sound speed is c?  A causal bound, then a scan of equation-of-state shapes.
  G3. An open medium that keeps its density by creating new medium as space grows (steady state).  Reasoning only, no number.
  G4. A second sector.  The medium's own phase field has a decay constant F fixed by the r33 mapping; what does a pseudo-Goldstone
      (natural inflation) potential with that F predict for (n_s, r)?

Units: c = hbar = 1, M_Pl = reduced Planck mass = 1, H^2 = rho / 3.  N = ln a is the clock (e-folds).
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r39_what_drives_the_stretching"
NS, NS_ERR = 0.9649, 0.0042       # Planck 2018 tilt
R_LIMIT = 0.036                   # BICEP/Keck 2021 tensor-to-scalar ratio limit (95 %), typed from memory (as in r37)
C_SOUND_HE4, C_SOUND_WATER, C_LIGHT = 238.0, 1480.0, 299792458.0   # m/s, textbook values


# ----------------------------------------------------------------------------------------------------------------------
# G1: barotropic media that approach de Sitter (analytic backgrounds, numerical perturbations)
# ----------------------------------------------------------------------------------------------------------------------
class Attractor:
    """A barotropic medium approaching a de Sitter fixed point, with rho_f = 3 so that H_f = 1.

    kind 'bag':        P = c2 rho - (1 + c2) rho_f   (constant sound speed squared c2; for c2 = 1 it is stiff matter + a constant),
                       rho = rho_f (1 + u), u = u0 exp(-3 (1 + c2) N).
    kind 'chaplygin':  P = -A rho^-alpha, alpha = c2 (the generalised Chaplygin gas, which is what a brane of tension A has for
                       alpha = 1), (rho/rho_f)^(1+alpha) = 1 + u, u = u0 exp(-3 (1 + alpha) N); c_s^2 = alpha / (1 + u).
    N = 0 is the start of accelerated expansion (eps = 1)."""

    def __init__(self, kind, c2):
        self.kind, self.c2 = kind, c2
        self.gamma = 3.0 * (1.0 + c2)
        self.u0 = 2.0 / (1.0 + 3.0 * c2) if kind == "bag" else 2.0

    def u(self, n):
        return self.u0 * math.exp(-self.gamma * n)

    def eps(self, n):
        u = self.u(n)
        pref = 1.5 * (1.0 + self.c2) if self.kind == "bag" else 1.5
        return pref * u / (1.0 + u)

    def w(self, n):
        return -1.0 + 2.0 * self.eps(n) / 3.0

    def cs2(self, n):
        return self.c2 if self.kind == "bag" else self.c2 / (1.0 + self.u(n))

    def eta(self, n):                       # d ln eps / dN, analytic
        return -self.gamma / (1.0 + self.u(n))

    def s(self, n):                         # d ln c_s / dN
        return 0.0 if self.kind == "bag" else 0.5 * self.gamma * self.u(n) / (1.0 + self.u(n))

    def hubble(self, n):
        u = self.u(n)
        return math.sqrt(1.0 + u) if self.kind == "bag" else (1.0 + u) ** (1.0 / (2.0 * (1.0 + self.c2)))


def power_spectrum(bg, n_k, n_end, x_i_min=60.0):
    """Dimensionless spectrum P_zeta(k) = k^3 |zeta|^2 / 2 pi^2 at e-fold n_end for the mode whose sound horizon is crossed at n_k
    (c_s k = a H).  The mode starts at N = 0 in the adiabatic vacuum, which is its true initial state only if it is deep inside the
    horizon then: X(0) = c_s k / (a H) >= x_i_min.  Equation (N = ln a as time, X = c_s k / aH):
        zeta'' + (3 - eps + eta - 2 s) zeta' + X^2 zeta = 0,   zeta = v / z,  z = a sqrt(2 eps) / c_s."""
    k = math.exp(n_k) * bg.hubble(n_k) / math.sqrt(bg.cs2(n_k))
    x0 = math.sqrt(bg.cs2(0.0)) * k / bg.hubble(0.0)
    if x0 < x_i_min:
        raise ValueError(f"mode not deep inside the horizon at the start (X = {x0:.1f})")
    eps0, eta0, s0 = bg.eps(0.0), bg.eta(0.0), bg.s(0.0)
    z0 = math.sqrt(2.0 * eps0) / math.sqrt(bg.cs2(0.0))
    zeta0 = 1.0 / (z0 * math.sqrt(2.0 * math.sqrt(bg.cs2(0.0)) * k))
    dz = (-1j * x0 - 1.0 - eta0 / 2.0 + s0 / 2.0) * zeta0     # WKB: D ln zeta = -iX - s/2 - D ln z, D ln z = 1 + eta/2 - s

    def rhs(n, y):
        fr = 3.0 - bg.eps(n) + bg.eta(n) - 2.0 * bg.s(n)
        x2 = bg.cs2(n) * k * k / (math.exp(n) * bg.hubble(n)) ** 2
        return [y[1], -fr * y[1] - x2 * y[0], y[3], -fr * y[3] - x2 * y[2]]

    sol = solve_ivp(rhs, (0.0, n_end), [zeta0.real, dz.real, zeta0.imag, dz.imag], method="DOP853", rtol=1e-10, atol=1e-30)
    y = sol.y[:, -1]
    return k, k ** 3 * (y[0] ** 2 + y[2] ** 2) / (2.0 * math.pi ** 2)


def measured_tilt(bg, n_lo=5.5, n_hi=11.0, n_modes=9, n_end=18.0):
    ks, ps = [], []
    for n_k in np.linspace(n_lo, n_hi, n_modes):
        k, pk = power_spectrum(bg, n_k, n_end)
        ks.append(k)
        ps.append(pk)
    return np.polyfit(np.log(ks), np.log(ps), 1)[0]


# ----------------------------------------------------------------------------------------------------------------------
# G2: stretched liquids.  Energy density rho = n + E(n) (units m c^2 = 1), pressure P = n E' - E, c_s^2 = dP/drho = n E'' / (1 + E').
# Family E(n) = -a n^q + b n^r with the equilibrium n0 = 1 (P = 0) and c_s(n0) = c fixed; q < r.
# ----------------------------------------------------------------------------------------------------------------------
def liquid(q, r):
    """Coefficients a, b for E = -a n^q + b n^r with P(1) = 0 and c_s^2(1) = 1, or None if they are not positive."""
    denom = (q - 1.0) * (r - q) + q - (q - 1.0) * r / (r - 1.0)
    if abs(denom) < 1e-9:
        return None
    a = 1.0 / denom
    b = a * (q - 1.0) / (r - 1.0)
    return (a, b) if a > 0 and b > 0 else None


def liquid_state(q, r, n):
    a, b = liquid(q, r)
    e = -a * n ** q + b * n ** r
    de = -a * q * n ** (q - 1.0) + b * r * n ** (r - 1.0)
    d2e = -a * q * (q - 1.0) * n ** (q - 2.0) + b * r * (r - 1.0) * n ** (r - 2.0)
    rho = n + e
    p = n * de - e
    return rho, p, n * d2e / (1.0 + de)


def liquid_stretch(q, r):
    """Stretch the liquid from n = 1 downward.  Returns (n_spinodal, w at the spinodal, rho_0/rho_spinodal, e-folds with w < -1/3,
    binding fraction -E(1)/mc^2) or None if the branch is not a sensible liquid (c_s^2 < 0 before the spinodal is a true spinodal; c_s > 1 is rejected)."""
    if liquid(q, r) is None:
        return None
    grid = np.linspace(1.0, 1e-3, 40000)
    rho, p, cs2 = liquid_state(q, r, grid)
    bad = np.where(cs2 <= 0.0)[0]
    if len(bad) == 0:
        return None
    i = bad[0]
    if i < 2 or np.any(rho[:i] <= 0.0) or np.any(cs2[:i] > 1.0 + 1e-9):
        return None
    w = p[:i] / rho[:i]
    j = int(np.argmin(w))
    n_acc = None
    below = np.where(w < -1.0 / 3.0)[0]
    efolds = 0.0
    if len(below):
        n_acc = grid[below[0]]
        efolds = math.log(n_acc / grid[j]) / 3.0     # n falls as a^-3 for a conserved medium
    a, b = liquid(q, r)
    return grid[j], w[j], rho[0] / rho[j], efolds, a - b      # last entry: binding energy per constituent, in units of m c^2


# ----------------------------------------------------------------------------------------------------------------------
# G4: natural inflation, V = L^4 (1 + cos(phi/f)).  Closed forms in f (units of the reduced Planck mass).
# ----------------------------------------------------------------------------------------------------------------------
def natural_inflation(f, n_efolds):
    x_end_half = math.atan(math.sqrt(2.0) * f)                                  # eps = 1
    sin_star = math.sin(x_end_half) * math.exp(-n_efolds / (2.0 * f * f))       # N = 2 f^2 ln(sin(x_e/2) / sin(x*/2))
    x_half = math.asin(sin_star)
    t = math.tan(x_half)
    eps = t * t / (2.0 * f * f)
    cos_x = 1.0 - 2.0 * sin_star ** 2
    eta = -cos_x / (1.0 + cos_x) / (f * f)
    return 1.0 - 6.0 * eps + 2.0 * eta, 16.0 * eps


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)

    # ======================================================================================================
    p.section("G1. A single barotropic medium cannot slow-roll: the identity, and the spectrum it makes instead")
    # ------------------------------------------------------------------------------------------------------
    p("Zero-temperature superfluid: pressure and energy depend on one number (mu), so P = P(rho).  Then d rho / dN = -3 (rho + P) gives")
    p("    d ln(rho + P)/dN = -3 (1 + c_s^2),   d ln rho / dN = -3 (1 + w)   =>   d ln eps / dN = -3 (c_s^2 - w)   [exact].")
    ident_rows = []
    for kind, c2 in (("bag", 1.0), ("bag", 0.5), ("chaplygin", 1.0), ("chaplygin", 0.5)):
        bg = Attractor(kind, c2)
        worst = 0.0
        for n in (0.3, 1.0, 2.0, 4.0):
            h = 1e-5
            num = (math.log(bg.eps(n + h)) - math.log(bg.eps(n - h))) / (2 * h)
            frm = -3.0 * (bg.cs2(n) - bg.w(n))
            worst = max(worst, abs(num - frm), abs(bg.eta(n) - frm))
            # the Friedmann relation eps = -d ln H / dN must hold too
            num_h = -(math.log(bg.hubble(n + h)) - math.log(bg.hubble(n - h))) / (2 * h)
            worst = max(worst, abs(num_h - bg.eps(n)))
        ident_rows.append((kind, c2, worst))
        p(f"    {kind:>9s} c_inf^2 = {c2:.1f}: identity and Friedmann relation checked at four times, worst error {worst:.1e}")
    eta_max_slow = 0.0175
    p(f"    Slow roll that gives n_s - 1 = -0.035 needs |eta| = |d ln eps/dN| <~ {eta_max_slow}: c_s^2 = w - eta/3 = -0.988 +- {eta_max_slow / 3:.3f}, i.e. a NEGATIVE")
    p("    c_s^2: perturbations grow as exp(|c_s| k t) (gradient instability), fastest at the cutoff k ~ 1/xi, i.e. within ~ one Planck time.")
    p("    (A scalar field with a potential is not barotropic: its adiabatic c_a^2 = -1 - 2V'/(3 H phidot) -> -1 in slow roll, while its")
    p("    physical sound speed is 1.  The gap is the non-adiabatic pressure; a one-component T = 0 medium has no such gap.)")
    p("")
    p("What such a medium does instead.  Near its de Sitter fixed point eps ~ exp(-3 (1 + c^2) N) -- an ultra-slow-roll: zeta is NOT frozen")
    p("outside the sound horizon but grows as exp[(3 c^2) N].  Counting that growth, the spectrum is predicted analytically to be")
    p("    n_s - 1 = 3 (1 - c_inf^2),    c_inf = the sound speed at the fixed point.")
    p("Check by integrating the full mode equation  zeta'' + (3 - eps + eta - 2s) zeta' + (c_s k / aH)^2 zeta = 0  from the vacuum (modes")
    p("exiting 5.5-11 e-folds after acceleration starts, power read at N = 18):")
    p(f"    {'medium':>26s} {'c_inf^2':>8s} {'n_s-1 measured':>15s} {'3(1-c_inf^2)':>13s} {'difference':>11s}")
    tilt_rows = []
    cases = [("bag", 0.36), ("bag", 0.64), ("bag", 1.0), ("chaplygin", 0.5), ("chaplygin", 1.0)]
    c2_obs = 1.0 - (NS - 1.0) / 3.0
    cases.append(("bag", c2_obs))
    for kind, c2 in cases:
        bg = Attractor(kind, c2)
        tilt = measured_tilt(bg)
        tilt_rows.append((kind, c2, tilt, 3.0 * (1.0 - c2)))
        label = {"bag": "constant c_s", "chaplygin": "Chaplygin gas (brane)"}[kind]
        p(f"    {label:>26s} {c2:8.4f} {tilt:15.4f} {3.0 * (1.0 - c2):13.4f} {tilt - 3.0 * (1.0 - c2):11.1e}")
    worst_tilt = max(abs(r[2] - r[3]) for r in tilt_rows)
    ns_lo, ns_hi = NS - 2 * NS_ERR, NS + 2 * NS_ERR
    c2_lo, c2_hi = 1.0 - (ns_hi - 1.0) / 3.0, 1.0 - (ns_lo - 1.0) / 3.0
    p(f"    => the formula holds to {worst_tilt:.0e}.  Planck's n_s = {NS} +- {NS_ERR} needs c_inf^2 = {c2_obs:.4f} (2-sigma range {c2_lo:.4f} to {c2_hi:.4f}):")
    p("       a sound speed ABOVE c.  A causal medium (c_s <= c, and c_s = c in the Planck-length mapping) gives n_s >= 1.  For c_s = c the")
    p(f"       spectrum is exactly flat (n_s = 1.0000), which is {(1.0 - NS) / NS_ERR:.1f} sigma from the measurement.")
    p("    Tensors: gravitational waves freeze at exit while zeta keeps growing, so r = 16 eps c_s e^{-2(3 c^2) dN} is far below any limit.")
    p("    Besides, the fixed point is eternal: there is no end of stretching and no reheating in this medium.  It models dark energy, not an")
    p("    inflation that ends.  (Priors: ultra-slow-roll, Kinney 2005; Chaplygin gas, Kamenshchik-Moschella-Pasquier 2001; brane origin,")
    p("    Bilic-Tupper-Viollier 2002; kinetic-driven inflation, Armendariz-Picon-Damour-Mukhanov 1999.)")

    # ======================================================================================================
    p.section("G2. A stretched liquid: how far can tension go before the liquid tears (cavitates)?")
    # ------------------------------------------------------------------------------------------------------
    p("Causal bound.  Start at the equilibrium density rho_0 (P = 0, the vacuum of the liquid) and dilute it.  Since dP = c_s^2 d rho and")
    p("c_s <= c everywhere, P(rho) >= -(rho_0 - rho), so  w = P/rho >= -(rho_0/rho - 1).  w < -1/3 needs rho < (3/4) rho_0; w = -0.988 needs")
    p("rho < 0.50 rho_0 and c_s = c all the way down: the bag equation of state, whose sound speed never drops.  A real liquid's sound speed")
    p("falls to zero at the spinodal.")
    p("Real liquids (rest mass counts in rho): w_min >~ -(c_s/c)^2 x (stretch factor of order 1):")
    for name, cs in (("He-4", C_SOUND_HE4), ("water", C_SOUND_WATER)):
        p(f"    {name:>6s}: c_s = {cs:.0f} m/s  ->  (c_s/c)^2 = {(cs / C_LIGHT) ** 2:.1e}: w stays within ~{(cs / C_LIGHT) ** 2:.0e} of zero.")
    p("    For the Planck-length medium c_s = c, so the bound allows w of order -1; the question is what the shape of P(rho) does.")
    p("")
    p("Scan of shapes E(n) = -a n^q + b n^r (a, b fixed by P(1) = 0 and c_s(1) = c), requiring a stable branch with 0 < c_s^2 <= 1 between")
    p("n = 1 and the spinodal.  w and e-folds with w < -1/3 as n falls (n ~ a^-3):")
    qs = np.linspace(1.01, 6.0, 70)
    rs = np.linspace(1.02, 9.0, 70)
    results = []
    for q in qs:
        for r in rs:
            if r <= q + 0.02:
                continue
            res = liquid_stretch(q, r)
            if res is not None:
                results.append((q, r) + res)           # q, r, n_sp, w_min, stretch, e-folds, binding fraction
    n_forms = len(results)
    p(f"    {len(qs) * len(rs)} (q, r) pairs tried; {n_forms} give a causal, stable stretched liquid with a spinodal.")
    p("    A catch found on the first pass: the most negative w sat in the corner q, r -> 1, where the binding energy per constituent")
    p("    approaches the whole rest-mass energy, rho_0 -> 0, and w = P/rho blows up for a trivial reason.  So the result is reported against")
    p(f"    the binding fraction f_b = -E(1)/(m c^2) (f_b = 0.4 for the quantum-droplet shape; liquid He-4, 7.2 K per atom, has f_b = {7.2 * 8.617e-5 / 3.727e9:.0e}):")
    p(f"    {'f_b <=':>7s} {'shapes':>7s} {'best w at spinodal':>19s} {'stretch':>8s} {'longest w<-1/3 (e-folds)':>25s}")
    fb_cuts = (0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0)
    cut_rows = []
    for cut in fb_cuts:
        sub = [t for t in results if t[6] <= cut]
        if not sub:
            continue
        bst = min(sub, key=lambda t: t[3])
        cut_rows.append((cut, len(sub), bst[3], bst[4], max(t[5] for t in sub)))
        p(f"    {cut:7.2f} {len(sub):7d} {bst[3]:19.3f} {bst[4]:8.2f} {max(t[5] for t in sub):25.3f}")
    reach_third = sum(1 for t in results if t[3] < -1.0 / 3.0)
    reach_988 = sum(1 for t in results if t[3] < -0.988)
    best_e = max(results, key=lambda t: t[5])
    fb_for_third = min((t[6] for t in results if t[3] < -1.0 / 3.0), default=float("nan"))
    p(f"    Forms with w < -1/3 at the spinodal: {reach_third} of {n_forms}, all with f_b >= {fb_for_third:.2f}.  Forms with w < -0.988: {reach_988} of {n_forms}.")
    p(f"    Longest acceleration (w < -1/3) in any shape: {best_e[5]:.3f} e-folds (f_b = {best_e[6]:.2f}) -- needed: >= 50.")
    best = min(results, key=lambda t: t[3])
    p("    Reading: tension strong enough to accelerate needs the equilibrium vacuum energy of the medium to be cancelled to within")
    p(f"    {1.0 - fb_for_third:.0%} of its rest mass -- a vacuum-energy tuning, the cosmological-constant problem again -- and even then")
    p("    the liquid tears after a fraction of one e-fold.")
    ref = liquid_stretch(2.0, 2.5)
    p(f"    Reference (the quantum-droplet shape q = 2, r = 5/2): spinodal at n = {ref[0]:.3f}, w = {ref[1]:.3f}, stretch {ref[2]:.2f}, acceleration {ref[3]:.2f} e-folds.")
    p("    Look-elsewhere count: the grid above is the number of forms tried; only the extremes are quoted.  (The scan covers two-term power")
    p("    laws only; it does not prove no liquid exists.  What it shows is that the causal bound w >= -(rho_0/rho - 1) is not approached.)")
    p("    The medium stretches, cavitates, and the cavities merge: after the spinodal the 'medium' is a foam, not an expanding fluid.")

    # ======================================================================================================
    p.section("G3. An open medium that makes new medium as space grows (reasoning, no number)")
    # ------------------------------------------------------------------------------------------------------
    p("If the density is held fixed by creating medium at a rate Gamma = 3 H per particle, rho = const, w = -1 exactly, de Sitter by")
    p("construction (steady state: Bondi-Gold-Hoyle 1948; irreversible creation pressure: Prigogine et al. 1988).  Two problems remain:")
    p("  (i) eps = 0 exactly, so the medium has no clock of its own: no scalar perturbation exists without a second ingredient;")
    p("  (ii) the creation rate is an input, and creating medium out of nothing is a statement about the hyper-dimensions that is not derived.")
    p("This is the 'space grows by itself' picture; it explains the stretch by assuming it.")

    # ======================================================================================================
    p.section("G4. A second sector: the medium's own phase field as a pseudo-Goldstone (natural inflation)")
    # ------------------------------------------------------------------------------------------------------
    p("The phase theta of the condensate is a free field (shift symmetry) with canonical decay constant F^2 = hbar^2 n / (m c_s^2).")
    p("In the r33 mapping (xi = alpha l_P = hbar/(sqrt2 m c), c_s = c) with n xi^3 the number of constituents in a healing volume (mean-field")
    p("needs n xi^3 >> 1): in Planck units F = 2^(1/4) sqrt(n xi^3)/alpha, and in units of the reduced Planck mass (m_P / sqrt(8 pi)):")
    f_coeff = (8.0 * math.pi) ** 0.5 * 2.0 ** 0.25
    p(f"    F / M_Pl = {f_coeff:.2f} sqrt(n xi^3) / alpha   (an estimate from the mapping, not a measurement; n xi^3 >= 1, alpha ~ 1).")
    p("A potential for the phase needs an explicit U(1)-breaking term (for example a Josephson coupling to a second condensate): V = L^4 (1 + cos(theta)),")
    p("which is natural inflation (Freese-Frieman-Olinto 1990).  Closed-form (n_s, r) at N e-folds before the end:")
    p(f"    {'f/M_Pl':>7s} | {'N = 50: n_s':>12s} {'r':>8s} | {'N = 60: n_s':>12s} {'r':>8s} | verdict at N = 60")
    nat_rows = []
    for f in (3.0, 4.0, 5.0, 5.3, 6.0, 8.0, 10.0, 15.0, 25.0):
        n50 = natural_inflation(f, 50.0)
        n60 = natural_inflation(f, 60.0)
        sig = (n60[0] - NS) / NS_ERR
        ok = (abs(sig) <= 2.0) and n60[1] < R_LIMIT
        nat_rows.append((f, n50, n60, sig, ok))
        p(f"    {f:7.1f} | {n50[0]:12.4f} {n50[1]:8.4f} | {n60[0]:12.4f} {n60[1]:8.4f} | n_s {sig:+.1f} sigma, r {'ok' if n60[1] < R_LIMIT else 'too big'}")
    fs = np.linspace(2.0, 40.0, 761)
    window = [f for f in fs for nn in (50.0, 60.0)
              if abs(natural_inflation(f, nn)[0] - NS) <= 2 * NS_ERR and natural_inflation(f, nn)[1] < R_LIMIT]
    f_r_ok = max((f for f in fs if natural_inflation(f, 60.0)[1] < R_LIMIT), default=None)
    ns_at_edge = natural_inflation(f_r_ok, 60.0)[0] if f_r_ok else float("nan")
    p(f"    Both n_s within 2 sigma and r < {R_LIMIT} (N = 50 or 60): {'no value of f' if not window else f'f = {min(window):.1f} to {max(window):.1f}'}.")
    p(f"    r < {R_LIMIT} needs f <= {f_r_ok:.1f} M_Pl (N = 60), where n_s = {ns_at_edge:.4f} ({(NS - ns_at_edge) / NS_ERR:.1f} sigma low).")
    p(f"    The medium's own F = {f_coeff:.1f} sqrt(n xi^3)/alpha M_Pl is at or above the r bound unless alpha >~ {f_coeff / f_r_ok:.1f} sqrt(n xi^3).")
    p("    Natural inflation therefore sits at the edge of what the data allow, with the medium's F in the right order of magnitude (>~ 5 M_Pl is")
    p("    unusual for a field theory, and here it arrives for free).  But it needs a second sector, a potential nobody derived, and a medium")
    p("    with an explicit phase-breaking term; the amplitude (Lambda) is one free number.")

    # ======================================================================================================
    p.section("Verdict (every number below is computed above)")
    # ------------------------------------------------------------------------------------------------------
    ok_eq = max(r[2] for r in ident_rows)
    verdict = [
        ("G1a: a one-component barotropic medium can slow-roll",
         f"NO: d ln eps/dN = -3(c_s^2 - w) (checked to {ok_eq:.0e}); w = -0.988 needs c_s^2 = -0.988 (imaginary sound speed)"),
        ("G1b: what such a medium makes at its de Sitter fixed point",
         f"n_s - 1 = 3(1 - c_inf^2), integrated to {worst_tilt:.0e}; c_s = c gives n_s = 1.0000 exactly = {(1.0 - NS) / NS_ERR:.1f} sigma from Planck"),
        ("G1c: reproducing n_s = 0.965 with a causal barotropic medium",
         f"NO: needs c_inf^2 = {c2_obs:.4f} > 1 (a signal faster than the medium's own light)"),
        ("G2: a stretched liquid (c_s = c at equilibrium) reaches w < -1/3 before tearing",
         f"ONLY with the vacuum energy cancelled to within {1.0 - fb_for_third:.0%} of the rest mass (f_b >= {fb_for_third:.2f}); at f_b <= 0.5 the best w is "
         f"{[r for r in cut_rows if r[0] == 0.5][0][2]:.3f}; longest acceleration {best_e[5]:.2f} e-folds vs 50 needed; w < -0.988 in {reach_988} of {n_forms} shapes"),
        ("G3: an open medium that creates itself holds de Sitter",
         "BY CONSTRUCTION: w = -1 is put in, and eps = 0 leaves no perturbation clock; not derived (reasoning only)"),
        ("G4: the medium's phase field as natural inflation fits the sky",
         f"MARGINAL: F/M_Pl = {f_coeff:.1f} sqrt(n xi^3)/alpha is the right size, but r < {R_LIMIT} needs f <= {f_r_ok:.1f}, where n_s is {(NS - ns_at_edge) / NS_ERR:.1f} sigma low; needs a second sector"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<72s} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ======================================================================================================
    # Figure
    # ======================================================================================================
    fig, axs = plt.subplots(2, 2, figsize=(12.8, 10.0))

    ax = axs[0, 0]
    xx = np.linspace(0.0, 1.15, 50)
    ax.plot(xx, 3.0 * (1.0 - xx), color=MUTED, ls="--", lw=1.3, label="n_s − 1 = 3(1 − c²)   (analytic)")
    bag = [(r[1], r[2]) for r in tilt_rows if r[0] == "bag"]
    cha = [(r[1], r[2]) for r in tilt_rows if r[0] == "chaplygin"]
    ax.plot(*zip(*bag), "o", color=S1, ms=8, label="constant-c_s medium (mode integration)")
    ax.plot(*zip(*cha), "s", color=S2, ms=8, label="Chaplygin gas = brane (mode integration)")
    ax.axhspan(NS - 1 - 2 * NS_ERR, NS - 1 + 2 * NS_ERR, color=S3, alpha=0.30, lw=0)
    ax.text(0.02, NS - 1 - 0.18, "observed n_s (Planck 2018, 2σ)", fontsize=9, color=S3, va="top")
    ax.axvline(1.0, color=INK_2, lw=1.2, ls=":")
    ax.text(1.0, 2.55, "causal limit\nc_s = c", fontsize=9, color=INK_2, ha="right", va="top")
    ax.set(xlabel="sound speed squared at the de Sitter fixed point, c_s²/c²", ylabel="spectral tilt n_s − 1",
           ylim=(-0.7, 3.0), xlim=(0.0, 1.15), title="A causal one-fluid medium makes n_s ≥ 1; the sky has n_s < 1")
    ax.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(0.97, 0.80))

    ax = axs[0, 1]
    xr = np.linspace(1.0, 0.25, 400)
    ax.plot(xr, 1.0 - 1.0 / xr, color=MUTED, ls="--", lw=1.3, label="causal limit: c_s = c all the way down")
    sub50 = [t for t in results if t[6] <= 0.5]
    best50 = min(sub50, key=lambda t: t[3])
    for (q, r), col, lab in (((2.0, 2.5), S1, "quantum-droplet shape (q=2, r=5/2)"),
                             ((best50[0], best50[1]), S2, f"most negative with f_b ≤ 0.5 (q={best50[0]:.2f}, r={best50[1]:.2f})")):
        grid = np.linspace(1.0, 0.05, 4000)
        rho, pr, cs2 = liquid_state(q, r, grid)
        bad = np.where(cs2 <= 0.0)[0][0]
        rho, pr = rho[:bad], pr[:bad]
        ax.plot(rho / rho[0], pr / rho, color=col, lw=2.0, label=lab)
        ax.plot(rho[-1] / rho[0], pr[-1] / rho[-1], "x", color=col, ms=9, mew=2)
    ax.axhline(-1.0 / 3.0, color=S3, lw=1.3)
    ax.text(0.97, -1.0 / 3.0 - 0.07, "acceleration starts (w = −1/3)", fontsize=9, color=S3, ha="left")
    ax.axhline(-0.988, color=S3, lw=1.3, ls=":")
    ax.text(0.97, -0.988 + 0.03, "w = −0.988 (tilt)", fontsize=9, color=S3, ha="left")
    ax.set(xlim=(1.0, 0.25), ylim=(-1.12, 0.1), xlabel="density of the stretched medium ÷ its equilibrium density",
           ylabel="equation of state w = P/ρ", title="A stretched liquid tears (×) well before w reaches −1/3")
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.42), fontsize=8.5)

    ax = axs[1, 0]
    ax.plot([t[6] for t in results], [t[3] for t in results], ".", color=MUTED, ms=2.5, alpha=0.5, label=f"{n_forms} stretched-liquid shapes")
    fbs = np.linspace(0.02, 1.0, 60)
    env = [min((t[3] for t in results if t[6] <= fb), default=np.nan) for fb in fbs]
    ax.plot(fbs, env, color=S1, lw=2.2, label="most negative w reachable")
    ax.axhline(-1.0 / 3.0, color=S3, lw=1.3)
    ax.text(0.02, -1.0 / 3.0 + 0.03, "acceleration needs w < −1/3", fontsize=9, color=S3)
    ax.axhline(-0.988, color=S3, lw=1.3, ls=":")
    ax.text(0.02, -0.988 + 0.03, "w = −0.988 (tilt)", fontsize=9, color=S3)
    ax.set(xlim=(0, 1.0), ylim=(-1.1, 0.02), xlabel="binding energy ÷ rest-mass energy of a constituent, f_b  (ρ₀ → 0 as f_b → 1)",
           ylabel="w at the spinodal", title="Accelerating tension needs the vacuum energy cancelled")
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.30), fontsize=8.5)

    ax = axs[1, 1]
    fgrid = np.geomspace(2.5, 40.0, 200)
    for nn, col in ((60.0, S1), (50.0, S2)):
        pts = np.array([natural_inflation(f, nn) for f in fgrid])
        ax.plot(pts[:, 0], pts[:, 1], color=col, lw=2.0, label=f"natural inflation, N = {nn:.0f}")
    for f in (3.0, 5.0, 10.0, 25.0):
        pt = natural_inflation(f, 60.0)
        ax.plot(*pt, "o", color=S1, ms=5)
        ax.annotate(f"f = {f:.0f}", pt, textcoords="offset points", xytext=(6, -3), fontsize=8.5, color=INK_2)
    ax.axvspan(NS - 2 * NS_ERR, NS + 2 * NS_ERR, color=S3, alpha=0.25, lw=0)
    ax.axhline(R_LIMIT, color=MUTED, ls="--", lw=1.3)
    ax.text(0.9505, R_LIMIT * 1.12, "r < 0.036", fontsize=9, color=INK_2)
    ax.text(NS + 2 * NS_ERR + 0.0006, 0.0042, "observed n_s\n(Planck 2018, 2σ)", fontsize=9, color=S3)
    ax.set(yscale="log", xlim=(0.945, 0.985), ylim=(0.004, 0.3), xlabel="spectral tilt n_s", ylabel="tensor-to-scalar ratio r",
           title="The medium's own phase field sits at the edge of the data")
    ax.legend(loc="lower left", fontsize=8.5)

    fig.tight_layout()
    save_fig(fig, NAME, "stretching")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
