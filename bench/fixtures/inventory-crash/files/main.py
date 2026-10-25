from loader import load_items

items = load_items("items.json")
print("total", sum(items.values()))
