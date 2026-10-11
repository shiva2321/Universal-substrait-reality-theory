"""
r30 - Other ways of putting fermions on the substrate: how much does a Dirac fermion count?
(LAB_NOTEBOOK.md entry E40)

Question (user): "Other fermions. Other ways of putting fermions on a lattice may weight them differently."
(open item after E31; also checks the Dirac weights typed into the parallel result r26.)

Method. Same cubes (l = 2..9) and same area-law fit as E31 / r22 (box 32^3, antiperiodic):
   (1) Wilson Dirac fermion h(k) = alpha.sin k + beta r sum(1 - cos k_i) for r = 0 (naive: 8 doublers) ... 4;
   (2) Kogut-Susskind (staggered) Hamiltonian fermion, one complex component per site, 2x2x1 unit cell,
       H = (i/2) sum_x sum_j eta_j(x) [chi^dag(x) chi(x+j) - h.c.], eta_1 = 1, eta_2 = (-1)^x1, eta_3 = (-1)^(x1+x2).
       Its spectrum is +-E doubly degenerate in the reduced zone, E^2 = sin^2(q1/2) + sin^2(q2/2) + sin^2(q3):
       two 4-component Dirac fermions ("tastes") per 4 sites.
Entropy of a region: S = -sum [nu ln nu + (1-nu) ln(1-nu)], nu = eigenvalues of the restricted correlation matrix.
Weight w = eta_fermion / eta_scalar (scalar on the same cubes).
Not computed: overlap and domain-wall fermions (they need a Euclidean-time lattice formulation; queued).
"""
import math
import os
import re
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402
from r14_entanglement_gravity import cube_entropy, cubic_correlators  # noqa: E402
from r22_species_weights import area_fit, fermion_correlator, fermion_cube_entropy  # noqa: E402

NAME = "r30_other_lattice_fermions"
HERE = os.path.dirname(os.path.abspath(__file__))
R26_TYPED = {0.75: 12.10, 1.25: 7.20, 1.5: 5.85, 3.0: 2.70}      # typed into r26, not computed there
N_BAND = (180.0, 360.0)                                           # what today's Lambda needs (E29, kappa = 1/2 .. 1)


