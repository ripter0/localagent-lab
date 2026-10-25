# PC setup (Windows + Ollama)

Everything here was set up and tested on 2026-10-25 on Windows 11 with an RTX 4070 SUPER (12 GB), Ollama 0.40.11, Python 3.14, Node.js 24 LTS and OpenCode 1.19.4.

## 1. Ollama

Install the Ollama app for Windows, then pull the model:

```bash
ollama pull qwen3.5:9b
```

Set these **user** environment variables (Start → "Edit environment variables for your account"), then quit Ollama from the tray icon and start it again:

| Variable | Value | Why |
|---|---|---|
| `OLLAMA_CONTEXT_LENGTH` | `65536` | Default context for tools that don't set `num_ctx` (OpenCode). Without it, long instructions get cut silently. |
| `OLLAMA_FLASH_ATTENTION` | `1` | Needed for the compressed cache below. |
| `OLLAMA_KV_CACHE_TYPE` | `q8_0` | Stores the context cache at 8 bits, about half the memory. |

Measured effect on qwen3.5:9b. "Max on GPU" is the largest context that still shows 100% GPU in `ollama ps`:

| Setting | 65k context | 131k context | Max on GPU |
|---|---|---|---|
| Default | 7.15 GB | 9.95 GB, spills to RAM | 122,880 |
| Flash attention + `q8_0` | 6.43 GB | 7.8 GB | 188,416 |

Check: `ollama ps` should show `100% GPU` while a model runs.

## 2. Python (for `agent.py`)

Python 3.14 from python.org. Its folder must be on the user PATH:

```
%LOCALAPPDATA%\Programs\Python\Python314
%LOCALAPPDATA%\Programs\Python\Python314\Scripts
```

Then:

```bash
python -m pip install requests
```

`py` (the launcher) is not installed. Use `python`.

## 3. OpenCode (the everyday local assistant)

1. Install Node.js LTS. If `winget` isn't recognized, see Troubleshooting.
   ```bash
   winget install --id OpenJS.NodeJS.LTS -e
   ```
2. Install OpenCode and connect it to Ollama:
   ```bash
   ollama launch opencode --model qwen3.5:9b --yes
   ```
3. Copy the two files from [`setup/opencode/`](../setup/opencode) to `%USERPROFILE%\.config\opencode\`:
   - `opencode.jsonc` makes the local model the default and turns thinking off (`reasoningEffort: none`).
   - `AGENTS.md` holds the rules OpenCode follows on every task: read before edit, re-check after editing, run the tests.

Then, in any folder:

```bash
opencode
```

## 4. The course, as a local reference

Clone the **original** repo only (forks may carry malware). Keep it outside this project:

```bash
git clone --depth 1 https://github.com/rohitg00/ai-engineering-from-scratch.git %USERPROFILE%\ref\ai-engineering-from-scratch
```

Open OpenCode in that folder and ask about any lesson, for example: "read phases/14-agent-engineering/01-the-agent-loop/docs/en.md and explain it". Which lessons go with which milestone: [CURRICULUM.md](CURRICULUM.md).

## 5. WSL (tests only)

The tests run in WSL2 Ubuntu with `uv`:

```bash
uv run pytest
```

Don't run the agent in WSL: see Troubleshooting.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused` on `localhost:11434` | You started the agent inside WSL. In WSL, `localhost` is not Windows, and Ollama runs on Windows. | Run it from a Windows `cmd`. |
| `'python' is not recognized` | The Python folder is not on PATH. | Add the two folders from step 2 and open a new `cmd`. |
| `'py' is not recognized` | The launcher is not installed. | Use `python`. |
| `No module named 'requests'` | It's not installed for the Python that `cmd` runs. | `python -m pip install requests` |
| `'AGENT_MODEL=...' is not recognized` | That's Linux syntax. | In `cmd`: `set AGENT_MODEL=gemma4:12b`, then `python agent.py` |
| `'winget' is not recognized` | The user PATH is missing your WindowsApps folder. | Add `%LOCALAPPDATA%\Microsoft\WindowsApps` to the user PATH. |
| Empty replies, `invalid_format` loops | qwen3.5 thinking mode together with JSON format. | Already fixed: `"think": False` in `agent.py`, `reasoningEffort: none` in OpenCode. |
| OpenCode reads a file, then gives no answer | Same thinking-mode issue. | Use the `opencode.jsonc` from `setup/opencode/`. |
| Model claims a change is already there, edit fails | Small model skipped reading the file. | Ask step by step: "read X, edit it, read it again". `AGENTS.md` asks for this too. |
| PyCharm can't find the interpreter | `PycharmProjects\AI\.venv` is missing. | `python -m venv %USERPROFILE%\PycharmProjects\AI\.venv`, then install `requests` and `pytest` into it. |
