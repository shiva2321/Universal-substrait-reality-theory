"""
Audit 03 - Entanglement: what does a "phase-locked vortex cord" actually predict?

The USRT scripts (dark_sector_and_vortex.py, ironclad_theory_refinements.py,
advanced_four_proofs.py) do not simulate any vortex. They type in the quantum
result E(a,b) = -cos(a-b) and then evaluate CHSH, so S = 2*sqrt(2) is an input.

Here three explicit models are simulated:
  A. LOCAL phase lock: the pair shares a hidden phase lambda fixed at creation
     (the '3D phase rigidity' / 'theta_A + theta_B = const' story).
  B. NONLOCAL cord: measuring A instantly re-orients B (a Bohm-type model with a
     preferred frame). It can reproduce quantum mechanics - if the cos law is
     put into the update rule by hand.
  C. The same nonlocal cord with a different update rule: gives S = 4, far above
     quantum mechanics. Nothing in the 'cord' picture selects the quantum value.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import banner  # noqa: E402

rng = np.random.default_rng(7)
N = 400_000
A_ANG = (0.0, math.pi / 2)
B_ANG = (math.pi / 4, 3 * math.pi / 4)   # standard optimal CHSH settings
PAPER_B_ANG = (math.pi / 4, -math.pi / 4)  # settings quoted in the USRT documents


def chsh(Efun, b_angles=None):
    a, a2 = A_ANG
    b, b2 = b_angles or B_ANG
    return abs(Efun(a, b) - Efun(a, b2) + Efun(a2, b) + Efun(a2, b2))


def E_local(a, b):
    lam = rng.uniform(0, 2 * math.pi, N)
    A = np.sign(np.cos(a - lam))
    B = -np.sign(np.cos(b - lam))
    return float(np.mean(A * B))


def E_cord_qm(a, b):
    # A measured first: outcome +-1 with prob 1/2. The cord instantly sets B's axis anti-parallel;
    # B then answers with the quantum rule P(B = -A) = cos^2((a-b)/2) -- inserted by hand.
    A = rng.choice([-1, 1], N)
    p_anti = np.cos((a - b) / 2) ** 2
    B = np.where(rng.random(N) < p_anti, -A, A)
    return float(np.mean(A * B))


def E_cord_pr(a, b):
    # Same cord, different hand-written rule: perfectly anti-correlated unless both use the
    # 'primed' settings (a Popescu-Rohrlich box). Marginals still 50/50 -> no signalling.
    A = rng.choice([-1, 1], N)
    flip = (a == A_ANG[0]) and (b == B_ANG[1])
    B = A if flip else -A
    return float(np.mean(A * B))


def main():
    out = []
    p = out.append
    p(banner("Bell-CHSH test of explicit 'vortex cord' models (400k pairs each)"))
    s_local = chsh(E_local)
    s_qm = chsh(E_cord_qm)
    s_pr = chsh(E_cord_pr)
    s_paper = chsh(lambda x, y: -math.cos(x - y), PAPER_B_ANG)
    p(f"0. Paper's own CHSH arithmetic: E = -cos(a-b), S = |E(a,b)-E(a,b')+E(a',b)+E(a',b')| with the")
    p(f"   quoted angles (0, pi/2, pi/4, -pi/4) gives S = {s_paper:.3f}, not 2.828: a sign slip in the")
    p(f"   documents (2*sqrt2 needs b' = 3pi/4). Standard settings are used below.")
    p(f"A. local shared phase (fixed at creation):   S = {s_local:.3f}   (Bell bound 2)")
    # random search for any better local setting
    best = 0.0
    for _ in range(200):
        angs = rng.uniform(0, 2 * math.pi, 4)
        lam = rng.uniform(0, 2 * math.pi, 50_000)

        def E(x, y):
            return float(np.mean(np.sign(np.cos(x - lam)) * -np.sign(np.cos(y - lam))))
        s = abs(E(angs[0], angs[2]) - E(angs[0], angs[3]) + E(angs[1], angs[2]) + E(angs[1], angs[3]))
        best = max(best, s)
    p(f"   best over 200 random measurement settings: S = {best:.3f}  (never above 2)")
    p(f"B. nonlocal cord + quantum rule put in by hand: S = {s_qm:.3f}   (Tsirelson 2*sqrt2 = {2*math.sqrt(2):.3f})")
    p(f"C. same nonlocal cord + different rule:        S = {s_pr:.3f}   (above any quantum system)")
    p("")
    p("Conclusions")
    p(" - A phase relation fixed at pair creation and carried locally (the '3D phase rigidity' version)")
    p("   is a local hidden-variable model: S <= 2. It cannot explain the measured Bell violations.")
    p(" - An instantaneous cord through a 'bulk' is a NONLOCAL hidden-variable model, like Bohmian")
    p("   mechanics with a preferred frame. Bell's theorem allows such models, and a substrate with a")
    p("   rest frame could host one. That part of the idea is not ruled out.")
    p(" - But the cord picture does not by itself give -cos(a-b) or the value 2*sqrt2: model C uses the")
    p("   same cord and gives 4. The quantum prediction has to be supplied by quantum mechanics, which")
    p("   is exactly what the USRT scripts do (E = -cos is typed in).")
    p(" - 'ER = EPR' (Maldacena-Susskind 2013) is a conjecture about entangled black holes/wormholes in")
    p("   quantum gravity; it does not say entangled particles are joined by fluid vortex tubes.")
    text = "\n".join(out)
    print(text)
    with open(os.path.join(os.path.dirname(__file__), "results", "a03_bell_models.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
