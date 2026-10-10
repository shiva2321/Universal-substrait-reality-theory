"""
r02 - Can a substrate make real light?  Checking the Levin-Wen and Volovik routes.
(2026-10-10, LAB_NOTEBOOK.md entry E5)

The problem from r01/audit: a solid gives 3 wave types (2 transverse + 1 gapless
longitudinal) with direction-dependent speeds; a plain superfluid gives only the
longitudinal one.  Light has exactly 2 transverse polarisations, same speed in
every direction.

A. Elastic lattice vs "gauge" lattice (the low-energy limit of Levin-Wen string-nets
   and of quantum spin ice).  In a gauge medium the energy depends only on the
   TWIST (curl) of the field, E ~ |curl A|^2, not on stretching.  We diagonalise both
   on a simple cubic lattice and compare: number of propagating modes, speed vs
   direction, birefringence.
B. Why symmetry decides: average a random response tensor over the cubic and the
   hexagonal symmetry groups.  Rank-2 (gauge/optics: epsilon, mu) vs rank-4 (elasticity).
C. Volovik's route: a Weyl point (as in superfluid helium-3 A-phase).  Emergent
   light cone, topological protection of masslessness (Chern number), and why an
   anisotropic light cone is undetectable if every species shares it.
"""
import itertools
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK, INK_2, MUTED, S1, S2, S3, Report, c, eV, hbar, lP, save_fig, style  # noqa: E402

NAME = "r02_emergent_light"


# ---------------------------------------------------------------- A. lattices
def sc_bonds(k1=1.0, k2=0.5):
    """Simple cubic: 6 nearest (spring k1) + 12 next-nearest (spring k2) central springs.
    Elastic constants C11 = k1 + 2 k2, C12 = C44 = k2, so the lattice is isotropic only if k1 = k2."""
    nn = [(k1, np.array(v, float)) for v in itertools.product((-1, 0, 1), repeat=3) if sum(map(abs, v)) == 1]
    nnn = [(k2, np.array(v, float)) for v in itertools.product((-1, 0, 1), repeat=3) if sum(map(abs, v)) == 2]
    return nn + nnn


def elastic_w2(q, bonds):
    D = np.zeros((3, 3))
    for k, d in bonds:
        n = d / np.linalg.norm(d)
        D += k * (1 - math.cos(q @ d)) * np.outer(n, n)
    return np.linalg.eigvalsh(D)            # ascending


def gauge_w2(q):
    """Lattice curl-curl operator: energy ~ |curl A|^2 with forward differences."""
    s = np.exp(1j * q) - 1.0
    M = (np.vdot(s, s).real) * np.eye(3) - np.outer(s, np.conj(s))
    return np.linalg.eigvalsh(M)            # ascending: [0, w^2, w^2]


def path():
    G, X, M, R = np.zeros(3), np.array([np.pi, 0, 0]), np.array([np.pi, np.pi, 0]), np.array([np.pi] * 3)
    legs = [(G, X), (X, M), (M, G), (G, R)]
    qs, ticks, x0 = [], [0.0], 0.0
    xs = []
    for a, b in legs:
        L = np.linalg.norm(b - a)
        for t in np.linspace(0, 1, 120, endpoint=False):
            qs.append(a + t * (b - a))
            xs.append(x0 + t * L)
        x0 += L
        ticks.append(x0)
    qs.append(R)
    xs.append(x0)
    return np.array(qs), np.array(xs), ticks


def fib_sphere(n):
    i = np.arange(n) + 0.5
    ph = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(ph), np.sin(th) * np.sin(ph), np.cos(ph)], 1)


# ---------------------------------------------------------------- B. symmetry groups
def cubic_group():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            M = np.zeros((3, 3))
            for i, j in enumerate(perm):
                M[i, j] = signs[i]
            mats.append(M)
    return mats                              # 48 elements (O_h)


