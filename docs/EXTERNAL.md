# External projects and downloads

Things this project uses that are **not** copied into the repo. They're too big or someone else's, but each one can be restored exactly.

| What | Where it was | How to get it back |
|---|---|---|
| **rizzo-flow** (decision model, by Rizzo AI Academy) | `Desktop\ai test pazzi\rizzo-flow`, 5.5 GB with models | See below |
| **ai-engineering-from-scratch** (the course) | `%USERPROFILE%\ref\ai-engineering-from-scratch` | `git clone --depth 1 https://github.com/rohitg00/ai-engineering-from-scratch.git %USERPROFILE%\ref\ai-engineering-from-scratch` |
| **qwen3.5:9b** (main model, 6.6 GB) | Ollama | `ollama pull qwen3.5:9b` |
| **qwen3.5-fix**, **qwen-plannig** | Ollama, same weights as qwen3.5:9b | `ollama create qwen3.5-fix -f setup\ollama\qwen3.5-fix.Modelfile` (same for qwen-plannig) |
| **qwen3.5-uncensored** (DavidAU Defiant Fable Heretic, Q6_K, 8.0 GB, refusals removed) | `%USERPROFILE%\models\qwen3.5-uncensored\` + Ollama | Download link, sha256 and steps are in [setup/ollama/qwen3.5-uncensored.Modelfile](../setup/ollama/qwen3.5-uncensored.Modelfile) |
| **OpenCode** 1.19.4 and Node.js LTS | npm / winget | [SETUP.md](SETUP.md#3-opencode-the-everyday-local-assistant) |

## rizzo-flow

The local copy was a clean clone with no local changes, at this commit:

```
b9ba007ee4d2928bbab5b1d8bfe9009c3696b6de   2026-09-25   "SemIf fixtures on the fine-tuned weights"
```

To get exactly that version back:

```bash
git clone https://github.com/Rizzo-AI-Academy/rizzo-flow.git
```

```bash
git -C rizzo-flow checkout b9ba007ee4d2928bbab5b1d8bfe9009c3696b6de
```

Then, inside `rizzo-flow`:

```bash
uv run rizzo download
```

That last command fetches the parts that aren't in git:
- the llama.cpp runtime for this machine;
- the fine-tuned model `models/rizzo-flow/spark-x2.5-4b-rizzo-flow-lora-q8_0.gguf`, about 4.4 GB.
