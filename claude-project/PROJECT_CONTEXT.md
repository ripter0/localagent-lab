# localagent-lab: project context

Local-first agent project on my own PC, free open models only. Two modes: **coder** (works in a sandboxed folder, verified by tests) and **advisor** (daily/career planning from a plain-text profile + notes). Core idea: a plain-Python agent loop where one decision point is later replaced by a small fast "System One" decider. Everything is measured, nothing is assumed.

## Me and constraints

- Student, side project. Studies come first.
- Learning Python with CS50P. Background: Java, C#. Explain in English.
- No budget. PC: Ryzen 5 7600, 32 GB RAM, RTX 4070 SUPER 12 GB, Windows + WSL2 Ubuntu, Ollama. Models must fit ~9.5 GB. Do not install NVIDIA drivers inside WSL.
- Time budget: 4hrs/week.

## Existing code

`agent.py`: JSON-action loop (`list_dir`, `read_file`, `write_file`, `run_command`, `finish`), files restricted to `./workspace`, shell commands need my approval.

## Models (test, don't trust rankings)

All benchmark numbers are vendor claims. Last checked 2026-10-13. Details in Local_AIs.md. Fit rule: weights + KV cache at the chosen `num_ctx` must stay under ~9.5 GB. Confirm with `ollama ps` (should show 100% GPU). Always set `num_ctx` explicitly.

- **Starting model (M0-M7):** `qwen3.5:9b` (Ollama tag, ~6.6-7.6 GB). It replaces the Qwen 27B IQ2_XS baseline.
- **M8 comparison (3 models x 2 prompts):** `qwen3.5:9b`, `gemma4:12b` (~7.2-8.0 GB), Nanbeige4.2-3B. Optional extra: `qwen2.5-coder:14b`.
    - Nanbeige4.2-3B: first confirm a trustworthy GGUF/Ollama source. Never use `trust_remote_code` without reading the repo code. Its SWE-Bench 63.6 is a vendor-reported number.
- **Decider candidates (M10):** Spark-X2.5 1.7B/4B, or a ModernBERT-class encoder. Spark's 1M context is a vendor claim. On 12 GB expect 8-32k.
- **Unverified / not preferred:** Qwen3 14B and DeepSeek-R1 14B (older generation, not checked). Qwen3-Coder has no official 14B; the 30B is ~19 GB and does not fit.
- **CLM-8B:** open, but its default recipe needs vLLM and ~16 GB, so unquantized it won't fit 12 GB. Check checkpoint security. Its benchmarks are vendor claims.
- **Known gotcha (unverified on my setup):** qwen3.5 has thinking mode. If `"format": "json"` gives empty or slow replies, try `"think": false` in the request.

## Milestones (one at a time, commit each)

|#|Milestone|Done when|
|---|---|---|
|M0|Setup|WSL, `uv`, git, `nvidia-smi` and `ollama list` all work; one script prints a model reply|
|M1|Python basics(CS50P in parallel)|You finished the course weeks that cover functions, dicts, files and `pytest`, and wrote a small tool with tests and type hints|
|M2|Talk to the model|Send a request to Ollama and parse a JSON action from the reply|
|M3|Tools|`list_dir`, `read_file`, `write_file`, restricted to `workspace/`, tested by hand|
|M4|The loop|The agent completes a task end to end, with `run_command` behind an approval prompt|
|M5|Logging|Every step saved to JSONL|
|M6|Eval harness|10 pytest tasks, one command prints a results table|
|M7|Better tools and safety|`replace_in_file`, step and time limits, sandbox|
|M8|Model Comparison|3 models x 2 prompts compared in a table|
|M9|Advisor mode|`profile.md`, `notes.md`, daily only until M9|
|M10|Decider experiment|One decision point replaced by a small model and compared with the baseline, canidadates: small Spark-X2.5 models (1.7B/4B)|
|M11|Packaging|README, results, short demo, public repo|

## Learning order

Python basics (type hints, dataclasses, Pydantic, pytest, git) -> Ollama + agent loop -> embeddings/ranking -> PyTorch basics -> small decider. Learn theory only when needed. Use only the original `rohitg00/ai-engineering-from-scratch` repo (forks may carry malware): Phase 14 lesson 1 (agent loop), Phase 11 (evaluation, context engineering), Phase 13 (tools). Math-heavy parts in 2nd year; never aim to finish it all.

## Rules for any AI helper

1. Explain in a few lines, then give small code steps I can type and understand.
2. One milestone, one step at a time; plain Python + `requests` before frameworks.
3. Everything new needs a test. Flag anything unverified (versions, models, benchmarks) and tell me when I'm wrong.
4. No destructive commands, no secrets in the repo, file access only in `workspace/`.

## Starter prompt

> Read PROJECT_CONTEXT.md. We are at M0. Review my agent.py and show the smallest changes to make the model name configurable and log each step to JSONL. Explain each change before the code.