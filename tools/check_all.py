"""Run apps in separate processes so identical module names do not collide.
Usage: python tools/check_all.py solutions (should pass) or starters (expected failures).
"""
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
mode = sys.argv[1] if len(sys.argv)>1 else "solutions"
paths = sorted((root/"solutions").glob("*")) if mode == "solutions" else sorted(root.glob("block-*/*"))
failed = False
for path in paths:
    if (path/"app.py").exists():
        print(f"\n{path.relative_to(root)}", flush=True)
        result = subprocess.run([sys.executable,"-m","pytest","-q"],cwd=path)
        failed |= result.returncode != 0
sys.exit(1 if failed else 0)
