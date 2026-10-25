import pathlib
import subprocess
import sys

left = [p.name for p in pathlib.Path(".").glob("*.py") if "get_usr" in p.read_text(encoding="utf-8")
        and not p.name.startswith("_hidden")]
assert not left, f"get_usr still used in {left}"
from users import get_user  # noqa: E402

assert get_user(1) == "anna" and get_user(42) == "unknown"
out = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True, timeout=20).stdout.split()
assert out == ["{'user':", "'luca'}", "#3:", "sara", "#9:", "unknown"], out
print("OK")
