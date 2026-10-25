import argparse
import json

parser = argparse.ArgumentParser(description="Show my todo list")
parser.add_argument("--done", action="store_true", help="show only finished tasks")
parser.add_argument("--limit", type=int, default=None, help="show at most N tasks")
args = parser.parse_args()

with open("todo.json", encoding="utf-8") as f:
    tasks = json.load(f)
if args.done:
    tasks = [t for t in tasks if t["done"]]
if args.limit is not None:
    tasks = tasks[:args.limit]
for t in tasks:
    print(("[x] " if t["done"] else "[ ] ") + t["title"])
