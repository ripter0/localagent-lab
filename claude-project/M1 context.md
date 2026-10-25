**Done when:** you've finished the CS50P weeks covering functions, dicts, files and `pytest`, and written a small tool with tests and type hints.

## Where I am

- M0 done (2026-10-13): wsl, uv, git, nvidia-smi, ollama list verified; `agent.py` has `AGENT_MODEL` env var, per-run JSONL logs, utf-8 file I/O; pytest passes; `qwen3.5:9b` fits at 100% GPU.
- In WSL, `uv run pytest` failed because `requests` was missing. Fix: `uv add requests`, then re-run (result to confirm).
- Working directory in WSL: `/mnt/c/Users/<me>/PycharmProjects/AI/agent`.
- Started CS50P Lecture 0 and found it too easy. Plan: test out via the problem sets and move on.
- Course route: Audit or cs50.harvard.edu/python (free). No paid certificate.

## The tool to build: log summarizer

- `tools/summarize_log.py` with `summarize_log(path: Path) -> dict[str, int]`: counts tool calls per tool from one JSONL log.
- A small `main()` that prints a table.
- `tests/test_summarize.py` with four tests:
    1. normal log
    2. empty file
    3. broken-JSON line
    4. the `{"event": "start"}` line is ignored
- Every function has type hints.

## Decisions from the real log

- The first line is `{"event": "start", ...}` and has no `"tool"` key. Step lines have `"tool"`. The tool skips any line without `"tool"`.
- Open question: what is the last line of a log? Run `tail -n 1` on one log and check whether there is an end line or just a final step.

## Learning order

1. CS50P Lectures 0 to 2 (functions, conditionals, loops with lists and dicts). Test out via the problem sets.
2. Lecture 3 (exceptions), Lecture 5 (unit tests, where pytest is taught), Lecture 6 (file I/O), then type hints.
3. Write the tool test-first: one failing test, then just enough code to pass it.

Lecture numbers are from memory. Check them on the course site.

## Time

About 3 to 4 weeks at 4 hrs/week. Studies come first.

## Parked for later (not M1)

- The agent ran on Windows `cmd.exe`, so the model's Linux heredoc command failed. Fix in M4/M7: tell the model its OS in the system prompt, or run the agent from WSL.
- `read_file` output looks truncated by `MAX_OUTPUT` (4000 characters). Unconfirmed, but likely relevant to the snake_game task.

## When M1 is done

Ask for the 3-line status block to paste into the milestone table in `PROJECT_CONTEXT.md`.