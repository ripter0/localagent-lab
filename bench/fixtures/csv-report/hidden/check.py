import csv
import re
import subprocess
import sys
from collections import defaultdict

totals = defaultdict(int)
with open("sales.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        totals[row["region"]] += int(row["amount"])
expected = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)

out = subprocess.run([sys.executable, "report.py"], capture_output=True, text=True, timeout=20).stdout
got = []
for line in out.splitlines():
    m = re.match(r"^\s*(\w+)\s*:\s*([\d.,]+)\s*$", line)
    if m:
        got.append((m.group(1), float(m.group(2).replace(",", ""))))
assert [(r, float(t)) for r, t in expected] == got, f"expected {expected}, got {got}"
print("OK")
