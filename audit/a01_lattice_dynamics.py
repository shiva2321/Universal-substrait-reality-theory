"""
Audit 01 - Lattice dynamics of the proposed Planckion crystal.

Independent re-computation (no values copied from the USRT documents) of:
  1. Elastic constants of an FCC nearest-neighbour central-spring lattice
     (Cauchy-Born, by finite-difference strain energy) vs. RESEARCH_PREPRINT
     Calc. 1.6 (C11 = 2*sqrt2 k/a, C12 = C44 = sqrt2 k/a, mu = k/(5 sqrt2 a)).
  2. Long-wavelength sound speeds in every direction for FCC and for a true
     HCP lattice (2-atom basis, ideal c/a), from the full dynamical matrix.
     Tests the claim "low-energy wave speed is perfectly isotropic".
  3. The longitudinal branch omega_L(q): is there an energy *gap* (minimum
     energy > 0) or only a band *maximum*?
  4. The 7.2 calibration and the de Boer parameter Lambda* = sqrt(7.2).
  5. Whether a velocity can be built from hbar and G alone (circularity).

Units: spring constant k = 1, mass M = 1, nearest-neighbour distance a = 1,
so speeds are in units of a*sqrt(k/M).
"""
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import banner, c, hbar, planck_mass, planck_length  # noqa: E402


# ---------------------------------------------------------------------------
# Lattice construction
# ---------------------------------------------------------------------------
def fcc_neighbours(a=1.0):
    vecs = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        for s1, s2 in itertools.product((1, -1), repeat=2):
            v = np.zeros(3)
            v[i], v[j] = s1, s2
            vecs.append(v * a / math.sqrt(2.0))
    return np.array(vecs)


def hcp_structure(a=1.0):
    """Primitive vectors and 2-atom basis of ideal HCP (c/a = sqrt(8/3))."""
    cc = a * math.sqrt(8.0 / 3.0)
    A = np.array([[a, 0, 0], [a / 2, a * math.sqrt(3) / 2, 0], [0, 0, cc]])
    basis = np.array([[0, 0, 0], [a / 2, a / (2 * math.sqrt(3)), cc / 2]])
    return A, basis


def hcp_bonds(a=1.0, tol=1e-6):
    """List of (s, s', d) nearest-neighbour bonds for the HCP basis."""
    A, basis = hcp_structure(a)
    bonds = []
    rng = range(-2, 3)
    for s, tau_s in enumerate(basis):
        for n1, n2, n3 in itertools.product(rng, rng, rng):
            R = n1 * A[0] + n2 * A[1] + n3 * A[2]
            for sp, tau_sp in enumerate(basis):
                d = R + tau_sp - tau_s
                if abs(np.linalg.norm(d) - a) < tol:
                    bonds.append((s, sp, d))
    return bonds


# ---------------------------------------------------------------------------
# Dynamical matrices (central nearest-neighbour springs, k = M = 1)
# ---------------------------------------------------------------------------
def dyn_fcc(q, nbrs):
    D = np.zeros((3, 3))
    for d in nbrs:
        n = d / np.linalg.norm(d)
        D += (1.0 - math.cos(q @ d)) * np.outer(n, n)
    return D


def dyn_hcp(q, bonds):
    D = np.zeros((6, 6), dtype=complex)
    for s, sp, d in bonds:
        n = d / np.linalg.norm(d)
        nn = np.outer(n, n)
        D[3 * s:3 * s + 3, 3 * s:3 * s + 3] += nn
        D[3 * s:3 * s + 3, 3 * sp:3 * sp + 3] -= nn * np.exp(1j * (q @ d))
    return D


