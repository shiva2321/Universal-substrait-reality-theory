"""Run every research/rNN_*.py script; each writes research/results/ and research/figures/."""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    env = dict(os.environ, MPLBACKEND="Agg")
    failed = []
    for script in sorted(glob.glob(os.path.join(HERE, "r[0-9][0-9]_*.py"))):
        name = os.path.basename(script)
        print(f"--- running {name}")
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, env=env)
        if r.returncode != 0:
            failed.append(name)
            print(r.stderr[-2000:])
        else:
            print(f"    ok -> results/{name.replace('.py', '.txt')}")
    print("all ok" if not failed else f"FAILED: {failed}")
    sys.exit(1 if failed else 0)
