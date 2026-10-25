from slugify import slugify

assert slugify("Hello World") == "hello-world"
assert slugify("  --Hi!!  there--  ") == "hi-there"
assert slugify("a   b") == "a-b"
assert slugify("Python 3.14") == "python-3-14"
print("ALL OK")
