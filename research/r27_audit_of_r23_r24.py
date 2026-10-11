"""
r27 - Independent audit of the parallel (Gemini) work r23 and r24
(LAB_NOTEBOOK.md entry E37)

Question (user): "i had gemini working symultanousely locally as well so check these as well"

Method: every claim in r23 (fermion spin and g = 2) and r24 (causal-set growth, Kleitman-Rothschild
suppression, 3+1 selection) is re-tested with a calculation that does not reuse the thing being tested.
  A. r23-B: the Calugareanu-White-Fuller check in r23 is circular (Tw is *defined* as Lk - Wr). Test the
     theorem for real: Wr from the Gauss integral, Tw from an explicit ribbon frame, Lk from an integer
     crossing count of the ribbon's two edges.
  B. r23-D: the "equipartition gives g = 2" argument. Algebra (sympy), a quadrature of the angular
     momentum of poloidal flow, and the Schwinger bookkeeping.
  C. r23-E: knot census versus "three generations".
  D. r24: the critical coupling beta_c = 2 ln 2. Re-derive it, put back the Benincasa-Dowker term the
     script prints but then drops, and extend from the single Kleitman-Rothschild point to the whole
     layered family.
  E. r24: the 3+1 "selection" list, checked dimension by dimension.
"""
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import ALPHA, INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402
from r24_causal_set_growth_and_4d_emergence import (  # noqa: E402
    generate_kr_ensemble, sprinkle_minkowski_ensemble)

NAME = "r27_audit_of_r23_r24"
KAPPA = 4.0 / math.sqrt(6.0)            # Benincasa-Dowker 4D prefactor, as printed in r24
G_E_EXP = 2.00231930436256              # the value typed into r23 (this is the CODATA 2018 number)


# ----------------------------------------------------------------------------------------------------------
# A. ribbon geometry: writhe, twist and linking number computed independently
# ----------------------------------------------------------------------------------------------------------
def curve(A, M, a=0.4, k=3):
    """The deformation family used in r23: a 3-lobed curve lifted out of the plane by A."""
    t = np.linspace(0, 2 * np.pi, M, endpoint=False)
    return np.stack([(1 + a * np.cos(k * t)) * np.cos(t), (1 + a * np.cos(k * t)) * np.sin(t),
                     A * np.sin(k * t)], axis=1)


def segments(P):
    Q = np.roll(P, -1, axis=0)
    return Q - P, 0.5 * (P + Q)


def writhe(P):
    """Gauss double integral, midpoint rule over segment pairs (adjacent pairs contribute exactly 0)."""
    s, m = segments(P)
    d = m[:, None, :] - m[None, :, :]
    r2 = np.einsum("ijk,ijk->ij", d, d)
    np.fill_diagonal(r2, np.inf)
    cr = np.cross(s[:, None, :], s[None, :, :])
    return float(np.sum(np.einsum("ijk,ijk->ij", cr, d) / r2 ** 1.5) / (4 * np.pi))


def gauss_link(P, Q):
    s1, m1 = segments(P)
    s2, m2 = segments(Q)
    d = m1[:, None, :] - m2[None, :, :]
    r2 = np.einsum("ijk,ijk->ij", d, d)
    cr = np.cross(s1[:, None, :], s2[None, :, :])
    return float(np.sum(np.einsum("ijk,ijk->ij", cr, d) / r2 ** 1.5) / (4 * np.pi))


def rotate(v, axis, ang):
    axis = axis / np.linalg.norm(axis)
    return (v * math.cos(ang) + np.cross(axis, v) * math.sin(ang)
            + axis * np.dot(axis, v) * (1 - math.cos(ang)))


