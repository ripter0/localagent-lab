# localagent-lab

A local-first coding agent in plain Python, running free open models through [Ollama](https://ollama.com) on one 12 GB GPU. Everything is measured, nothing is assumed.

`agent.py` is a JSON-action loop with the tools `list_dir`, `read_file`, `write_file`, `run_command` and `finish`. Files are restricted to `./workspace`, and every shell command needs your approval.

## Setup

The model runs in the Ollama app on Windows. Run the agent from Windows too: inside WSL, `localhost:11434` does not reach Windows Ollama.

```bash
pip install requests
ollama pull qwen3.5:9b
python agent.py
```

On startup the agent picks `num_ctx` (the model's working memory) by itself. It loads the model at bigger and bigger sizes and keeps the largest one that still shows 100% GPU in `ollama ps`. The search takes about a minute per model the first time. After that the result is cached in `logs/num_ctx.json` and checked once each start. To force a size, use `set AGENT_NUM_CTX=16384`.

To try another model in `cmd`, run `set AGENT_MODEL=gemma4:12b` and then `python agent.py`. Tests run in WSL with `uv run pytest`.

Check `ollama ps` while it runs: the model should show 100% GPU. Each run writes a step log to `logs/<timestamp>.jsonl`.

## Milestones

| # | Milestone | Status |
|---|---|---|
| M0 | Setup | done 2026-10-13 |
| M1 | Python basics + log summarizer tool | in progress |
| M2 | Talk to the model | |
| M3 | Tools | |
| M4 | The loop | |
| M5 | Logging | |
| M6 | Eval harness | |
| M7 | Better tools and safety | |
| M8 | Model comparison | |
| M9 | Advisor mode | |
| M10 | Decider experiment | |
| M11 | Packaging | |

## Layout

- `agent.py`: the agent
- `tools/`: helper scripts (M1: `summarize_log.py`)
- `tests/`: pytest
- `prompts/`: saved system prompts (for example, an old hackathon one)
- `docs/CURRICULUM.md`: which lessons of [ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) go with each milestone
- `claude-project/`: instructions and context for the Claude project used as a mentor