def hex_group():
    def rz(t):
        return np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])
    gens = [rz(math.pi / 3), np.diag([1.0, -1.0, -1.0]), -np.eye(3)]
    group = [np.eye(3)]
    changed = True
    while changed:
        changed = False
        for g in list(group):
            for h in gens:
                k = g @ h
                if not any(np.allclose(k, m) for m in group):
                    group.append(k)
                    changed = True
    return group                             # 24 elements (D_6h)


def avg2(T, grp):
    return sum(R @ T @ R.T for R in grp) / len(grp)


def avg4(C, grp):
    out = np.zeros_like(C)
    for R in grp:
        out += np.einsum("ia,jb,kc,ld,abcd->ijkl", R, R, R, R, C)
    return out / len(grp)


def iso_residual4(C):
    """Relative distance of a rank-4 tensor from the nearest isotropic one."""
    d = np.eye(3)
    B1 = np.einsum("ij,kl->ijkl", d, d)
    B2 = np.einsum("ik,jl->ijkl", d, d) + np.einsum("il,jk->ijkl", d, d)
    A = np.array([[np.sum(B1 * B1), np.sum(B1 * B2)], [np.sum(B2 * B1), np.sum(B2 * B2)]])
    lam, mu = np.linalg.solve(A, [np.sum(C * B1), np.sum(C * B2)])
    return np.linalg.norm(C - lam * B1 - mu * B2) / np.linalg.norm(C)


def random_elastic(rng):
    """Random tensor with the symmetries of an elasticity tensor (Voigt 6x6 SPD)."""
    A = rng.normal(size=(6, 6))
    V = A @ A.T + 6 * np.eye(6)
    idx = {(0, 0): 0, (1, 1): 1, (2, 2): 2, (1, 2): 3, (2, 1): 3, (0, 2): 4, (2, 0): 4, (0, 1): 5, (1, 0): 5}
    C = np.zeros((3, 3, 3, 3))
    for i, j, k, l in itertools.product(range(3), repeat=4):
        C[i, j, k, l] = V[idx[(i, j)], idx[(k, l)]]
    return C


# ---------------------------------------------------------------- C. Weyl point
SX = np.array([[0, 1], [1, 0]], complex)
SY = np.array([[0, -1j], [1j, 0]])
SZ = np.array([[1, 0], [0, -1]], complex)


def weyl_H(p, cpar, cperp, pert=None):
    H = cpar * p[2] * SZ + cperp * (p[0] * SX + p[1] * SY)
    if pert is not None:
        H = H + pert
    return H


def chern_on_sphere(Hfun, radius=0.3, n=60):
    """Fukui-Hatsugai-Suzuki lattice Berry flux of the lower band through a sphere."""
    th = np.linspace(1e-3, np.pi - 1e-3, n)
    ph = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    U = np.empty((n, 2 * n, 2), complex)
    for i, t in enumerate(th):
        for j, f in enumerate(ph):
            p = radius * np.array([math.sin(t) * math.cos(f), math.sin(t) * math.sin(f), math.cos(t)])
            w, v = np.linalg.eigh(Hfun(p))
            U[i, j] = v[:, 0]
    flux = 0.0
    for i in range(n - 1):
        for j in range(2 * n):
            j2 = (j + 1) % (2 * n)
            loop = (np.vdot(U[i, j], U[i, j2]) * np.vdot(U[i, j2], U[i + 1, j2]) *
                    np.vdot(U[i + 1, j2], U[i + 1, j]) * np.vdot(U[i + 1, j], U[i, j]))
            flux += np.angle(loop)
    return flux / (2 * np.pi)


