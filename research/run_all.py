"""Run every research/rNN_*.py script; each writes research/results/ and research/figures/.

Usage: python run_all.py [--fast]
  --fast skips the slow scripts (SLOW below): a full run takes more than half an hour (r42 ~11 min, r45 ~5 min, r46 ~4 min at 256^3, r48 needs a GPU).
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SLOW = ("r21", "r29", "r30", "r35", "r39", "r42", "r44", "r45", "r46", "r48")

if __name__ == "__main__":
    env = dict(os.environ, MPLBACKEND="Agg")
    failed = []
    for script in sorted(glob.glob(os.path.join(HERE, "r[0-9][0-9]_*.py"))):
        name = os.path.basename(script)
        if "--fast" in sys.argv and name[:3] in SLOW:
            print(f"--- skipping {name} (--fast)")
            continue
        print(f"--- running {name}")
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, env=env)
        if r.returncode != 0:
            failed.append(name)
            print(r.stderr[-2000:])
        else:
            print(f"    ok -> results/{name.replace('.py', '.txt')}")
    print("all ok" if not failed else f"FAILED: {failed}")
    sys.exit(1 if failed else 0)
