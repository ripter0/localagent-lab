import subprocess
import sys


def lines(*args):
    r = subprocess.run([sys.executable, "todo.py", *args], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0, r.stderr[-300:]
    return [l for l in r.stdout.splitlines() if l.strip()]


assert len(lines()) == 4, lines()
assert lines("--limit", "2") == ["[ ] study for the exam", "[x] buy milk"], lines("--limit", "2")
assert lines("--done", "--limit", "1") == ["[x] buy milk"], lines("--done", "--limit", "1")
assert len(lines("--done")) == 2
print("OK")
