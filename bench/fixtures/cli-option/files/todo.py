import argparse
import json

parser = argparse.ArgumentParser(description="Show my todo list")
parser.add_argument("--done", action="store_true", help="show only finished tasks")
args = parser.parse_args()

with open("todo.json", encoding="utf-8") as f:
    tasks = json.load(f)
if args.done:
    tasks = [t for t in tasks if t["done"]]
for t in tasks:
    print(("[x] " if t["done"] else "[ ] ") + t["title"])
