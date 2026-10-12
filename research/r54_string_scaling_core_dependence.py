"""
r54 - Is the slow drift of the string-network scaling parameter physical or an artefact of the core width?  (LAB_NOTEBOOK.md entry E49, test T1; GPU)

Question (open item from E48 / r48): the relativistic string network under radiation-era expansion was 'approximately scaling' with xi = 2/(eta sqrt(l_c)) drifting slowly (d ln xi / d ln eta = -0.13
over eta = 16-60), whereas global strings are expected to drift logarithmically UPWARD (their tension and radiation carry ln(xi t / core)).  The constant-comoving-core prescription (Press-Ryden-
Spergel) fixes the core width in comoving units, so ln(xi t / core) changes with the core width.  If the drift is physical, xi(eta) should not depend on the core width once core << horizon; if
it is an artefact of the prescription or of the finite dynamic range, it will.

Same code as r48 (u = eta phi, leapfrog, 512^3 on the GPU, box 256) with the potential strength lambda varied: core width = 1/sqrt(lambda) v = 1, 1.41, 2 (lambda = 1, 0.5, 0.25), v = 1.
Three seeds each.  Measured: xi(eta) = 2 / (eta sqrt(l_c)), the string length per comoving volume l_c from the plaquette windings (L = (2/3) N_p dx).
"""
import math
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import INK_2, MUTED, S1, S2, S3, Report, save_fig, style  # noqa: E402

import torch  # noqa: E402

NAME = "r54_string_scaling_core_dependence"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
N_GRID = int(os.environ.get("R54_N", 512 if DEV == "cuda" else 96))
DX, D_ETA, ETA0 = 0.5, 0.1, 1.0
MARKS = tuple(float(x) for x in os.environ.get("R54_MARKS", "8,10,13,16,20,25,30,36,44,52,60").split(","))
SEEDS = tuple(int(x) for x in os.environ.get("R54_SEEDS", "1,2,3").split(","))
LAMBDAS = tuple(float(x) for x in os.environ.get("R54_LAMBDAS", "1.0,0.5,0.25").split(","))


def laplacian(u):
    lap = -6.0 * u
    for d in range(3):
        lap += torch.roll(u, 1, d)
        lap += torch.roll(u, -1, d)
    return lap / DX ** 2


def windings_count(u):
    th = torch.angle(u)
    twopi = 2.0 * math.pi
    wr = lambda d: torch.remainder(d + math.pi, twopi) - math.pi
    total = 0
    ti, tj, tk = torch.roll(th, -1, 0), torch.roll(th, -1, 1), torch.roll(th, -1, 2)
    tjk = torch.roll(tj, -1, 2)
    total += int(torch.count_nonzero(torch.round((wr(tj - th) + wr(tjk - tj) + wr(tk - tjk) + wr(th - tk)) / twopi)))
    tik = torch.roll(ti, -1, 2)
    total += int(torch.count_nonzero(torch.round((wr(tk - th) + wr(tik - tk) + wr(ti - tik) + wr(th - ti)) / twopi)))
    tij = torch.roll(ti, -1, 1)
    total += int(torch.count_nonzero(torch.round((wr(ti - th) + wr(tij - ti) + wr(tj - tij) + wr(th - tj)) / twopi)))
    return total


def run(seed, lam, marks):
    g = torch.Generator(device=DEV).manual_seed(seed)
    n = N_GRID
    phase = torch.rand((n, n, n), generator=g, device=DEV, dtype=torch.float32) * (2.0 * math.pi)
    u = (ETA0 * torch.polar(torch.ones_like(phase), phase)).to(torch.complex64)
    del phase
    eta = ETA0

    def acc(u_, eta_):
        return laplacian(u_) - lam * ((u_.real ** 2 + u_.imag ** 2) / eta_ ** 2 - 1.0) * u_

    vel = (u / ETA0).clone()
    vel += 0.5 * D_ETA * acc(u, eta)
    out = {}
    for mark in marks:
        while eta < mark - 1e-9:
            u += D_ETA * vel
            eta += D_ETA
            vel += D_ETA * acc(u, eta)
        out[mark] = windings_count(u)
    return out


