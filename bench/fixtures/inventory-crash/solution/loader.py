import json


def load_items(path):
    """Read items.json and return {name: quantity}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {item["name"]: item.get("qty", item.get("quantity", 0)) for item in data["items"]}
