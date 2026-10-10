"""
Shared helpers for the research/ calculations.

Every research script:
  * imports its constants from audit/common.py (CODATA 2022 / PDG 2024 / Planck 2018),
  * prints its results AND writes them to research/results/<script>.txt,
  * saves every figure to research/figures/<script>_<name>.png,
  * gets a dated entry in research/LAB_NOTEBOOK.md.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "audit"))
from common import G, alpha, c, e, eV, hbar, planck_length, planck_mass  # noqa: E402,F401

G0 = G[0]          # m^3 kg^-1 s^-2 (audit/common.py stores (value, sigma))
ALPHA = alpha[0]   # fine-structure constant

RESULTS = os.path.join(HERE, "results")
FIGURES = os.path.join(HERE, "figures")

# Chart roles (reference palette, light surface). Max three series per chart.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#9a9993"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # blue, orange, aqua


class Report:
    """Collects printed lines and writes them to research/results/<name>.txt."""

    def __init__(self, name):
        self.name = name
        self.lines = []

    def __call__(self, *parts):
        line = " ".join(str(p) for p in parts)
        print(line)
        self.lines.append(line)

    def section(self, title):
        bar = "=" * 78
        self("")
        self(bar)
        self(title)
        self(bar)

    def save(self):
        os.makedirs(RESULTS, exist_ok=True)
        path = os.path.join(RESULTS, self.name + ".txt")
        with open(path, "w") as f:
            f.write("\n".join(self.lines) + "\n")
        print(f"\n[saved] {os.path.relpath(path, os.path.dirname(HERE))}")


def style(plt):
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK_2, "ytick.color": INK_2, "grid.color": "#e4e3df",
        "axes.grid": True, "grid.linewidth": 0.8, "axes.spines.top": False,
        "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
        "axes.titleweight": "bold", "legend.frameon": False, "lines.linewidth": 2.0,
    })


def save_fig(fig, script, name):
    os.makedirs(FIGURES, exist_ok=True)
    path = os.path.join(FIGURES, f"{script}_{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[saved] {os.path.relpath(path, os.path.dirname(HERE))}")
    return path


def mP():
    return planck_mass()[0]


def lP():
    return planck_length()
