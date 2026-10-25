import csv
from collections import defaultdict

totals = defaultdict(int)
with open("sales.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        totals[row["region"]] += int(row["amount"])
for region, total in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
    print(f"{region}: {total}")
