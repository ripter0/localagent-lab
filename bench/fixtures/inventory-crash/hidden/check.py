import json
import os
import tempfile

from loader import load_items

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "x.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"items": [{"name": "a", "qty": 1}, {"name": "b", "quantity": 4}]}, f)
    assert load_items(path) == {"a": 1, "b": 4}, load_items(path)
print("OK")
