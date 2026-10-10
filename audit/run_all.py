"""Run every audit check and write the outputs to audit/results/."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["a01_lattice_dynamics.py", "a02_numerology.py", "a03_bell_models.py", "a04_mechanics_checks.py"]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    failed = []
    for s in SCRIPTS:
        print(f"--- running {s}")
        r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True)
        if r.returncode != 0:
            failed.append(s)
            print(r.stderr)
        else:
            print(f"    ok -> results/{s.replace('.py', '.txt')}")
    sys.exit(1 if failed else 0)
