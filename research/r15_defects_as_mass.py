"""
r15 - Mass as a defect of the substrate: the world-crystal route  (LAB_NOTEBOOK.md entry E20)

Question (user): find the protected spin-2 mode "with field-established and out-of-the-box ways
... based on our theory as well", and earlier: "how a particle would affect the substrate".

The original USRT substrate was a crystal (FCC lattice).  Crystals have a 60-year-old exact
dictionary with gravity (Kroener 1960s 'continuum theory of defects'; Kleinert 1987 'world
crystal'; Katanaev & Volovich 1992; Pretko & Radzihovsky 2018 'fracton-elasticity duality'):
    strain of the crystal          <->  metric perturbation  h_ij = 2 eps_ij
    density of disclinations       <->  curvature
    density of dislocations        <->  torsion
  A. Check the core identity symbolically: the linearised Einstein tensor of a spatial metric IS
     Kroener's incompatibility of the strain.  Then a static mass  <->  a density of disclinations.
  B. A single wedge disclination (Frank angle Omega) is a cone: it lenses light into a double image
     exactly like a point mass in 2+1 gravity (deficit 8 pi G m) or a cosmic string in 3+1
     (deficit 8 pi G mu).  Computed by unfolding the cone.
  C. Measured consequence for a CRYSTAL substrate: its disclination lines carry quantised Frank
     angles (90 deg for a cubic/FCC lattice) -> cosmic strings with G mu = Omega/(8 pi) ~ 0.06,
     against the observed bound G mu < 1.5e-7.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

NAME = "r15_defects_as_mass"
GMU_CMB = 1.5e-7          # Planck 2013 XXV, A&A 571, A25 (2014): Nambu-Goto strings, 95%


def part_A(p):
    p.section("A. Kroener = Einstein: curvature of the strain is the density of defects")
    x = sp.symbols("x0:3")
    h = [[sp.Function(f"h{min(i, j)}{max(i, j)}")(*x) for j in range(3)] for i in range(3)]
    eps = sp.LeviCivita

    def d(f, a):
        return sp.diff(f, x[a])
    # linearised Riemann tensor of g = delta + h, R_klmn = 1/2 (d_l d_m h_kn + d_k d_n h_lm - d_k d_m h_ln - d_l d_n h_km)
    def R(k, l, m, n):
        return sp.Rational(1, 2) * (d(d(h[k][n], l), m) + d(d(h[l][m], k), n) - d(d(h[l][n], k), m) - d(d(h[k][m], l), n))
    ric = [[sum(R(k, i, k, j) for k in range(3)) for j in range(3)] for i in range(3)]
    Rs = sum(ric[i][i] for i in range(3))
    G = [[sp.expand(ric[i][j] - sp.Rational(1, 2) * (1 if i == j else 0) * Rs) for j in range(3)] for i in range(3)]
    inc = [[sp.expand(sum(eps(i, k, l) * eps(j, m, n) * d(d(h[l][n], k), m)
                          for k in range(3) for l in range(3) for m in range(3) for n in range(3)))
            for j in range(3)] for i in range(3)]
    ok = all(sp.expand(G[i][j] - sp.Rational(1, 2) * inc[i][j]) == 0 for i in range(3) for j in range(3))
    p(f"linearised 3D Einstein tensor G_ij(h) = +1/2 inc(h)_ij, inc = eps_ikl eps_jmn d_k d_m h_ln:  {ok}")
    p("   inc(eps) is exactly Kroener's incompatibility: in a crystal it equals the DEFECT DENSITY")
    p("   (disclinations, plus gradients of dislocations). With h = 2 eps:  G_ij = inc(eps)_ij = defect density.")
    Phi = sp.Function("Phi")(*x)
    hs = [[(-2 * Phi if i == j else 0) for j in range(3)] for i in range(3)]
    R3 = sum(d(d(hs[i][j], i), j) for i in range(3) for j in range(3)) - sum(d(d(hs[i][i], k), k) for i in range(3) for k in range(3))
    lap = sum(d(d(Phi, k), k) for k in range(3))
    p(f"weak-field mass (space part g_ij = (1 - 2 Phi) delta_ij, i.e. gamma = 1): spatial curvature R3 = "
      f"{sp.simplify(R3 / lap)} lap(Phi) = 16 pi G rho")
    p("=> a static mass is a cloud of disclination density in the substrate's strain, of strength")
    p("   16 pi G rho. This is precisely the SPATIAL half of the metric -- the 'mu' half that r08 needed")
    p("   (eps = mu) for the full light bending. The world-crystal picture supplies it automatically.")


def unfold_images(Omega, D_ls, D_o):
    """Cone of deficit Omega with apex at the origin; the removed wedge |theta| < Omega/2 points at the
    source.  Observer at (-D_o, 0); the source on the far side appears at (D_ls, +-Omega/2)."""
    imgs = [np.array([D_ls * math.cos(s * Omega / 2), D_ls * math.sin(s * Omega / 2)]) for s in (1, -1)]
    O = np.array([-D_o, 0.0])
    ang = [math.atan2(*(v - O)[::-1]) for v in imgs]
    return O, imgs, abs(ang[0] - ang[1])


def part_B(p):
    p.section("B. A wedge disclination lenses like a mass: double images")
    p("Unfold the cone (deficit Omega): straight lines in the unfolded plane are the light rays.")
    for Om_deg, D_ls, D_o in ((60, 1.0, 1.0), (60, 1.0, 3.0), (1e-3, 1.0, 1.0), (1e-3, 1.0, 3.0)):
        Om = math.radians(Om_deg)
        _, _, sep = unfold_images(Om, D_ls, D_o)
        approx = Om * D_ls / (D_ls + D_o)
        p(f"   Omega = {Om_deg:g} deg, D_ls = {D_ls}, D_o = {D_o}: image separation {math.degrees(sep):.6g} deg;"
          f" small-angle formula Omega D_ls/D_s = {math.degrees(approx):.6g} deg")
    p("=> two images, separated by Omega D_ls/D_s for small Omega: identical to the cosmic-string lens")
    p("   (Vilenkin 1981, Gott 1985) with Omega = 8 pi G mu, and to a 2+1D point mass (Deser, Jackiw &")
    p("   't Hooft 1984) with Omega = 8 pi G m. Space around the defect is locally FLAT; the effect is")
    p("   global (missing angle) -- in 2+1D a point mass exerts no local force at all, only this.")
    p("   A negative disclination (7-fold, extra wedge) is an EXCESS angle: in 2+1D that is a negative")
    p("   mass, which defocuses -- the closest thing to 'antigravity' in this dictionary. Real crystals")
    p("   make +-disclinations in bound pairs (a pair = a dislocation).")


def part_C(p):
    p.section("C. Measured test of a CRYSTAL substrate: its disclination lines would be cosmic strings")
    rows = [("cubic / FCC lattice (original USRT), 4-fold axis", 90.0),
            ("hexagonal lattice, 6-fold axis", 60.0),
            ("cubic lattice, 3-fold [111] axis", 120.0)]
    out = []
    for name, deg in rows:
        Gmu = math.radians(deg) / (8 * math.pi)
        out.append((name, deg, Gmu))
        p(f"   {name:50s} Omega = {deg:5.1f} deg -> G mu = {Gmu:.4f} -> {Gmu / GMU_CMB:.1e} x the CMB bound")
    Om_max = 8 * math.pi * GMU_CMB
    p(f"CMB bound (Planck 2013 XXV): G mu < {GMU_CMB:.1e}  ->  allowed Frank angle < {Om_max:.1e} rad = {math.degrees(Om_max) * 3600:.2f} arcsec")
    p("   (pulsar-timing and LIGO-Virgo-KAGRA bounds are stronger still for most string-loop models)")
    p("=> a substrate with DISCRETE rotation symmetry would have quantised disclinations, each a cosmic")
    p("   string with a 60-120 degree deficit: one inside our horizon would double large parts of the")
    p("   sky. None is seen. So either the substrate has no free disclination lines anywhere in the")
    p("   visible universe (confined or never formed), or its rotation symmetry is CONTINUOUS at large")
    p("   scales -- a quantum liquid (crystal melted by dislocations, Zaanen et al.; or no lattice at all),")
    p("   where curvature can take any value, as GR requires. This independently agrees with the audit's")
    p("   verdict against a rigid crystal and with r06's 'no fixed lattice' option.")
    return out, Om_max


def part_D(p):
    p.section("D. Brainstorm: what the defect picture adds, and its limits")
    for line in (
        "* Particles as defects (r07) and mass as defect density (A) are the SAME idea: trapped energy",
        "  that cannot unwind is a topological defect; its gravitational field is the curvature it imposes.",
        "* Dislocations = torsion: in the same dictionary the substrate's dislocations are torsion, which",
        "  couples to spin (Einstein-Cartan; Hehl et al. 1976). Torsion is unobserved so far: another sign",
        "  the substrate's dislocations must be condensed or absent at accessible scales.",
        "* Fracton-elasticity duality (Pretko & Radzihovsky 2018): an isolated disclination cannot move",
        "  (a 'fracton'); it moves only together with other defects. Pretko (2017) noted this gives a",
        "  Mach-like inertia from the environment. Free particles DO move, so particles cannot be bare",
        "  disclinations -- at most bound clusters.",
        "* Limit: the dictionary gives the GEOMETRY of gravity (curvature = defects), not its DYNAMICS.",
        "  Kleinert's world crystal needs a special 'second-gradient' elasticity for the defect fluctuations",
        "  to produce the Einstein action; the graviton count and speed are again the questions of r12-r13.",
    ):
        p(line)


def main():
    p = Report(NAME)
    style(plt)
    part_A(p)
    part_B(p)
    out, Om_max = part_C(p)
    part_D(p)

    # ---------- figure
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw={"width_ratios": [1.15, 1]})
    Om = math.radians(60)
    R = 9
    pts = []
    for i in range(-2 * R, 2 * R + 1):
        for j in range(-2 * R, 2 * R + 1):
            v = np.array([i + 0.5 * j, j * math.sqrt(3) / 2])
            r = np.hypot(*v)
            if 0 < r <= R and abs(math.atan2(v[1], v[0])) >= Om / 2 - 1e-9:
                pts.append(v)
    pts = np.array(pts)
    ax = axs[0]
    ax.plot(pts[:, 0], pts[:, 1], ".", color=MUTED, ms=3.5)
    ax.plot(0, 0, "*", color=S2, ms=16, zorder=5)
    for s in (1, -1):
        ax.plot([0, R * math.cos(s * Om / 2)], [0, R * math.sin(s * Om / 2)], color=S2, ls="--", lw=1.2)
    O, imgs, sep = unfold_images(Om, 7.0, 7.5)
    for v in imgs:
        ax.plot([O[0], v[0]], [O[1], v[1]], color=S1, lw=2)
        ax.plot(*v, "o", color=S1, ms=8)
    ax.plot(*O, "s", color=INK_2, ms=8)
    ax.text(O[0] - 0.3, O[1] - 1.2, "observer", ha="center", color=INK_2, fontsize=9)
    ax.text(imgs[0][0] - 1.0, imgs[0][1] + 0.6, "source (image 1)", color=S1, fontsize=9, ha="right")
    ax.text(imgs[1][0] - 1.0, imgs[1][1] - 0.9, "same source (image 2)", color=S1, fontsize=9, ha="right")
    ax.text(-0.4, -1.0, "defect", color=S2, fontsize=9, ha="right")
    ax.text(R * 0.62, 0.0, "60° wedge\nremoved;\ndashed edges\nare glued", color=S2, fontsize=8.5, va="center")
    ax.set_aspect("equal")
    ax.set(xlim=(-R - 1, R + 2.5), ylim=(-R - 0.5, R + 0.5), xticks=[], yticks=[],
           title=f"A 5-fold disclination in the substrate:\nlight passing either side forms two images ({math.degrees(sep):.0f}° apart)")
    ax.grid(False)
    for sp_ in ax.spines.values():
        sp_.set_visible(False)

    ax = axs[1]
    names = [o[0].split(",")[0].replace(" lattice", "") + "\n" + o[0].split(",")[1].strip() for o in out]
    vals = [o[2] for o in out]
    y = np.arange(len(out))
    ax.barh(y, vals, color=S2, height=0.5, label="crystal disclination line (computed)")
    ax.axvline(GMU_CMB, color=S1, lw=2, label="observed limit (CMB)")
    ax.set_xscale("log")
    for yi, v in zip(y, vals):
        ax.text(v * 1.3, yi, f"Gμ = {v:.3f}", va="center", color=INK_2, fontsize=9)
    ax.set(yticks=y, yticklabels=names, xlim=(1e-8, 2), ylim=(-0.6, len(out) + 0.3),
           xlabel="string tension Gμ/c² (deficit angle / 8π)",
           title="A crystal substrate's defect lines would be cosmic strings\n3–6 × 10⁵ times heavier than allowed")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save_fig(fig, NAME, "disclination_lensing")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
