import json


def load_items(path):
    """Read items.json and return {name: quantity}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {item["name"]: item["qty"] for item in data["items"]}