def minimal_rotation(v, a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    cr = np.cross(a, b)
    s = np.linalg.norm(cr)
    return v.copy() if s < 1e-14 else rotate(v, cr, math.atan2(s, np.dot(a, b)))


def bishop_frame(P):
    """Parallel-transported normal along the polygon (zero twist). Returns tangents, frame, holonomy angle."""
    s, _ = segments(P)
    T = s / np.linalg.norm(s, axis=1)[:, None]
    M = len(P)
    U0 = np.array([0.0, 0.0, 1.0])
    U0 = U0 - np.dot(U0, T[0]) * T[0]
    U0 /= np.linalg.norm(U0)
    U = np.zeros((M + 1, 3))
    U[0] = U0
    for i in range(M):
        U[i + 1] = minimal_rotation(U[i], T[i], T[(i + 1) % M])
    delta = math.atan2(np.dot(np.cross(U0, U[M]), T[0]), np.dot(U0, U[M]))
    return T, U, delta


def closed_frame(T, U, phi_total):
    """Add a uniform extra rotation about the tangent so that the frame closes: total angle phi_total."""
    M = len(T)
    return np.array([rotate(U[i], T[i], phi_total * i / M) for i in range(M)])


def twist(T, U):
    """Tw = (1/2pi) closed-integral (T x U) . dU, discretised."""
    M = len(T)
    tot = 0.0
    for i in range(M):
        j = (i + 1) % M
        Um = U[i] + U[j]
        Um = Um - np.dot(Um, T[i]) * T[i]
        Um /= np.linalg.norm(Um)
        tot += np.dot(np.cross(T[i], Um), U[j] - U[i])
    return tot / (2 * np.pi)


def crossing_link(P, Q, seed=1):
    """Linking number of two disjoint closed polygons as half the signed crossing count in a generic
    projection. An integer by construction and independent of Wr and Tw."""
    rng = np.random.default_rng(seed)
    w = rng.normal(size=3)
    w /= np.linalg.norm(w)
    a = np.cross(w, [1.0, 0.3, 0.2])
    a /= np.linalg.norm(a)
    b = np.cross(w, a)

    def proj(X):
        return np.stack([X @ a, X @ b, X @ w], axis=1)

    p, q = proj(P), proj(Q)
    p2, q2 = np.roll(p, -1, axis=0), np.roll(q, -1, axis=0)
    d1, d2 = (p2 - p)[:, None, :2], (q2 - q)[None, :, :2]
    r = q[None, :, :2] - p[:, None, :2]
    den = d1[..., 0] * d2[..., 1] - d1[..., 1] * d2[..., 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (r[..., 0] * d2[..., 1] - r[..., 1] * d2[..., 0]) / den
        u = (r[..., 0] * d1[..., 1] - r[..., 1] * d1[..., 0]) / den
    ok = (den != 0) & (s >= 0) & (s < 1) & (u >= 0) & (u < 1)
    tot = 0
    for i, j in zip(*np.nonzero(ok)):
        hp = p[i, 2] + s[i, j] * (p2[i, 2] - p[i, 2])
        hq = q[j, 2] + u[i, j] * (q2[j, 2] - q[j, 2])
        da, db = p2[i, :2] - p[i, :2], q2[j, :2] - q[j, :2]
        cr = (da[0] * db[1] - da[1] * db[0]) if hp > hq else (db[0] * da[1] - db[1] * da[0])
        tot += 1 if cr > 0 else -1
    return tot / 2.0


def vertex_rule_writhe(r):
    """The writhe routine of r23, reproduced (vertex rule, M = 300)."""
    n = len(r)
    dr = np.roll(r, -1, axis=0) - r
    wr = 0.0
    for i in range(n):
        diff = r[i] - r
        dist3 = np.linalg.norm(diff, axis=1) ** 3
        dist3[i] = np.inf
        wr += float(np.sum(np.sum(np.cross(dr[i], dr) * diff, axis=1) / dist3))
    return wr / (4.0 * np.pi)


# ----------------------------------------------------------------------------------------------------------
# D. layered posets
# ----------------------------------------------------------------------------------------------------------
def layered_poset(N, dens, rng):
    """Three layers N/4, N/2, N/4; each possible edge between neighbouring layers present with prob dens.
    dens = 1/2 is the Kleitman-Rothschild poset."""
    n1, n2 = N // 4, N // 2
    n3 = N - n1 - n2
    a = (rng.random((n1, n2)) < dens).astype(np.float32)
    b = (rng.random((n2, n3)) < dens).astype(np.float32)
    R = np.zeros((N, N), np.float32)
    R[:n1, n1:n1 + n2] = a
    R[n1:n1 + n2, n1 + n2:] = b
    R[:n1, n1 + n2:] = ((a @ b) > 0).astype(np.float32)
    return R


def bd_counts(R):
    N = R.shape[0]
    interior = R @ R
    rel = R > 0
    n = [int(np.sum(rel & (interior == k))) for k in range(4)]     # links, 1, 2, 3 interior elements
    return n[0], n[1], n[2], n[3], KAPPA * (N - n[0] + 9 * n[1] - 16 * n[2] + 8 * n[3])


def log_choose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def main():
    p = Report(NAME)
    style(plt)
    t_start = time.time()

    # ======================================================================================================
    p.section("A. r23-B: is the Calugareanu-White-Fuller check in r23 a test?")
    p("r23 computes Wr, then SETS Tw = Lk_exact - Wr and prints Lk = Wr + Tw. That returns Lk_exact for ANY Wr.")
    wr_true = writhe(curve(0.48, 800))
    for label, wr in (("converged Wr (A = 0.48)", wr_true), ("deliberately wrong Wr = +0.70", 0.70),
                      ("absurd Wr = +1000", 1000.0)):
        tw = 1.0 - wr
        p(f"   r23 pipeline, {label:<30}: Tw = {tw:+10.4f}, Lk = Wr + Tw = {wr + tw:.16f}   |Lk - 1| = {abs(wr + tw - 1):.1e}")
    p("   => 'Lk conserved to 2.2e-16' is floating-point rounding of 1 - Wr + Wr. It is not evidence for the theorem.")
    p("   (On this Linux machine the same r23 script printed d(Lk) = 1.11e-16 at A = 0.32 where the Windows run printed 0.)")
    wr_vertex = vertex_rule_writhe(curve(0.48, 300))
    p(f"   r23's writhe routine uses a vertex rule: Wr(A=0.48) = {wr_vertex:+.4f} at M = 300; "
      f"converged midpoint value {wr_true:+.4f} (difference {abs(wr_vertex - wr_true):.4f}, "
      f"{100 * abs(wr_vertex - wr_true) / abs(wr_true):.2f} %).")

    p("")
    p("Real test. Ribbon = centre curve C plus its push-off C' = C + eps*U (eps = 0.02), same family as r23:")
    p("   r(t) = ((1 + 0.4 cos 3t) cos t, (1 + 0.4 cos 3t) sin t, A sin 3t), M = 800 segments.")
    p("   Wr : Gauss double integral of C (midpoint rule).")
    p("   Tw : (1/2pi) closed-integral of (T x U).dU for an explicit ribbon frame U, built by parallel transport")
    p("        plus a uniform extra rotation, with the integer part tracked continuously in A (the ribbon is deformed")
    p("        continuously, starting from the planar ribbon with Tw = 1).")
    p("   Lk : half the signed crossing count between C and C' in a generic projection (an integer).")
    p("   The three are computed with no reference to one another; then Lk - Tw - Wr is the test of the theorem.")
    M = 800
    eps = 0.02
    phi_prev = 2 * np.pi * 1.0
    A_grid = np.round(np.arange(0.0, 0.8001, 0.04), 2)
    rows = []
    for A in A_grid:
        P = curve(A, M)
        T, U, delta = bishop_frame(P)
        n = round((phi_prev + delta) / (2 * np.pi))
        phi = -delta + 2 * np.pi * n
        phi_prev = phi
        Uc = closed_frame(T, U, phi)
        closure = np.linalg.norm(rotate(U[M], T[0], phi) - U[0])
        Wr = writhe(P)
        Tw = twist(T, Uc)
        Q = P + eps * Uc
        Lk = crossing_link(P, Q)
        rows.append((A, Wr, Tw, Lk, Tw + Wr - Lk, closure))
    p(f"   {'A':>5} {'Wr':>10} {'Tw':>10} {'Tw+Wr':>10} {'Lk (crossings)':>15} {'Tw+Wr-Lk':>10}")
    for r in rows:
        if abs((r[0] / 0.16) - round(r[0] / 0.16)) < 1e-9:
            p(f"   {r[0]:5.2f} {r[1]:+10.5f} {r[2]:+10.5f} {r[1] + r[2]:+10.5f} {r[3]:15.1f} {r[4]:+10.2e}")
    max_res = max(abs(r[4]) for r in rows)
    lk_all = sorted({r[3] for r in rows})
    p(f"   max |Tw + Wr - Lk| over {len(rows)} deformation steps = {max_res:.1e};  Lk takes the values {lk_all};  "
      f"max frame-closure error = {max(r[5] for r in rows):.1e}")
    p(f"   Over the sweep Wr changes by {rows[-1][1] - rows[0][1]:+.3f} and Tw by {rows[-1][2] - rows[0][2]:+.3f}: "
      "writhe really is traded for twist.")
    p("   Convergence of the residual with the number of segments M (A = 0.48; the integer branch of the frame is")
    p("   tracked from A = 0 in 12 steps at each M):")
    conv = []
    for Mq in (100, 200, 400, 800, 1600):
        phi_c = 2 * np.pi
        for Ai in np.linspace(0.0, 0.48, 13):
            Ti, Ui, di = bishop_frame(curve(Ai, Mq))
            phi_c = -di + 2 * np.pi * round((phi_c + di) / (2 * np.pi))
        P = curve(0.48, Mq)
        T, U, delta = bishop_frame(P)
        Uc = closed_frame(T, U, phi_c)
        res = twist(T, Uc) + writhe(P) - crossing_link(P, P + eps * Uc)
        conv.append((Mq, res))
        p(f"      M = {Mq:5d}:  Tw + Wr - Lk = {res:+.2e}")
    p(f"   the residual falls from {abs(conv[0][1]):.0e} (M = {conv[0][0]}) to {abs(conv[-1][1]):.0e} (M = {conv[-1][0]}); it is not")
    p("   monotone because the Wr and Tw discretisation errors have different signs. It is discretisation error.")
    p("   Verdict A: the THEOREM and the writhe-for-twist exchange in r23's table are TRUE (now checked: residual "
      f"<= {max_res:.0e}); r23's own check proved nothing, and its Wr is ~0.2 % off.")
    A_curve = np.array([r[0] for r in rows])
    Wr_curve = np.array([r[1] for r in rows])
    Tw_curve = np.array([r[2] for r in rows])
    Lk_curve = np.array([r[3] for r in rows])
    res_curve = np.array([r[4] for r in rows])

    # ======================================================================================================
    p.section("B. r23-D: does equipartition give g = 2 and spin hbar/2?")
    q, c_, Mm, R, f, hb = sp.symbols("q c M R f hbar", positive=True)
    mu = q * c_ * R / 2                       # charge q circling at speed c on radius R
    J = f * Mm * c_ * R                       # angular momentum of the fraction f of the energy that circles
    R_sol = sp.solve(sp.Eq(J, hb / 2), R)[0]  # quantise J = hbar/2
    g_expr = sp.simplify((mu / ((q / (2 * Mm)) * J)).subs(R, R_sol))
    p(f"   mu = q c R / 2 ;  J = f M c R ;  J = hbar/2  =>  R = {R_sol} ;  g = mu / [(q/2M) J] = {g_expr}  (sympy)")
    p("   So g = 1/f: the 'derivation' is the choice f = 1/2 (half the energy circulating, half 'poloidal').")
    p(f"   f = 1   -> g = 1 (bare loop);   f = 1/2 -> g = 2 exactly;   measured g_e = {G_E_EXP:.11f} needs f = "
      f"{1 / G_E_EXP:.6f} ({100 * (0.5 - 1 / G_E_EXP) / 0.5:.3f} % below 1/2).")
    p("   Equipartition is assumed, not derived; with it g = 2 comes out because 1/f = 2 was put in.")
    # poloidal flow carries no angular momentum about the symmetry axis
    Rmaj, a_min, v0 = 1.0, 0.3, 1.0
    nr, nth, nph = 40, 80, 160
    rr = (np.arange(nr) + 0.5) / nr * a_min
    th = (np.arange(nth) + 0.5) / nth * 2 * np.pi
    ph = (np.arange(nph) + 0.5) / nph * 2 * np.pi
    RR, TH, PH = np.meshgrid(rr, th, ph, indexing="ij")
    rho = Rmaj + RR * np.cos(TH)
    X, Y = rho * np.cos(PH), rho * np.sin(PH)
    dm = RR * rho                                        # uniform density volume element (constant factors dropped)
    vx = v0 * (-np.sin(TH) * np.cos(PH))                 # poloidal flow e_theta (meridional plane)
    vy = v0 * (-np.sin(TH) * np.sin(PH))
    Lz_pol = np.sum(dm * (X * vy - Y * vx))
    tx, ty = -np.sin(PH) * v0, np.cos(PH) * v0           # toroidal flow e_phi
    Lz_tor = np.sum(dm * (X * ty - Y * tx))
    p(f"   Quadrature over a torus (R = {Rmaj}, minor radius {a_min}): L_z(poloidal flow) / L_z(toroidal flow, same speed) "
      f"= {Lz_pol / Lz_tor:+.1e}")
    p("   A poloidal (around-the-tube) flow lies in the meridional plane, so rho*v_phi = 0 and it adds NOTHING to J_z.")
    p("   r23 counts it as a second hbar/2. Its own formula S_pol = (E_pol/c^2) r0 c equals hbar/2 only if the tube")
    p("   radius r0 equals the major radius R = hbar/(Mc); for a thin torus S_pol = (hbar/2)(r0/R):")
    for ratio in (1.0, 0.3, 0.1):
        p(f"      r0/R = {ratio:3.1f}:  S_pol = {0.5 * ratio:.2f} hbar")
    a_s = ALPHA / (2 * math.pi)
    g_schw = 2 * (1 + a_s)
    p(f"   Schwinger term: 2(1 + alpha/2pi) = {g_schw:.10f}; residual to the measured g_e = {g_schw - G_E_EXP:+.3e}. This is")
    p("   textbook QED (1948). r23 attributes it to 'substrate gauge fluctuations (computed in r02)'; r02 contains no")
    p("   g-2 calculation (searched: no 'schwinger', 'anomal' or 'g-2' in r01-r22). '99.85 % explained' is QED's credit.")
    p("   Constants: the number typed into r23 as 'CODATA 2022' (2.00231930436256) is the CODATA 2018 value; CODATA 2022 is")
    p("   2.00231930436092(36) (from memory: a_e = 1.15965218046(18)e-3 gives exactly that; not re-fetched). Effect: 1.6e-12.")
    p("   Verdict B: the numbers g = 1 (bare loop) and the Schwinger arithmetic are right; 'g = 2 identically from")
    p("   geometry' is NOT derived (g = 1/f with f = 1/2 assumed), the spin accounting double-counts, and Schwinger is QED's.")

    # ======================================================================================================
    p.section("C. r23-E: do prime knots explain 'exactly three generations'?")
    census = {3: 1, 4: 1, 5: 2, 6: 3, 7: 7, 8: 21, 9: 49, 10: 165, 11: 552, 12: 2176, 13: 9988}
    p("   Prime knots by minimal crossing number (Hoste-Thistlethwaite-Weeks census; OEIS A002863):")
    cum = 0
    cum_list = []
    for n_, k_ in census.items():
        cum += k_
        cum_list.append(cum)
        p(f"      {n_:2d} crossings: {k_:5d} knots   (cumulative {cum:6d})")
    p("   r23 takes 3_1, 4_1, 5_1 and stops. But 5_1 shares its crossing number with 5_2, and 6 crossings has 3 knots,")
    p("   7 has 7, 8 has 21: the count grows exponentially with no gap to end a 'low-lying' list at three.")
    m_ratio = {"mu": 105.6583755 / 0.51099895, "tau": 1776.93 / 0.51099895}
    rope = {"e": 32.74, "mu": 42.44, "tau": 47.39}                         # as typed in r23 (not re-verified)
    x_mu = math.log(m_ratio["mu"]) / math.log(rope["mu"] / rope["e"])
    x_tau = math.log(m_ratio["tau"]) / math.log(rope["tau"] / rope["e"])
    p(f"   Mass ratios m_mu/m_e = {m_ratio['mu']:.1f}, m_tau/m_e = {m_ratio['tau']:.1f}; ropelengths (as typed in r23) "
      f"{rope['e']}, {rope['mu']}, {rope['tau']} differ by factors 1.30 and 1.45.")
    p(f"   A power law m ~ L^x would need x = {x_mu:.1f} (muon) and x = {x_tau:.1f} (tau). That is a diagnostic, not a fit:")
    p("   no soliton energy scales as the 21st power of ropelength, and two numbers with one free exponent test nothing.")
    p("   Verdict C: the mapping e,mu,tau <-> 3_1,4_1,5_1 is a labelling, not a result. r23's own 'open' status stands;")
    p("   the sentence 'provides a clean topological rationale for exactly three generations' should be withdrawn.")

    # ======================================================================================================
    p.section("D. r24: the critical coupling beta_c = 2 ln 2 and 'KR posets are crushed'")
    s_kr = math.log(2) / 4
    p("   D1. What the script's number is. Weight exp(-beta*N1) only; KR entropy (ln2/4) N^2, links N^2/8:")
    p(f"       log-weight(KR) per N^2 = ln2/4 - beta/8, zero at beta = 2 ln 2 = {2 * math.log(2):.4f};  "
      f"at beta = 1.5, N = 256 the exponent is (beta - 2ln2) N^2/8/ln10 = "
      f"{(1.5 - 2 * math.log(2)) * 256 ** 2 / 8 / math.log(10):.1f} decades.  (r24 prints 404.5: reproduced.)")
    p("       This compares the single point p = 1/2 against zero and uses NO Benincasa-Dowker term.")

    p("   D2. Put back the BD term that r24 itself prints. Samples (r24's own samplers; 4 KR, 3 sprinklings):")
    N_list = (32, 64, 128, 256)
    kr, m4 = {}, {}
    for N in N_list:
        kr[N] = generate_kr_ensemble(N, reps=4)
        m4[N] = sprinkle_minkowski_ensemble(4, N, reps=3)
    p(f"       {'N':>4} {'N1(KR)':>9} {'S_BD(KR)':>10} {'S_BD/N^2':>9} | {'N1(4D)':>8} {'S_BD(4D)':>9}")
    for N in N_list:
        p(f"       {N:4d} {kr[N]['mean_links']:9.1f} {kr[N]['mean_sbd']:10.1f} {kr[N]['mean_sbd'] / N ** 2:9.4f} | "
          f"{m4[N]['mean_links']:8.1f} {m4[N]['mean_sbd']:9.1f}")
    p(f"       S_BD(KR)/N^2 -> -kappa/8 = -{KAPPA / 8:.4f}  (kappa = 4/sqrt6 = {KAPPA:.4f}); entropy term ln2/4 = {s_kr:.4f}.")
    p("       The BD term is LARGER than the entropy term, and in r24's own weight exp(-S_BD - beta*N1) it has the")
    p("       sign that ENHANCES KR (S_BD < 0). The honest threshold for that weight is")
    beta_A = 2 * math.log(2) + KAPPA
    p(f"           beta_c(A) = 8(ln2/4 + kappa/8) = 2 ln 2 + 4/sqrt6 = {beta_A:.4f}   (not 1.3863).")
    p("       With the opposite overall sign of the action (the convention in which the continuum phase exists):")
    beta_B = 2 * math.log(2) - KAPPA
    p(f"           beta_c(B) = 2 ln 2 - 4/sqrt6 = {beta_B:+.4f} < 0: the BD term alone already beats the entropy, narrowly "
      f"({8 * (KAPPA / 8 - s_kr):.3f} N^2/8).")
    beta0 = 1.5
    N = 256
    s_man = log_choose(N * (N - 1) // 2, int(round(m4[N]["mean_links"])))
    p(f"       At beta = {beta0}, N = {N}, KR against the sampled 4D class (N1 = {m4[N]['mean_links']:.0f}, S_BD = {m4[N]['mean_sbd']:.0f}):")
    lwA_kr = s_kr * N ** 2 - kr[N]["mean_sbd"] - beta0 * kr[N]["mean_links"]
    lwA_4d_max = s_man - m4[N]["mean_sbd"] - beta0 * m4[N]["mean_links"]           # entropy at its upper bound
    ratio_A = (lwA_kr - lwA_4d_max) / math.log(10)
    p(f"         convention A, r24's stated weight exp(-S_BD - beta N1): even if the 4D class has the largest entropy any class")
    p(f"            with its link count can have (ln C(N(N-1)/2, N1) = {s_man:.0f} nats), log10(W_KR / W_4D) >= {ratio_A:+.0f}.")
    lwB_kr = s_kr * N ** 2 + kr[N]["mean_sbd"] - beta0 * kr[N]["mean_links"]
    lwB_4d_min = m4[N]["mean_sbd"] - beta0 * m4[N]["mean_links"]                     # entropy at its lower bound, 0
    ratio_B = (lwB_kr - lwB_4d_min) / math.log(10)
    p(f"         convention B, exp(+S_BD - beta N1): even if the 4D class has entropy 0, log10(W_KR / W_4D) <= {ratio_B:+.0f}.")
    p("       r24 reports -404.5, which is neither. Whether KR is enhanced or suppressed depends on a sign convention that")
    p("       r24 never fixes, and in the convention it states KR wins by thousands of decades at its own example point.")
    p("       (The 4D class's S_BD fluctuates by several hundred between runs, still far below the N^2 terms.)")

    p("   D3. The whole layered family. Three layers N/4, N/2, N/4 with edge density d between neighbouring layers:")
    p("       number of such posets ~ exp[(N^2/4) H2(d)], links N1 = d N^2/4 (KR is d = 1/2). With weight")
    p("       exp(-beta_eff*N1), log W = (N^2/4)[H2(d) - beta_eff d], maximised at d* = 1/(1+e^beta_eff):")
    p("           max_d = ln(1 + e^(-beta_eff)) > 0   for EVERY finite beta_eff.")
    p(f"       {'beta_eff':>9} {'d*':>8} {'ln(1+e^-b)':>11} {'KR point ln2 - b/2':>19}")
    for b in (0.0, 1.0, 2 * math.log(2), 1.5, 3.0, 5.0, 8.0):
        p(f"       {b:9.3f} {1 / (1 + math.exp(b)):8.4f} {math.log1p(math.exp(-b)):11.4f} {math.log(2) - b / 2:19.4f}")
    p("       The exact KR point (d = 1/2) does go negative beyond beta = 2 ln 2, but the maximum moves to a thinner")
    p("       layered poset and stays positive: the N^2 entropy of the layered family is never removed at fixed beta.")
    p("       Sampled check that BD reduces to a pure link action on dense layered posets (N = 1024):")
    rng = np.random.default_rng(7)
    dens_pts = []
    for dens in (0.5, 0.3, 0.2):
        vals = [bd_counts(layered_poset(1024, dens, rng)) for _ in range(3)]
        sbd_n2 = np.mean([v[4] for v in vals]) / 1024 ** 2
        dens_pts.append((dens, sbd_n2))
        p(f"         d = {dens}: S_BD/N^2 = {sbd_n2:+.4f}   link-action value -kappa*d/4 = {-KAPPA * dens / 4:+.4f}")
    p("       (For thin layers, d <~ N^(-1/2), the 2-, 3-, 4-step intervals matter and S_BD is dominated by large")
    p("       fluctuations; that regime is where the nonlocal smearing of the action is needed.)")
    p(f"       In the two conventions the dense-layer BD action is -kappa*N1, so beta_eff = beta - kappa (A) or beta + kappa (B),")
    p(f"       kappa = {KAPPA:.4f}; either way beta_eff is finite and ln(1 + e^-beta_eff) > 0.")
    N_ref = 256
    c4 = m4[N_ref]["mean_links"] / (N_ref * math.log(N_ref) ** 3)

    def log_choose_big(n, k):                       # k << n form, avoids lgamma cancellation at huge n
        return k * (math.log(n / k) + 1.0) - 0.5 * math.log(2 * math.pi * k)

    def crossover(b):
        grid = np.unique(np.round(np.logspace(2, 12, 4000)).astype(float))
        last = -1
        for idx, N_ in enumerate(grid):
            n1 = c4 * N_ * math.log(N_) ** 3
            lw_lay = N_ ** 2 / 4 * math.log1p(math.exp(-b))
            lw_man = log_choose_big(N_ * (N_ - 1) / 2, n1) - b * n1
            if lw_man >= lw_lay:
                last = idx
        return None if last < 0 else grid[min(last + 1, len(grid) - 1)]

    p("       Where the layered family overtakes the 4D class for good. N1(4D) = c N ln^3 N with c fitted at N = 256 "
      f"(c = {c4:.3f}),")
    p("       4D entropy at its upper bound ln C(N^2/2, N1) (the true manifold entropy is far smaller, so these N are upper")
    p("       limits on the crossover), 4D weight exp(-beta*N1). ILLUSTRATIVE: the N ln^3 N law is assumed.")
    for b in (1.5, 3.0, 5.0, 8.0):
        Nc = crossover(b)
        p(f"         beta = {b}: beyond N ~ {Nc:.1e} the layered family wins even with the 4D class at maximal entropy"
          if Nc else f"         beta = {b}: the layered family is above the 4D class at every N >= 100")
    p("       So a fixed link coupling cannot make the continuum limit manifold-like; the coupling would have to grow")
    p("       like ln N. (Literature, from abstracts only; arXiv is blocked in this container: Loomis & Carlip handle")
    p("       the two-level orders; Mathur, Singh & Surya find the link action suppresses KR orders; Carlip, Carlip &")
    p("       Surya extend this to ALL layered sets, 'given a suitable discretization length' of the nonlocal action.)")
    p("   D4. Citation: r24/E33 cite 'Loomis & Carlip, Phys. Rev. D 98, 086003 (2018)'. The paper is Class. Quantum")
    p("       Grav. 35, 024002 (2018), arXiv:1709.00064, on bilayer orders. It does not show that 'the naive BD action is")
    p("       unbounded from below on KR posets, so KR dominates'; it argues the opposite, that suitable parameters")
    p("       suppress them. 'Proof of Loomis & Carlip' in r24 is a misattribution.")
    heights = [(N, m4[N]["mean_height"]) for N in N_list]
    slope_h = math.log(heights[-1][1] / heights[0][1]) / math.log(N_list[-1] / N_list[0])
    slope_g = math.log(6.6 / 3.1) / math.log(8.0)                     # r24's own printed heights 3.1 ... 6.6
    p(f"   D5. Height of 4D sprinklings, N = 32..256: this run L = {', '.join(f'{h:.1f}' for _, h in heights)} "
      f"(local log-log slope {slope_h:.2f});")
    p(f"       r24's run L = 3.1, 4.0, 5.2, 6.6 (slope {slope_g:.2f}). Both exceed the asymptotic 0.25: N = 256 is not in the")
    p("       asymptotic regime, so the figure label 'L ~ N^(1/4)' is a statement about N >> 10^3 that r24 did not test.")

    # ======================================================================================================
    p.section("E. r24: is 3+1 'selected'? The criteria, dimension by dimension")
    p("   Criteria listed in r24 plus two standard ones (spatial dimension D; spacetime d = D + 1):")
    crit = [
        ("circle can be knotted", lambda D: D == 3),
        ("knotted codim-2 membrane S^(D-2) exists", lambda D: D >= 3),
        ("Weyl tensor nonzero (graviton), d >= 4", lambda D: D >= 3),
        ("Huygens sharp propagation (odd D >= 3)", lambda D: D >= 3 and D % 2 == 1),
        ("Maxwell conformal (d = 4)", lambda D: D == 3),
        ("stable atoms/orbits (D <= 3, Ehrenfest)", lambda D: D <= 3),
    ]
    Ds = list(range(1, 9))
    p("   " + f"{'criterion':<44}" + " ".join(f"D={D}" for D in Ds))
    table = []
    for name, fn in crit:
        table.append([fn(D) for D in Ds])
        p("   " + f"{name:<44}" + " ".join(f"{'yes' if fn(D) else ' . ':>3}" for D in Ds))
    sets = {
        "r24's four criteria": [0, 2, 3, 4],
        "graviton + Huygens + knotted membranes": [1, 2, 3],
        "graviton + Huygens + stable atoms": [2, 3, 5],
    }
    for label, idx in sets.items():
        ok = [D for j, D in enumerate(Ds) if all(table[i][j] for i in idx)]
        p(f"   intersection, {label:<38}: D = {ok}")
    p("   Reading: 'circle knots' and 'Maxwell conformal' are each single-dimension statements that point at D = 3 by")
    p("   construction. Without them, graviton + Huygens + knotted membranes leave every odd D >= 3; adding 'atoms are")
    p("   stable' (D <= 3) gives D = 3. That is the Ehrenfest (1917) / Tegmark (1997) argument, which r24 does not cite.")
    p("   No dimension-dependent quantity was computed in r24 (the link action does not know d), so the sentence 'the")
    p("   regularized causal path sum ... uniquely selects d = 3+1' is not a result of the simulation.")

    # ======================================================================================================
    p.section("Verdict")
    verdict = [
        ("r23 A: bare loop gives L = hbar, mu = mu_B, g = 1", "REPRODUCED (an identity)"),
        ("r23 B: Lk = Tw + Wr, writhe traded for twist", f"TRUE, but r23's check is circular; tested here (<= {max_res:.0e})"),
        ("r23 C: 4pi belt period => spin 1/2", "ASSUMED: closed-form SU(2) matrix; FR gives permission, not necessity"),
        ("r23 D: equipartition => g = 2 identically", "NOT DERIVED: g = 1/f, f = 1/2 put in; poloidal J_z = 0"),
        ("r23 D: Schwinger 2(1 + alpha/2pi), 99.85 %", "QED's result, not the substrate's"),
        ("r23 E: 3_1, 4_1, 5_1 <-> e, mu, tau", "LABELLING: 4 knots with <= 5 crossings, no gap, no mass law"),
        ("r24 A: KR links N^2/8, r = 3/8, height 3, S_BD -> -0.204 N^2", "REPRODUCED"),
        ("r24 D: beta_c = 2 ln 2 cures the BD instability", "NOT ESTABLISHED: drops the BD term; the layered family survives"),
        ("r24 E: 3+1 uniquely selected", "NOT COMPUTED: argument list; known as Ehrenfest-Tegmark"),
    ]
    for claim, status in verdict:
        p(f"   {claim:<62} -> {status}")
    p(f"   runtime {time.time() - t_start:.0f} s")

    # ------------------------------------------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------------------------------------------
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 9.2))

    ax = axs[0, 0]
    ax.plot(A_curve, Wr_curve, "-", color=S1, label="writhe Wr (Gauss integral)")
    ax.plot(A_curve, Tw_curve, "-", color=S2, label="twist Tw (ribbon frame)")
    ax.plot(A_curve, Lk_curve, "o", color=S3, ms=6, label="Lk (integer crossing count)")
    ax.plot(A_curve, Tw_curve + Wr_curve, "--", color=MUTED, lw=1.3, label="Tw + Wr")
    ax.set(xlabel="lift amplitude A", ylabel="topological index",
           title="Călugăreanu–White–Fuller, tested independently")
    ax.text(0.03, 0.04, f"max |Tw + Wr − Lk| = {max_res:.1e}\n(r23 'checked' Lk = (1 − Wr) + Wr)",
            transform=ax.transAxes, fontsize=8.5, color=INK_2, va="bottom")
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.40), fontsize=8.5)

    ax = axs[0, 1]
    fgrid = np.linspace(0.3, 1.05, 200)
    ax.plot(fgrid, 1 / fgrid, color=S1, label="g = 1/f (algebra)")
    ax.plot([1.0], [1.0], "o", color=MUTED, ms=8)
    ax.annotate("bare loop f = 1, g = 1", (1.0, 1.0), xytext=(0.62, 1.12), fontsize=8.5, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.plot([0.5], [2.0], "s", color=S2, ms=8, label="equipartition f = 1/2 (assumed)")
    ax.axhline(G_E_EXP, color=MUTED, ls="--", lw=1.1)
    ax.text(0.60, G_E_EXP + 0.08, "measured electron g = 2.0023", fontsize=8.5, color=INK_2)
    ax.text(0.61, 2.75, f"g_e needs f = {1 / G_E_EXP:.5f}\n(0.116 % below ½): not predicted",
            fontsize=8.5, color=INK_2)
    ax.set(xlabel="fraction f of the energy that circulates", ylabel="g = μ / [(q/2M) J]", ylim=(0.7, 3.6),
           title="r23's g = 2 is the choice f = ½")
    ax.legend(loc="upper right", fontsize=8.5)

    ax = axs[1, 0]
    bgrid = np.linspace(-1.0, 6.0, 300)
    ax.plot(bgrid, np.log1p(np.exp(-bgrid)), color=S1, label="best layered poset: ln(1 + e^−β) > 0")
    ax.plot(bgrid, math.log(2) - bgrid / 2, color=S2, label="KR point (density ½): ln 2 − β/2")
    ax.axhline(0, color=MUTED, lw=1.0)
    ax.axvline(2 * math.log(2), color=MUTED, ls="--", lw=1.1)
    ax.text(2 * math.log(2) + 0.1, -1.25, "β = 2 ln 2\n(r24's β_c)", fontsize=8.5, color=INK_2)
    ax.set(xlabel="effective link coupling β", ylabel="log-weight per N²/4", ylim=(-1.6, 1.4),
           title="Past β = 2 ln 2 the KR point loses; the layered family does not")
    ax.legend(loc="upper right", fontsize=8.5)

    ax = axs[1, 1]
    ns = list(census.keys())
    ax.bar(ns, [census[n_] for n_ in ns], color=S1, width=0.7, label="prime knots with n crossings")
    ax.set_yscale("log")
    ax.plot(ns, cum_list, "o-", color=S2, lw=1.6, ms=5, label="cumulative count")
    for n_ in (3, 4, 5):
        ax.bar([n_], [census[n_]], color=S3, width=0.7)
    ax.text(3.0, 120, "green: the crossing numbers r23 uses\n(n = 5 holds two knots; one is used)", fontsize=8.5, color=INK_2)
    ax.set(xlabel="crossing number n", ylabel="number of prime knots",
           title="No gap after three: the knot list keeps growing")
    ax.legend(loc="upper left", fontsize=8.5, bbox_to_anchor=(0.0, 0.85))

    fig.tight_layout()
    save_fig(fig, NAME, "audit")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
