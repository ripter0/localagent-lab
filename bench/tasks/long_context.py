"""
Long-context tasks, generated to fit each model's num_ctx. Task ids are the same for every model,
so results line up: needle-4k/16k/64k (skipped if they don't fit), then the rest at 50-75% of num_ctx.
"""
import random

from bench.tasks.core import Task, json_values, parse_json

CHARS_PER_TOKEN = 2.8  # measured on these log lines with qwen3.5 (numbers tokenize badly; prose is ~4)
CODE_CHARS_PER_TOKEN = 3.3  # Python code tokenizes a bit better

CITIES = ["Torino", "Napoli", "Bari", "Genova", "Bologna", "Firenze", "Palermo", "Trieste", "Verona", "Pisa"]
WEATHER = ["sunny", "rainy", "windy", "foggy", "cloudy", "snowy"]
VERBS = ["adjust", "compute", "scale", "update", "normalize", "check", "prepare", "merge", "load", "apply"]
NOUNS = ["reading", "sample", "budget", "order", "report", "signal", "record", "batch", "metric", "value"]


def haystack(n_tokens, needles, seed=0):
    """About n_tokens of boring log lines, with each (depth, line) needle inserted at depth 0-1."""
    rnd = random.Random(seed)
    lines, chars = [], 0
    while chars < n_tokens * CHARS_PER_TOKEN:
        line = (f"Log {len(lines):06d}: in {rnd.choice(CITIES)} the weather was {rnd.choice(WEATHER)} "
                f"and {rnd.randint(10, 999)} people took the bus.")
        lines.append(line)
        chars += len(line) + 1
    for depth, needle in sorted(needles, reverse=True):  # insert from the back so depths stay right
        lines.insert(int(len(lines) * depth), needle)
    return "\n".join(lines)


def code_haystack(n_tokens, target_name, seed=0):
    """A big generated Python module. Exactly one function converts Celsius to Kelvin."""
    rnd = random.Random(seed)
    funcs, chars, target_at = [], 0, None
    while chars < n_tokens * CODE_CHARS_PER_TOKEN:
        noun = rnd.choice(NOUNS)
        f = (f"def {rnd.choice(VERBS)}_{noun}_{len(funcs):04d}(x):\n"
             f'    """Scale the value for the {noun} report by a fixed factor."""\n'
             f"    return x * {rnd.randint(2, 9)} + {rnd.randint(0, 99)}\n")
        funcs.append(f)
        chars += len(f) + 1
    target_at = int(len(funcs) * 0.6)
    funcs.insert(target_at, f'def {target_name}(x):\n    """Convert a temperature from Celsius to Kelvin."""\n'
                            f"    return x + 273.15\n")
    return "\n".join(funcs)


def code_check(code):
    def check(reply):
        return code in (reply or ""), (reply or "")[:60]
    return check


def function_check(name):
    def check(reply):
        data = parse_json(reply) or {}
        got = str(data.get("function", "")).strip().removesuffix("()")
        return got == name, f"got {got!r}"
    return check


def long_context_tasks(num_ctx):
    salt = f"Session {random.randrange(16**8):08x}\n"  # new first line each run: Ollama can't reuse a cached prompt
    big = int(num_ctx * 0.75)
    half = int(num_ctx * 0.5)
    ask_code = '\n\nWhat is the secret vault code? Reply only with JSON: {"code": "<code>"}.'
    tasks = []

    def needle(task_id, size, depth, code, seed):
        text = salt + haystack(size, [(depth, f"IMPORTANT: the secret vault code is {code}.")], seed=seed)
        tasks.append(Task(task_id, "long-context", "chat", text + ask_code, code_check(code), json_mode=True,
                          max_tokens=64, good=f'{{"code": "{code}"}}', bad='{"code": "0000"}'))

    for i, size in enumerate((4_000, 16_000, 64_000)):
        if size < big:
            needle(f"needle-{size // 1000}k", size, [0.5, 0.25, 0.75][i], str(7391 + 391 * i), seed=i)
    needle("needle-max-middle", big, 0.5, "8564", seed=10)
    needle("needle-max-start", big, 0.03, "2718", seed=11)
    needle("needle-max-end", big, 0.97, "3141", seed=12)

    codes = {"red": "4821", "green": "9056", "blue": "1377"}
    text = salt + haystack(half, [(0.2, f"NOTE: the red vault code is {codes['red']}."),
                                  (0.5, f"NOTE: the green vault code is {codes['green']}."),
                                  (0.8, f"NOTE: the blue vault code is {codes['blue']}.")], seed=13)
    tasks.append(Task("multi-needle", "long-context", "chat",
                      text + '\n\nThere are three vault codes in the log above. Reply only with JSON: '
                             '{"red": "<code>", "green": "<code>", "blue": "<code>"}.',
                      json_values(**codes), json_mode=True, max_tokens=96,
                      good='{"red": "4821", "green": "9056", "blue": "1377"}',
                      bad='{"red": "4821", "green": "0000", "blue": "1377"}'))

    target = "adjust_reading_k7342"  # the 'k' keeps it unique among the numbered decoys
    module = code_haystack(half, target, seed=14)
    tasks.append(Task("code-search", "long-context", "chat",
                      salt + "Here is a Python module:\n\n" + module +
                      '\n\nWhich function converts a temperature from Celsius to Kelvin? '
                      'Reply only with JSON: {"function": "<name>"}.',
                      function_check(target), json_mode=True, max_tokens=64,
                      good=f'{{"function": "{target}"}}', bad='{"function": "adjust_reading_0001"}'))
    return tasks
