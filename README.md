# localagent-lab

**Building a coding agent from scratch to learn how AI agents really work.** It runs fully on my own PC, with free open models only. Everything is measured, nothing is assumed.

The repo has two parts:

1. **`agent.py`: the agent I'm building**, in plain Python, one milestone at a time. It's the learning project.
2. **A ready-made local assistant ([OpenCode](https://opencode.ai))** for everyday help: questions, small code fixes, and explaining lessons from [ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch). Its config is in [`setup/opencode/`](setup/opencode).

Both use the same model, served by Ollama on the GPU.

```mermaid
flowchart TD
    O["Ollama: qwen3.5:9b<br/>RTX 4070 SUPER, 100% GPU"]
    A["agent.py<br/>my agent (learning)"] --> O
    C["OpenCode<br/>daily assistant"] --> O
    A --> W[("workspace/ sandbox")]
    C --> R[("my repos")]
    C --> K[("course repo, read-only")]
```

## How `agent.py` works

The model never touches files itself. On each step it replies with **one JSON action**, and Python runs it:

```mermaid
flowchart TD
    T["Your task"] --> M["Ask the model<br/>(history + tool results)"]
    M --> J{"Valid JSON?<br/>{thought, tool, args}"}
    J -- no --> E["Tell it: invalid format"] --> M
    J -- yes --> F{"tool == finish?"}
    F -- yes --> D["Print summary, stop"]
    F -- no --> X["Run the tool<br/>list_dir / read_file / write_file<br/>replace_in_file / run_command"]
    X --> L["Log the step to logs/*.jsonl"]
    L --> S{"Step 50?"}
    S -- no --> M
    S -- yes --> Z["Stop: step limit"]
```

Safety:
- Files are restricted to `./workspace`. Any path outside it is refused.
- Every shell command waits for **y/N** approval.
- Commands time out after 30 s.

## Quick start

From a **Windows** `cmd`, not WSL (why: [SETUP.md](docs/SETUP.md#troubleshooting)):

```bash
python agent.py
```

On startup it prints:

```
Model: qwen3.5:9b, num_ctx: 188416, max tool output: 188416 chars, thinking: False

Task (empty to quit):
```

Type a task, for example "write hello.py that prints hi, then run it". Each step shows the model's thought and the tool it calls.

To use another model, run `set AGENT_MODEL=gemma4:12b` first (`ollama pull` it before). For the daily assistant, run `opencode` in any folder.

Full PC setup, including Ollama settings, PATH, OpenCode and troubleshooting: **[docs/SETUP.md](docs/SETUP.md)**.

## What works (tested 2026-10-25)

| Feature | Status | Measured |
|---|---|---|
| Agent loop with 5 tools and `finish` (incl. `replace_in_file`) | ✅ | "pelican SVG" task done in 3 steps, 32 s |
| JSON replies from qwen3.5:9b | ✅ | `think: false` fixed the empty-reply loops seen on Oct 21 |
| Sandbox (`workspace/`) and command approval | ✅ | |
| Per-step JSONL logs with latency | ✅ | `logs/<timestamp>.jsonl` |
| Automatic `num_ctx`: largest that fits 100% on GPU | ✅ | 8,192 → **188,416** tokens; binary search ~1 min, then cached |
| Whole files to the model; cut output is marked | ✅ | 106k-character file read in one piece, last line found |
| Ollama flash attention and `q8_0` cache | ✅ | 131k context: 9.95 GB spilling → 7.8 GB on GPU |
| OpenCode with the local model | ✅ | Course lesson explained in 14 s; clean 3-line edit on a step-by-step prompt |
| Stops after 3 invalid replies in a row, optional time limit | ✅ | no more 50-step `invalid_format` loops |
| Personal benchmark (`bench/`) | ✅ | 80 tasks in 8 categories, 18 agent projects, 95% intervals ([bench/](bench/README.md)) |
| Tests | ✅ | 130 passing, on WSL and Windows: `uv run pytest` |
| Log summarizer `tools/summarize_log.py` | ⏳ | M1: empty, I write it myself |

Known limits:
- **Model size:** it's a 9B model. Great for focused tasks, weak at big multi-file changes, and it sometimes says "done" too early.
- **Context speed:** big contexts fill up as files are read, so steps get slower over a long run. One focused task per run works best.

## Benchmark

[`bench/`](bench) is a **personal benchmark** of 80 tasks in 8 categories, all checked automatically. It covers:
- the agent's JSON format
- instructions, reasoning, and code with hidden tests
- Italian
- long context up to 75% of `num_ctx`
- safety: dangerous commands, prompt injection, honesty
- **18 realistic mini-projects** the agent must debug, refactor, extend or analyze

It uses fixed seeds, saves after every task (`--resume`), and reports 95% confidence intervals, so you can tell a real difference between models from luck.

```bash
python -m bench.run qwen3.5:9b gemma4:12b --suite full
```

`--suite full` runs everything 3 times, about 1 to 1.5 hours per model. Results: [bench/RESULTS.md](bench/RESULTS.md). The guide and how to add tasks: [bench/README.md](bench/README.md).

Findings so far:
- **[v1](bench/RESULTS-v1.md):** `qwen3.5:9b` scored **80%** without thinking and **97%** with it. Reasoning went from 20% to 80%, but thinking took about 2.6× the time.
- **[v2](bench/RESULTS-v2.md):** `qwen3.5-uncensored` (Q6) scored **88%** and `qwen3.5:9b` (Q4) **84%**. The confidence intervals overlap, so that's no clear winner.
  - Both failed the same agent tasks, because of limits in `agent.py`.
  - Both started reading a passwords file to upload it.
- **v3** fixes all of that: `replace_in_file`, ignoring unknown arguments, safety rules, a speed check. [What changed](bench/README.md#v3-fixes-for-what-v2-found).

## Milestones

| # | Milestone | Done when | Status |
|---|---|---|---|
| M0 | Setup | WSL, `uv`, git, `nvidia-smi`, `ollama list` work; a script prints a reply | ✅ 2026-10-13 |
| M1 | Python basics | CS50P weeks done; log summarizer with tests and type hints | ⏳ in progress |
| M2 | Talk to the model | Send a request, parse a JSON action | code exists |
| M3 | Tools | `list_dir`, `read_file`, `write_file` restricted to `workspace/` | code exists |
| M4 | The loop | A task done end to end; `run_command` needs approval | code exists |
| M5 | Logging | Every step saved to JSONL | code exists |
| M6 | Eval harness | 10 pytest tasks, one command prints a results table | code exists (`bench/`) |
| M7 | Better tools and safety | `replace_in_file`, step and time limits, sandbox | mostly: replace_in_file, limits, allowlist (bench) |
| M8 | Model comparison | 3 models × 2 prompts in a table | ready: needs more models pulled |
| M9 | Advisor mode | `profile.md`, `notes.md`, daily plan | |
| M10 | Decider experiment | One decision point replaced by a small model and compared | |
| M11 | Packaging | README, results, short demo | |

"Code exists" means a first version is in `agent.py`, but the milestone isn't signed off yet. Which course lessons go with each milestone: **[docs/CURRICULUM.md](docs/CURRICULUM.md)**.

## Layout

```
agent.py              the agent (loop, tools, model call, auto num_ctx)
tools/                helper scripts: backup.py, summarize_log.py (M1)
bench/                personal benchmark: tasks/, fixtures/ (agent projects), runner, report, RESULTS.md
tests/                pytest: logging, num_ctx search, output clipping, benchmark checks, backup
prompts/              saved system prompts (an old hackathon one)
docs/SETUP.md         full PC setup, "new PC in 5 steps", troubleshooting
docs/CURRICULUM.md    milestone -> ai-engineering-from-scratch lessons
docs/EXTERNAL.md      things not copied (rizzo-flow, the course, models) and how to restore them exactly
setup/windows/        restore-settings.ps1: Ollama variables, PATH, OpenCode config
setup/ollama/         Modelfiles to rebuild my custom models (qwen3.5-fix, qwen-plannig)
setup/opencode/       working OpenCode config and rules
archive/              snapshots of workspace/ and logs/ (made by tools/backup.py)
notes/                plans and prompts from AI sessions (fine-tuning plan, CleanSignal prompts)
claude-project/       instructions and context for my Claude mentor project
```

Not in git, because they're live folders: `workspace/` (the agent's sandbox) and `logs/` (run logs and the `num_ctx` cache). Their snapshot is in `archive/`; refresh it with `python tools/backup.py`. Also not in git: `.venv/`.

## Settings

| Variable | Default | What it does |
|---|---|---|
| `AGENT_MODEL` | `qwen3.5:9b` | Ollama model to use |
| `AGENT_NUM_CTX` | auto | Force a context size instead of measuring |
| `AGENT_THINK` | off | `1` turns thinking mode on: much better reasoning, ~2.5× slower ([benchmark](bench/RESULTS-v1.md)) |
| `OLLAMA_URL` | `http://localhost:11434/api/chat` | Where Ollama is |