def fibonacci_sphere(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


def acoustic_speeds(kind, directions, qmag=1e-4):
    """Return (n_dir, 3) sorted acoustic speeds (TA1 <= TA2 <= LA)."""
    out = []
    if kind == "fcc":
        nbrs = fcc_neighbours()
        for u in directions:
            w2 = np.linalg.eigvalsh(dyn_fcc(qmag * u, nbrs))
            out.append(np.sqrt(np.clip(np.sort(w2), 0, None)) / qmag)
    else:
        bonds = hcp_bonds()
        for u in directions:
            w2 = np.linalg.eigvalsh(dyn_hcp(qmag * u, bonds))
            out.append(np.sqrt(np.clip(np.sort(w2.real)[:3], 0, None)) / qmag)
    return np.array(out)


# ---------------------------------------------------------------------------
# Cauchy-Born elastic constants for FCC (finite-difference strain energy)
# ---------------------------------------------------------------------------
def fcc_elastic_constants():
    nbrs = fcc_neighbours()
    vcell = 1.0 / math.sqrt(2.0)

    def W(eps):
        # per-atom energy = 1/2 * sum over 12 bonds of (1/2) k (dr)^2
        e = 0.0
        for d in nbrs:
            dr = d @ eps @ d / np.linalg.norm(d)
            e += 0.25 * dr * dr
        return e / vcell

    def C(i, j, k, l, hstep=1e-4):
        def strain(x, y):
            eps = np.zeros((3, 3))
            for (p, q_, val) in ((i, j, x), (k, l, y)):
                if p == q_:
                    eps[p, q_] += val
                else:
                    eps[p, q_] += val / 2
                    eps[q_, p] += val / 2
            return W(eps)
        return (strain(hstep, hstep) - strain(hstep, -hstep) - strain(-hstep, hstep)
                + strain(-hstep, -hstep)) / (4 * hstep * hstep)

    return C(0, 0, 0, 0), C(0, 0, 1, 1), C(1, 2, 1, 2)


def main():
    out = []
    p = out.append

    # 1. Elastic constants ----------------------------------------------------
    p(banner("1. FCC nearest-neighbour elastic constants (units k/a)"))
    C11, C12, C44 = fcc_elastic_constants()
    s2 = math.sqrt(2)
    p(f"computed : C11 = {C11:.6f}   C12 = {C12:.6f}   C44 = {C44:.6f}")
    p(f"analytic : C11 = sqrt2 = {s2:.6f},  C12 = C44 = 1/sqrt2 = {1/s2:.6f}")
    p(f"preprint : C11 = 2 sqrt2 = {2*s2:.6f},  C12 = C44 = sqrt2 = {s2:.6f}   (2x too large)")
    mu_V = (C11 - C12 + 3 * C44) / 5
    K = (C11 + 2 * C12) / 3
    p(f"Voigt shear modulus mu_V = (C11-C12+3C44)/5 = {mu_V:.6f} = 2 sqrt2/5 k/a")
    p(f"preprint mu0 = 1/(5 sqrt2) k/a = {1/(5*s2):.6f}   -> preprint is {mu_V/(1/(5*s2)):.1f}x too small")
    p(f"bulk modulus K = (C11+2C12)/3 = {K:.6f} k/a ; Cauchy relation C12 = C44 holds: {abs(C12-C44)<1e-6}")
    zener = 2 * C44 / (C11 - C12)
    p(f"Zener anisotropy ratio 2C44/(C11-C12) = {zener:.4f}  (1.0 would be elastically isotropic)")

    # 2. Directional sound speeds --------------------------------------------
    p(banner("2. Long-wavelength (k -> 0) sound speeds over 2000 directions"))
    dirs = fibonacci_sphere(2000)
    rho = math.sqrt(2.0)  # M / V_cell with V_cell = a^3/sqrt2
    v_ref = math.sqrt(mu_V / rho)  # the paper's calibration: this is set equal to c
    for kind in ("fcc", "hcp"):
        v = acoustic_speeds(kind, dirs)
        ta = v[:, :2]
        la = v[:, 2]
        p(f"[{kind.upper()}] transverse speed: min {ta.min()/v_ref:.4f} c   max {ta.max()/v_ref:.4f} c"
          f"   (spread {100*(ta.max()-ta.min())/ta.mean():.1f}%)")
        p(f"[{kind.upper()}] longitudinal speed: min {la.min()/v_ref:.4f} c   max {la.max()/v_ref:.4f} c")
        if kind == "hcp":
            # dependence on polar angle (c-axis) vs azimuth (basal plane)
            for th_deg in (0, 30, 60, 90):
                th = math.radians(th_deg)
                vals = []
                for ph in np.linspace(0, 2 * math.pi, 12, endpoint=False):
                    u = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
                    vals.append(acoustic_speeds("hcp", [u])[0])
                vals = np.array(vals)
                p(f"    HCP polar angle {th_deg:2d} deg: TA1 {vals[:,0].min()/v_ref:.4f}-{vals[:,0].max()/v_ref:.4f} c,"
                  f" TA2 {vals[:,1].min()/v_ref:.4f}-{vals[:,1].max()/v_ref:.4f} c, LA {vals[:,2].mean()/v_ref:.4f} c")
    p("(speeds are quoted relative to the Voigt-averaged shear speed, which the paper sets equal to c)")
    p("=> The low-energy speed of the transverse ('light') waves depends on direction by tens of percent.")
    p("   Laboratory bounds on direction-dependence of light speed are ~1e-17 to 1e-18 (rotating")
    p("   optical-resonator Michelson-Morley tests); astrophysical polarization bounds on birefringent")
    p("   Lorentz violation are ~1e-32 or tighter. A 10-30% effect is excluded by many orders of magnitude.")

    # 3. Longitudinal branch: gap or band edge? -------------------------------
    p(banner("3. Longitudinal phonon branch along FCC [100]: is there a gap?"))
    nbrs = fcc_neighbours()
    zb = 2 * math.pi / math.sqrt(2)  # [100] zone boundary X point, |q| = 2pi/A with A = sqrt2 a
    for frac in (1e-6, 1e-3, 0.01, 0.1, 0.5, 1.0):
        q = np.array([frac * zb, 0, 0])
        w = np.sqrt(np.clip(np.linalg.eigvalsh(dyn_fcc(q, nbrs)), 0, None))
        p(f"q = {frac:8.1e} x q_zone : omega_LA = {w[2]:.6e}  (omega_LA/q = {w[2]/np.linalg.norm(q):.4f})")
    p("omega_LA -> 0 as q -> 0: the longitudinal branch is GAPLESS. The quantity the preprint calls")
    p("E_gap = hbar*omega_max is the TOP of the band (highest possible frequency), not a minimum.")

    # In physical units with the paper's calibration
    lP = planck_length()
    mP, _ = planck_mass()
    cl_over_c = 3 ** 0.5  # paper's own (Cauchy, isotropic) value
    lam = 500e-9
    E_LA = hbar * cl_over_c * c * 2 * math.pi / lam / 1.602176634e-19
    p(f"Physical example: a longitudinal phonon of wavelength 500 nm (green light) has energy")
    p(f"E = hbar * c_l * 2pi/lambda = {E_LA:.2f} eV  -- i.e. ordinary optical energies excite it.")

    # 4. Calibration & de Boer -------------------------------------------------
    p(banner("4. The '7.2' calibration and the de Boer parameter"))
    # paper: mu/rho = 7.2 V0/M with its (wrong) mu; correct factor:
    k_per_V0 = 72.0  # k0 = 72 V0 / a^2 for this Lennard-Jones form (this part of the paper is right)
    factor_paper = 72.0 / (5 * s2) / s2
    factor_correct = k_per_V0 * mu_V / rho
    p(f"paper: mu0/rho0 = {factor_paper:.3f} V0/M0  -> V0 = M0 c^2 / {factor_paper:.1f}")
    p(f"correct Cauchy-Born: mu_V/rho0 = {factor_correct:.3f} V0/M0 -> V0 = M0 c^2 / {factor_correct:.1f}")
    lam_paper = math.sqrt(factor_paper)
    lam_correct = math.sqrt(factor_correct)
    lam_direct = hbar / (lP * math.sqrt(mP * mP * c * c / factor_paper))
    p(f"Lambda* = hbar/(a0 sqrt(M0 V0)) with a0 = l_P, M0 = m_P, V0 = M0 c^2/X  equals sqrt(X) EXACTLY,")
    p(f"because hbar = l_P m_P c.   paper X = 7.2 -> Lambda* = {lam_paper:.4f} (direct: {lam_direct:.4f})")
    p(f"with the corrected X = {factor_correct:.1f} -> Lambda* = {lam_correct:.4f}")
    p("So Lambda* is not an independent result: it is the square root of the fitting constant.")
    p("Either way Lambda* > 0.3, i.e. by the paper's own criterion the 'crystal' is a quantum LIQUID;")
    p("a liquid has zero static shear modulus, so the Cauchy-Born shear modulus used to make light")
    p("does not exist in that state. The two headline claims are mutually exclusive.")

    # 5. Circularity ------------------------------------------------------------
    p(banner("5. Can a speed be built from hbar and G alone?"))
    # hbar^x G^y with units: hbar = kg m^2 s^-1, G = m^3 kg^-1 s^-2. Want m^1 s^-1.
    Amat = np.array([[1, -1],   # kg
                     [2, 3],    # m
                     [-1, -2]])  # s
    target = np.array([0, 1, -1])
    sol, res, rank, _ = np.linalg.lstsq(Amat, target, rcond=None)
    p("hbar^x G^y must have units m/s: kg: x - y = 0;  m: 2x + 3y = 1;  s: -x - 2y = -1")
    p("kg & m give x = y = 1/5, but s needs x = y = 1/3  -> contradiction, no solution.")
    p(f"(numerical least-squares check: best (x, y) = {sol}, residual {res} != 0)")
    p("=> No combination of hbar and G is a velocity. Planck mass and Planck length both contain c,")
    p("   so 'c emerges as sqrt(mu/rho)' only returns the c that was put into M0, a0 and V0.")
    p("   A genuine prediction of c would need M0 and a0 measured independently of c.")

    # 6. HCP vs FCC stacking -----------------------------------------------------
    p(banner("6. HCP or FCC? (the documents use both interchangeably)"))
    bonds = hcp_bonds()
    above = sorted([tuple(np.round(d[:2], 4)) for s, sp, d in bonds if s == 0 and d[2] > 1e-6])
    below = sorted([tuple(np.round(d[:2], 4)) for s, sp, d in bonds if s == 0 and d[2] < -1e-6])
    p(f"HCP: the 3 neighbours above and the 3 below sit at the SAME (x,y): {above == below}  -> stacking ABAB")
    p("FCC: the upper and lower triangles are rotated 60 deg relative to each other -> stacking ABCABC")
    p("The preprint's Calc. 1.6 neighbour vectors (a/sqrt2)(+-1,+-1,0)... are FCC, the treatise calls")
    p("the lattice HCP, and the '3 generations / 3 colours from A->B->C stacking' argument needs FCC.")

    text = "\n".join(out)
    print(text)
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "results", "a01_lattice_dynamics.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