def main():
    t_start = time.time()
    p = Report(NAME)
    style(plt)
    name_dev = torch.cuda.get_device_name(0) if DEV == "cuda" else "CPU"
    p(f"Device: {name_dev}.  Lattice {N_GRID}^3, dx = {DX} (box {N_GRID * DX:g}); lambda = {LAMBDAS} (core widths {', '.join(f'{1 / math.sqrt(l):.2f}' for l in LAMBDAS)}); seeds {SEEDS}; marks {MARKS}.")
    vol = (N_GRID * DX) ** 3
    xi = {}
    for lam in LAMBDAS:
        counts = []
        for s in SEEDS:
            t0 = time.time()
            counts.append(run(s, lam, MARKS))
            print(f"    lambda {lam}: seed {s} done in {time.time() - t0:.0f} s", flush=True)
        xi[lam] = []
        for m in MARKS:
            npm = float(np.mean([c[m] for c in counts]))
            lc = (2.0 / 3.0) * npm * DX / vol
            xi[lam].append(2.0 / (m * math.sqrt(lc)) if lc > 0 else float("nan"))
        xi[lam] = np.array(xi[lam])

    p.section("T1. xi(eta) for three core widths")
    marks_a = np.array(MARKS)
    p(f"    {'eta':>6s} | " + " | ".join(f"core {1 / math.sqrt(l):4.2f}  xi" for l in LAMBDAS))
    for i, m in enumerate(MARKS):
        p(f"    {m:6.1f} | " + " | ".join(f"{xi[l][i]:14.3f}" for l in LAMBDAS))
    late = marks_a >= 25                     # core <= 2 << horizon only from eta ~ 25 on: the largest core is still forming at eta = 16
    p("")
    p(f"    {'core':>6s} {'mean xi (eta >= 25)':>20s} {'d ln xi / d ln eta':>20s} {'xi(60) / xi(25)':>16s}")
    slopes, means, ratios = {}, {}, {}
    for lam in LAMBDAS:
        slopes[lam] = float(np.polyfit(np.log(marks_a[late]), np.log(xi[lam][late]), 1)[0])
        means[lam] = float(np.mean(xi[lam][late]))
        ratios[lam] = float(xi[lam][-1] / xi[lam][np.argmin(np.abs(marks_a - 25))])
        p(f"    {1 / math.sqrt(lam):6.2f} {means[lam]:20.3f} {slopes[lam]:20.3f} {ratios[lam]:16.3f}")
    spread_slope = max(slopes.values()) - min(slopes.values())
    spread_mean = (max(means.values()) - min(means.values())) / np.mean(list(means.values()))
    p(f"    => the drift exponent varies by {spread_slope:.2f} across core widths (individual values {min(slopes.values()):+.2f} to {max(slopes.values()):+.2f}); the mean xi by {spread_mean:.0%}.")
    drift_phys = abs(spread_slope) < 0.06
    p(f"    A drift that is the same for every core width is a property of the network; one that changes with the core is an artefact of the prescription.")
    p(f"    Verdict of this test: the drift is {'THE SAME for all core widths (to 0.06 in the exponent, eta >= 25): physical within this dynamic range' if drift_phys else 'CORE-DEPENDENT: at least partly an artefact of the constant-comoving-core prescription and the finite dynamic range'}.")
    late16 = marks_a >= 16
    p("    For comparison, over eta >= 16 (the largest core is still forming there): " + ", ".join(f"core {1 / math.sqrt(l):.2f}: {np.polyfit(np.log(marks_a[late16]), np.log(xi[l][late16]), 1)[0]:+.2f}" for l in LAMBDAS))

    p.section("Verdict (every number below is computed above)")
    p(f"   T1: the slow drift of xi found in r48 is independent of the core width -> {'YES' if drift_phys else 'NO'}: d ln xi / d ln eta = " + ", ".join(f"{slopes[l]:+.2f} (core {1 / math.sqrt(l):.2f})" for l in LAMBDAS))
    p(f"   runtime {time.time() - t_start:.0f} s")

    fig, ax = plt.subplots(1, 1, figsize=(7.4, 5.2))
    for lam, col, mk in zip(LAMBDAS, (S1, S2, S3), ("o", "s", "^")):
        ax.plot(marks_a, xi[lam], mk + "-", color=col, ms=7, label=f"core width {1 / math.sqrt(lam):.2f}")
    ax.set(xlabel="conformal time η", ylabel="correlation length ÷ horizon, ξ = 2 / (η √l_c)", ylim=(0.8, 2.4),
           title="The drift of ξ for three core widths")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, NAME, "core_dependence")
    plt.close(fig)
    p.save()


if __name__ == "__main__":
    main()