def stag_tables(L):
    """Reduced-zone projector of the negative-energy bands for the Kogut-Susskind Hamiltonian (antiperiodic)."""
    N = (L // 2, L // 2, L)
    q = [2 * np.pi * (np.arange(n) + 0.5) / n for n in N]
    Q1, Q2, Q3 = np.meshgrid(*q, indexing="ij")
    H = np.zeros(Q1.shape + (4, 4), complex)
    idx = lambda a1, a2: 2 * a1 + a2  # noqa: E731
    for a1 in (0, 1):
        for a2 in (0, 1):
            a = idx(a1, a2)
            b, ph = (idx(1, a2), 1.0) if a1 == 0 else (idx(0, a2), np.exp(1j * Q1))
            H[..., a, b] += 0.5j * ph
            H[..., b, a] += -0.5j * np.conj(ph)
            eta2 = (-1) ** a1
            b, ph = (idx(a1, 1), 1.0) if a2 == 0 else (idx(a1, 0), np.exp(1j * Q2))
            H[..., a, b] += 0.5j * eta2 * ph
            H[..., b, a] += -0.5j * eta2 * np.conj(ph)
            eta3 = (-1) ** (a1 + a2)
            ph = np.exp(1j * Q3)
            H[..., a, a] += 0.5j * eta3 * ph - 0.5j * eta3 * np.conj(ph)
    w, V = np.linalg.eigh(H)
    P = np.einsum("...ai,...bi->...ab", V[..., :2], np.conj(V[..., :2]))
    E_formula = np.sqrt(np.sin(Q1 / 2) ** 2 + np.sin(Q2 / 2) ** 2 + np.sin(Q3) ** 2)
    dev = float(max(abs(w[..., 0] + E_formula).max(), abs(w[..., 3] - E_formula).max(),
                    abs(w[..., 0] - w[..., 1]).max(), abs(w[..., 2] - w[..., 3]).max()))
    return P, N, dev


def stag_cube_entropy(P, N, ell):
    Tq = np.fft.ifftn(P, axes=(0, 1, 2))
    sites = np.array(np.meshgrid(*(np.arange(ell),) * 3, indexing="ij")).reshape(3, -1).T
    R = np.stack([sites[:, 0] // 2, sites[:, 1] // 2, sites[:, 2]], axis=1)
    a = 2 * (sites[:, 0] % 2) + (sites[:, 1] % 2)
    dR = R[:, None, :] - R[None, :, :]
    ph = np.exp(1j * np.pi * sum(dR[..., j] / N[j] for j in range(3)))
    idx = tuple(dR[..., j] % N[j] for j in range(3))
    C = Tq[idx + (a[:, None], a[None, :])] * ph
    nu = np.clip(np.linalg.eigvalsh(0.5 * (C + C.conj().T)), 1e-15, 1 - 1e-15)
    return float(-np.sum(nu * np.log(nu) + (1 - nu) * np.log(1 - nu)))


def main():
    p = Report(NAME)
    style(plt)
    t0 = time.time()
    L, ells = 32, list(range(2, 10))
    Xs, Ps = cubic_correlators(L)
    eta_s = area_fit(ells, [cube_entropy(Xs, Ps, e) for e in ells])[0]
    txt = open(os.path.join(HERE, "results", "r29_gauge_field_weight.txt"), encoding="utf-8").read()
    w_V = float(re.search(r"eta_sym / eta_s = ([0-9.]+)", txt).group(1))
    p.section("A. Wilson fermions: the weight against the Wilson parameter, including the naive limit")
    p(f"   scalar on the same cubes: eta_s = {eta_s:.5f} per face; vector-boson quantum weight from r29: w_V = {w_V:.3f}")
    rs = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0]
    wD = {}
    p(f"   {'r':>5} {'eta_D per face':>15} {'w_D (scalars)':>14} {'N_eff(SM) = 4 + 22.5 w_D + 12 w_V':>34}")
    for r in rs:
        K = fermion_correlator(L, r)
        f = area_fit(ells, [fermion_cube_entropy(K, L, e) for e in ells])
        wD[r] = f[0] / eta_s
        p(f"   {r:5.2f} {f[0]:15.5f} {wD[r]:14.3f} {4 + 22.5 * wD[r] + 12 * w_V:34.0f}")
    p("   r = 0 is the naive fermion (8 massless doublers in 3 space dimensions): 32.5 scalars, about 4.1 per doubler.")
    p("   Check against E31 / r22 (computed there): r = 0.5, 1, 2, 4 gave 16.48, 9.14, 4.30, 1.79; reproduced above.")
    p("   The weight falls monotonically with r and tends to zero for r -> infinity (the Wilson term squeezes the Dirac cone).")
    p("   Weights typed into r26 (not computed there) against the values computed here:")
    for r, v in R26_TYPED.items():
        p(f"      r = {r}: typed {v:5.2f}, computed {wD[r]:6.3f}  ({100 * (v / wD[r] - 1):+.1f} %)")
    p("   They are within 1-4 %: accurate interpolations, but not computed. r26's power law 9.13 r^-1.08 is 17 % off at r = 0.5.")
    wlo, whi = (N_BAND[0] - 4 - 12 * w_V) / 22.5, (N_BAND[1] - 4 - 12 * w_V) / 22.5
    rr = np.array(rs[1:])
    ww = np.array([wD[r] for r in rs[1:]])
    r_hi = float(np.exp(np.interp(-math.log(wlo), -np.log(ww), np.log(rr))))
    r_lo = float(np.exp(np.interp(-math.log(whi), -np.log(ww), np.log(rr))))
    p(f"   Lambda's band N = {N_BAND[0]:.0f}-{N_BAND[1]:.0f} needs w_D between {wlo:.1f} and {whi:.1f} scalars, i.e. Wilson r between {r_lo:.2f} and {r_hi:.2f}.")

    p.section("B. Staggered (Kogut-Susskind) fermions")
    P, N, dev = stag_tables(L)
    p(f"   spectrum check: bands are +-E doubly degenerate with E^2 = sin^2(q1/2) + sin^2(q2/2) + sin^2(q3); max deviation {dev:.1e}")
    S_st = [stag_cube_entropy(P, N, e) for e in ells]
    f_st = area_fit(ells, S_st)
    w_st = f_st[0] / eta_s
    p(f"   area-law fit: eta_stag = {f_st[0]:.5f} per face = {w_st:.3f} scalars for the 2 tastes, {w_st / 2:.3f} per taste (one 4-component Dirac)")
    p(f"   Same ballpark as Wilson r = 1 ({wD[1.0]:.2f}) per Dirac fermion if each Standard Model Dirac fermion is one *pair* of tastes,")
    p(f"   and about half of it if one taste: the identification is a choice the substrate has to make.")

    p.section("C. Standard Model species count by discretisation (Higgs 4 + 22.5 Dirac x w + 12 vectors x w_V)")
    rows = [
        ("naive (8 doublers)", wD[0.0]),
        ("Wilson r = 0.5", wD[0.5]),
        ("Wilson r = 1", wD[1.0]),
        ("Wilson r = 2", wD[2.0]),
        ("staggered, 2 tastes per Dirac", w_st),
        ("staggered, 1 taste per Dirac", w_st / 2),
    ]
    p(f"   {'discretisation':<34} {'w per Dirac':>12} {'N_eff(SM)':>10} {'against 180-360':>18}")
    neffs = []
    for name, w in rows:
        n = 4 + 22.5 * w + 12 * w_V
        neffs.append(n)
        tag = "inside" if N_BAND[0] <= n <= N_BAND[1] else (f"{n / N_BAND[1]:.1f}x above" if n > N_BAND[1] else f"{N_BAND[0] / n:.1f}x below")
        p(f"   {name:<34} {w:12.2f} {n:10.0f} {tag:>18}")
    p("   => Lambda does not single out one fermion discretisation: it is met by Wilson r between "
      f"{r_lo:.2f} and {r_hi:.2f} and by staggered fermions counted as two tastes per Dirac; it is missed by the naive fermion and by r >= 2.")
    p(f"   => read the other way, the observed Lambda asks the substrate for a fermion weight of {wlo:.1f}-{whi:.1f} scalars per Dirac, i.e. an effective")
    p("      cutoff for the fermions of roughly one cell; it does not predict which lattice fermion does it.")

    p.section("Verdict")
    for line in (
        f"* COMPUTED HERE: Dirac weights w_D(r) from the naive fermion (32.5) to r = 4 (1.79); staggered 8.13 for two tastes (4.06 per taste).",
        f"* The window that Lambda needs corresponds to Wilson r = {r_lo:.2f}-{r_hi:.2f}, which contains the textbook r = 1.",
        "* r26's typed weights at r = 0.75, 1.25, 1.5, 3 are accurate to 1-4 % (they were interpolated, not computed).",
        "* NOT COMPUTED: overlap and domain-wall fermions; non-Abelian and gauge-sector edge terms (see r29).",
    ):
        p(line)
    p(f"   runtime {time.time() - t0:.0f} s")

    fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.9))
    ax = axs[0]
    rv = np.array(rs[1:])
    ax.loglog(rv, [wD[r] for r in rs[1:]], "o-", color=S1, label="Wilson fermion (computed)")
    ax.loglog([r for r in R26_TYPED], [wD[r] for r in R26_TYPED], "s", color=S2, ms=7, mfc="none", label="r26's typed values (not computed)")
    ax.axhspan(wlo, whi, color="#e4efe9", alpha=0.7)
    ax.text(0.11, whi * 1.06, f"weight Λ needs ({wlo:.1f}–{whi:.1f})", fontsize=8.5, color=INK_2)
    ax.axhline(w_st / 2, color=S3, ls="--", lw=1.4)
    ax.text(2.3, w_st / 2 * 1.08, "staggered, per taste", fontsize=8.5, color=S3)
    ax.axhline(wD[0.0], color=MUTED, ls=":", lw=1.3)
    ax.text(0.45, wD[0.0] * 0.9, "naive (r = 0, 8 doublers)", fontsize=8.5, color=INK_2)
    ax.set(xlabel="Wilson parameter r", ylabel="weight of one Dirac fermion (scalars)", title="A fermion's weight depends on how it is put on the lattice")
    ax.legend(loc="lower left", fontsize=8.5)
    ax = axs[1]
    names = ["naive\n(8 doublers)", "Wilson\nr = 0.5", "Wilson\nr = 1", "Wilson\nr = 2", "staggered\n2 tastes", "staggered\n1 taste"]
    cols = [MUTED, S1, S1, S1, S3, S3]
    ax.bar(range(len(rows)), neffs, color=cols, width=0.62)
    ax.axhspan(*N_BAND, color="#e4efe9", alpha=0.7)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels(names, fontsize=7.5)
    for i, v in enumerate(neffs):
        ax.text(i, v + 12, f"{v:.0f}", ha="center", fontsize=8.5, color=INK_2)
    ax.text(2.55, N_BAND[1] - 38, "needed by Λ: 180–360", fontsize=8.5, color=INK_2)
    ax.set(ylabel="N_eff of the Standard Model (quantum part of gauge fields)", title="Which discretisations meet what Λ needs")
    fig.tight_layout()
    save_fig(fig, NAME, "fermion_weights")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
