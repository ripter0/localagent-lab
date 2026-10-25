import re

# Read the current file
with open('snake_game.html', 'r') as f:
    content = f.read()

print("File length:", len(content))
print("Last 500 chars:")
print(repr(content[-500:]))