def main():
    p = Report(NAME)
    style(plt)
    rng = np.random.default_rng(3)

    # ---------------- A
    p.section("A. Elastic medium vs gauge ('twist-only') medium on a simple cubic lattice")
    for k2, label in ((1.0, "tuned springs k2 = k1"), (0.5, "generic springs k2 = k1/2")):
        b_ = sc_bonds(1.0, k2)
        dd = fib_sphere(800)
        v_ = np.array([np.sqrt(np.clip(elastic_w2(1e-4 * u, b_), 0, None)) / 1e-4 for u in dd])
        v_ /= v_[:, :2].mean()
        p(f"elastic, {label:26s}: Zener ratio {2 * k2 / (1.0 + 2 * k2 - k2):.3f}; transverse "
          f"{v_[:, :2].min():.3f}c-{v_[:, :2].max():.3f}c; longitudinal {v_[:, 2].min():.3f}c-{v_[:, 2].max():.3f}c")
    p("=> tuning the springs CAN make an elastic lattice isotropic, but it always keeps 3 propagating")
    p("   waves, including a longitudinal one at ~1.7c. The generic case is used below.")
    bonds = sc_bonds(1.0, 0.5)
    qs, xs, ticks = path()
    el = np.array([np.sqrt(np.clip(elastic_w2(q, bonds), 0, None)) for q in qs])
    ga = np.array([np.sqrt(np.clip(gauge_w2(q), 0, None)) for q in qs])
    dirs = fib_sphere(1500)
    eps = 1e-4
    vel = np.array([np.sqrt(np.clip(elastic_w2(eps * u, bonds), 0, None)) / eps for u in dirs])
    vga = np.array([np.sqrt(np.clip(gauge_w2(eps * u), 0, None)) / eps for u in dirs])
    vref = vel[:, :2].mean()
    vel /= vref
    p(f"elastic: long-wave transverse speeds {vel[:, :2].min():.3f}c - {vel[:, :2].max():.3f}c "
      f"(spread {100 * (vel[:, :2].max() - vel[:, :2].min()):.1f}%), longitudinal {vel[:, 2].min():.3f}c - {vel[:, 2].max():.3f}c")
    p(f"elastic: largest speed difference between the two transverse waves (birefringence): "
      f"{np.max(vel[:, 1] - vel[:, 0]):.3f}c")
    p(f"gauge:   long-wave transverse speeds {vga[:, 1:].min():.8f}c - {vga[:, 1:].max():.8f}c (both polarisations)")
    p(f"gauge:   third ('longitudinal') mode frequency: max {vga[:, 0].max() * eps:.1e} -> zero at EVERY wavelength")
    p("         a zero-frequency mode has no restoring force: it is a pure relabelling ('gauge') of the field,")
    p("         and Gauss's law (div E = 0 away from charges) removes it. => exactly 2 polarisations.")
    for label, lam in (("500 nm light", 500e-9), ("100 GeV gamma ray", 2 * math.pi * hbar * c / (100e9 * eV))):
        qa = 2 * math.pi * lP() / lam
        p(f"gauge lattice with Planck spacing, {label:18s}: direction dependence (qa)^2/36 = {qa * qa / 36:.1e}")
    p("Charges = places where Gauss's law is violated (ends of flux strings in Levin-Wen); in string-net")
    p("models those ends can be fermions. Emergent fine-structure constant in quantum spin ice is")
    p("computable from lattice couplings: ~0.08 (Pace, Morampudi, Moessner, Laumann, PRL 127, 117205 (2021)).")

    # ---------------- B
    p.section("B. Symmetry decides isotropy: group-average random response tensors")
    cub, hexg = cubic_group(), hex_group()
    p(f"group sizes: cubic O_h = {len(cub)}, hexagonal D_6h = {len(hexg)}")
    T = rng.normal(size=(3, 3))
    T = T + T.T
    for name, grp in (("cubic", cub), ("hexagonal", hexg)):
        A2 = avg2(T, grp)
        ev = np.linalg.eigvalsh(A2)
        p(f"{name:9s} rank-2 (dielectric/magnetic, i.e. gauge light): eigenvalues {np.round(ev, 6)} -> "
          f"{'ISOTROPIC' if np.ptp(ev) < 1e-9 * abs(ev).max() else 'uniaxial (birefringent)'}")
    C = random_elastic(rng)
    for name, grp in (("cubic", cub), ("hexagonal", hexg)):
        p(f"{name:9s} rank-4 (elasticity, i.e. 'light = shear wave'): distance from isotropic = "
          f"{iso_residual4(avg4(C, grp)):.3f}  -> anisotropic")
    p("=> On a CUBIC lattice, gauge-type light is automatically isotropic at long wavelengths (symmetry")
    p("   forces it). Elastic-type light is isotropic only if the couplings are tuned (symmetry does not")
    p("   protect it), and it keeps a third wave. On a hexagonal (HCP) lattice even gauge light is")
    p("   birefringent unless the couplings are tuned.")

    # ---------------- C
    p.section("C. Volovik: Weyl point (superfluid helium-3 A-phase type)")
    cpar, cperp = 1.0, 0.1
    bx, by, bz = 0.01 * rng.normal(size=3)
    pert = bx * SX + by * SY + bz * SZ + 0.02 * np.eye(2)
    node = np.array([-bx / cperp, -by / cperp, -bz / cpar])       # where d(p) = 0 after the perturbation
    grid = np.linspace(-0.6, 0.6, 241)
    PX, PY, PZ = np.meshgrid(grid, grid, grid, indexing="ij")
    gaps = []
    for b0 in ((0.0, 0.0, 0.0), (bx, by, bz)):
        # a 2x2 Hamiltonian d0*1 + d.sigma has band gap 2|d|; scan the grid, then the exact node
        d = np.sqrt((cperp * PX + b0[0]) ** 2 + (cperp * PY + b0[1]) ** 2 + (cpar * PZ + b0[2]) ** 2)
        gaps.append(2 * d.min())
    gap_at_node = np.ptp(np.linalg.eigvalsh(weyl_H(node, cpar, cperp, pert)))
    N0 = chern_on_sphere(lambda q: weyl_H(q, cpar, cperp))
    N1 = chern_on_sphere(lambda q: weyl_H(q + node, cpar, cperp, pert))
    p(f"anisotropic emergent light cone: E = sqrt(c_par^2 p_z^2 + c_perp^2 p_perp^2), c_par/c_perp = {cpar / cperp:.0f}")
    p(f"random perturbation moves the node to p = ({node[0]:+.3f}, {node[1]:+.3f}, {node[2]:+.3f})")
    p(f"smallest band gap on the grid: unperturbed {gaps[0]:.4f}, perturbed {gaps[1]:.4f}; exactly at the moved node "
      f"{gap_at_node:.1e}")
    p(f"topological charge (Berry flux / 2pi) around the node: {N0:+.3f} before, {N1:+.3f} after (around the moved node)")
    p("=> the perturbation only MOVES the massless point; it cannot give it a mass while the charge is +/-1.")
    p("   Masslessness is protected by topology (Volovik's explanation of massless fermions/photons).")
    p("In He-3 A-phase the emergent 'speeds of light' are roughly v_F ~ 55 m/s along the axis and a few")
    p("cm/s across it (Volovik 2003): hugely anisotropic, yet every quasiparticle near the node feels the")
    p("SAME cone. Rescaling z -> z c_perp/c_par makes it isotropic for all of them: internal observers")
    p("would measure the same c in every direction. Anisotropy is only detectable if species differ:")
    for ra, rb in ((10.0, 10.0), (10.0, 10.0 * (1 + 1e-6))):
        p(f"   species ratios c_par/c_perp = {ra:g} and {rb:.7g}: Michelson-Morley-type signal {rb / ra - 1:.1e}")
    p("Real experiments bound such species differences at ~1e-17 or better, so all species must share one")
    p("cone to that precision (the Collins et al. 2004 fine-tuning problem in its modern form).")

    # ---------------- figures
    fig = plt.figure(figsize=(14, 4.4))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2, sharey=ax1)
    ax3 = fig.add_subplot(1, 3, 3, projection="polar")
    for k, (col, lab) in enumerate(((S1, "transverse 1"), (S3, "transverse 2"), (S2, "longitudinal"))):
        ax1.plot(xs, el[:, k] / vref, color=col, label=lab)
    ax2.plot(xs, ga[:, 1], color=S1, label="transverse 1 and 2 (identical)")
    ax2.plot(xs, ga[:, 2], color=S3, ls=(0, (4, 3)))
    ax2.plot(xs, ga[:, 0], color=S2, label="longitudinal: zero, removed by Gauss's law")
    for ax, title in ((ax1, "Elastic lattice: 3 waves, all propagate"),
                      (ax2, "Twist-only (gauge) lattice: exactly 2 waves")):
        ax.set_xticks(ticks)
        ax.set_xticklabels(["Γ", "X", "M", "Γ", "R"])
        ax.set_xlim(0, ticks[-1])
        ax.set_title(title)
        ax.legend(loc="upper left", fontsize=8.5)
    ax1.set_ylabel("frequency (lattice units)")
    th = np.linspace(0, 2 * np.pi, 361)
    u = np.stack([np.sin(th) / math.sqrt(2), np.sin(th) / math.sqrt(2), np.cos(th)], 1)
    ve = np.array([np.sqrt(np.clip(elastic_w2(eps * w, bonds), 0, None)) / eps for w in u]) / vref
    vg = np.array([np.sqrt(np.clip(gauge_w2(eps * w), 0, None)) / eps for w in u])
    ax3.plot(th, ve[:, 0], color=S1, label="elastic, transverse 1")
    ax3.plot(th, ve[:, 1], color=S3, label="elastic, transverse 2")
    ax3.plot(th, vg[:, 1], color=INK, label="gauge, both (= c)")
    ax3.set_rlim(0.6, 1.25)
    ax3.set_yticks([0.8, 1.0, 1.2])
    ax3.set_yticklabels(["0.8c", "c", "1.2c"], fontsize=8, color=INK_2)
    ax3.set_xticklabels([])
    ax3.set_title("Long-wave light speed by direction", pad=12)
    ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=1, fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "elastic_vs_gauge")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    pz = np.linspace(-0.5, 0.5, 401)
    for P, base, col, lab in ((None, np.zeros(3), S1, "pure Weyl point"),
                              (pert, node, S2, "after a random perturbation")):
        E = np.array([np.linalg.eigvalsh(weyl_H(base + np.array([0, 0, z]), cpar, cperp, P)) for z in pz])
        axs[0].plot(base[2] + pz, E[:, 0], color=col, label=lab)
        axs[0].plot(base[2] + pz, E[:, 1], color=col)
    axs[0].set(xlabel="momentum along the axis (line through the node)", ylabel="energy",
               title="Perturbation moves the node; it stays massless")
    axs[0].legend(loc="upper center")
    pp = np.linspace(-0.5, 0.5, 401)
    axs[1].plot(pp, cpar * np.abs(pp), color=S1, label=f"along the axis (speed {cpar:g})")
    axs[1].plot(pp, cperp * np.abs(pp), color=S2, label=f"across the axis (speed {cperp:g})")
    axs[1].plot(pp, cperp * np.abs(pp * cpar / cperp), color=S3, ls=(0, (4, 3)),
                label="across, in rescaled units: identical cone")
    axs[1].set(xlabel="momentum", ylabel="energy of upper band",
               title="Anisotropic cone, but shared by every species")
    axs[1].legend(loc="upper center", fontsize=8.5)
    fig.tight_layout()
    save_fig(fig, NAME, "weyl_point")
    plt.close(fig)

    p.save()


if __name__ == "__main__":
    main()
