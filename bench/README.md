# Personal benchmark

A benchmark made for **my** use: the agent's JSON format, small code tasks, Italian, long files, and real agent runs in a sandbox. Public leaderboards test other things, so I don't trust them for my setup. Everything is scored automatically, so a run is repeatable and models can be compared fairly.

**Results: [RESULTS.md](RESULTS.md)**: leaderboard, chart, every task, and the pelican gallery.

## Findings (2026-10-25, qwen3.5:9b, 1 run per task)

1. **Thinking mode is the biggest lever: 80% → 97%.**
   - Reasoning went from 20% to 80%. Without thinking, the model has to answer instantly, and it got 53 − 7 = 41-style mistakes; with thinking it works them out.
   - Instructions went 75% → 100% (the "no letter e" sentence) and Italian 67% → 100% (it answered "Padre" for Italy's longest river, then "Po" with thinking).
   - **The cost:** 12.0 min instead of 4.6 for the whole benchmark, about 2.6× slower.
2. **For agent tasks, thinking doesn't help yet.**
   - Both modes passed all 6 agent tasks, with the same number of steps. Thinking was about 30% slower.
   - So the agent default stays *off*, and you can turn it on for hard tasks with `set AGENT_THINK=1`.
   - The Oct 21 runs gave empty replies with thinking and JSON. That didn't happen here, with 188k context and a bigger `num_predict`. The cause isn't proven.
3. **Code is solid:** 4/4 in both modes, checked by hidden tests.
4. **Long context really works.**
   - Both modes found the hidden code at **141,302 real tokens**, 75% of the context.
   - The model reads about 2,600 to 3,900 tokens/s, so a 141k prompt takes about 55 s just to read.
5. **Still hard: counting letters.** "How many r's in strawberry raspberry" failed in both modes (answers 4 and 5, correct is 6). Models see *tokens*, not letters. This is a famous weakness of LLMs.
6. **Two bugs in my own benchmark**, found by checking a result that looked suspicious:
   - **Wrong token estimate.** I assumed 4 characters per token, but log lines full of numbers average **2.8**. My "141k" test was really about 200k tokens, more than the context.
   - **Silent cutting.** Ollama then **cut the prompt silently to half the context** (94,210 tokens). The hidden code was lost, and the model "failed" a test it never really got. The benchmark now detects cut prompts and reports them.
   - **Faked speed.** The second run's "read speed" was faked by Ollama's prompt cache. Each haystack now gets a random first line, so it can't be reused.
   - Lesson: **check a surprising result before you believe it.**

One run per task means a single pass or fail is partly luck. Run `--repeat 3` before trusting a difference of one or two tasks.

## Run it

From the repo root, in a Windows `cmd` (Ollama must be running):

```bash
python -m bench.run qwen3.5:9b
```

| Command | What it does |
|---|---|
| `python -m bench.run qwen3.5:9b gemma4:12b` | Compare several models in one go |
| `python -m bench.run qwen3.5:9b+think` | Same model with **thinking mode on** |
| `python -m bench.run qwen3.5:9b --quick` | Skip agent and long-context tasks (~1 min) |
| `python -m bench.run qwen3.5:9b --only code,reasoning` | Only these categories (or task ids) |
| `python -m bench.run qwen3.5:9b --repeat 3` | Each task 3 times. Models are random, so this gives steadier numbers |
| `python -m bench.report` | Rebuild RESULTS.md from saved results |

A full run takes about 10 to 20 minutes per model. Models that aren't installed are skipped, with the `ollama pull` command to install them.

## What it tests

| Category | Tasks | How it's checked |
|---|---|---|
| **JSON tools** | 5 requests in `agent.py`'s action format (list, read, write, run, finish) | Valid JSON, right tool, right args |
| **Instructions** | Exactly 3 lowercase words, YES/NO only, a JSON list of 5, a sentence without the letter "e" | Exact rules |
| **Reasoning** | Apples, discount+tax, bat and ball, counting the r's in "strawberry raspberry", the weekday in 100 days | Exact answer |
| **Code** | `is_palindrome`, `roman_to_int`, `merge_intervals`, `word_count` | The model's code is run against hidden tests |
| **Italiano** | IT→EN, EN→IT, a fact question in Italian | Key words / exact answer |
| **Long context** | Find a secret code hidden in 4k, 16k, 64k tokens of logs, then in ~75% of the model's whole context | Exact code |
| **Agent** | The full `agent.py` loop, in a fresh temp folder | The resulting files are checked |

The agent tasks:
- **hello-script:** create a file and run it.
- **fix-bug:** two bugs in `stats.py`. Editing the check file counts as cheating.
- **multi-file:** change two files that depend on each other.
- **read-config:** find a value somewhere in the project.
- **honesty:** read a file that **doesn't exist**. It passes only if the model says so instead of making something up.
- **pelican:** draw an SVG pelican riding a bicycle. The drawing is saved to `results/artifacts/` and shown in RESULTS.md, so you can see each model's drawing.

Scores:
- **Category score** = tasks passed / tasks run.
- **Overall** = the mean of the category scores, so a category with 5 tasks weighs the same as one with 4.

Also measured, per model:
- **Speed:** generated tokens per second.
- **Reads:** prompt tokens per second on the long-context tasks.
- **Context:** the `num_ctx` that fits 100% on the GPU.
- **Memory:** GPU % and GB.

## Safety

The agent tasks run without asking you. Instead, every command goes through an **allowlist** (`is_allowed` in [run.py](run.py)):
- **Allowed:** `python <file>.py` with a relative path, plus `dir`, `ls`, `type` and `cat`.
- **Refused:** anything with `..`, absolute paths, `&`, `|`, `>`, `;` or `%`, and every other command, such as `del` or `python -c`.

Each agent task runs in a new temp folder that is deleted afterwards. The code tasks run the model's code in a temp folder, with a 15 s timeout. The model writing the code is a local 9B model working on simple tasks, so the risk is low. Still, don't add tasks that invite destructive code.

## Add a task

Tasks are plain Python in [tasks.py](tasks.py). A chat task is one prompt plus a check function:

```python
Task("capital", "italiano", "chat", "Qual è la capitale d'Italia? Una parola.",
     text_matches(r"^\W*roma\W*$")),
```

Then add a test for the check in `tests/test_bench.py`: one right answer and one wrong one. That way a broken check can't silently give wrong scores.

## Ideas to try

- **Thinking on or off.** Does `+think` fix reasoning, and does it break JSON? This one is already measured in RESULTS.md.
- **Models worth comparing on 12 GB**, all checked to exist in the Ollama library on 2026-10-25:
  - `gemma4:12b`: general use
  - `qwen2.5-coder:14b`: code specialist
  - `qwen3.5:4b`: small and fast, a candidate for the M10 decider
- **Settings:** the same model at `AGENT_NUM_CTX=8192` vs. the automatic maximum. Does a smaller context make it faster, or better?
- **Variance:** `--repeat 5` on one model shows how much the score moves between runs. Only trust a difference between models if it's bigger than that.
- **Your own tasks:** every time a model fails at something real, add it as a task. That's how the benchmark becomes truly personal.
