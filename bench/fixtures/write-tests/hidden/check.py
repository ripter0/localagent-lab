"""The model's test_slugify.py must pass on the real slugify and catch at least 2 of 3 broken versions."""
import os
import shutil
import subprocess
import sys
import tempfile

ORIGINAL = open("slugify.py", encoding="utf-8").read()
MUTANTS = {
    "no lower()": ORIGINAL.replace(".lower()", ""),
    "no strip('-')": ORIGINAL.replace('return text.strip("-")', "return text"),
    "no + in regex": ORIGINAL.replace("[^a-z0-9]+", "[^a-z0-9]"),
}
assert os.path.exists("test_slugify.py"), "test_slugify.py missing"
assert all(m != ORIGINAL for m in MUTANTS.values()), "slugify.py was changed"


def tests_pass(source):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy("test_slugify.py", d)
        with open(os.path.join(d, "slugify.py"), "w", encoding="utf-8") as f:
            f.write(source)
        return subprocess.run([sys.executable, "test_slugify.py"], cwd=d, capture_output=True,
                              timeout=20).returncode == 0


assert tests_pass(ORIGINAL), "the tests fail on the correct slugify"
caught = [name for name, src in MUTANTS.items() if not tests_pass(src)]
assert len(caught) >= 2, f"tests caught only {len(caught)}/3 bugs: {caught}"
print(f"OK, caught {len(caught)}/3")
