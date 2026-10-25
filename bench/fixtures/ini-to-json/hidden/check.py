import json

with open("settings.json", encoding="utf-8") as f:
    data = json.load(f)
expected = {"app": {"name": "Demo", "debug": True, "port": 8080, "ratio": 0.75},
            "db": {"host": "localhost", "user": "admin", "pool": 5}}
assert data == expected, f"got {data}"
assert isinstance(data["app"]["debug"], bool) and isinstance(data["app"]["port"], int)
print("OK")
