"""
Minimal local coding agent for Ollama.

Setup (Windows cmd, where Ollama runs):
    pip install requests
    python agent.py
    set AGENT_MODEL=gemma4:12b    # optional: another model from `ollama list`

The agent works only inside ./workspace. Shell commands need your approval.
"""
import json
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

import requests

MODEL = os.environ.get("AGENT_MODEL", "qwen3.5:9b")  # name shown by `ollama list`
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_BASE = OLLAMA_URL.rsplit("/api/", 1)[0]
CTX_STEP = 8192  # num_ctx is searched in multiples of this
NUM_CTX = CTX_STEP  # replaced at startup by pick_num_ctx()
WORKDIR = Path("workspace").resolve()
WORKDIR.mkdir(exist_ok=True)
MAX_STEPS = 50
MAX_OUTPUT = 4000  # chars of tool output sent back; set from NUM_CTX at startup

# run_command uses shell=True: cmd.exe on Windows, /bin/sh on Linux/WSL
SHELL = "Windows cmd.exe" if platform.system() == "Windows" else "Linux /bin/sh"

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
CTX_CACHE = LOG_DIR / "num_ctx.json"  # best num_ctx found per model


def log_step(log_file, **record):
    record["ts"] = datetime.now().isoformat(timespec="seconds")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


SYSTEM_PROMPT = f"""You are a coding agent working inside a project folder.
You solve the user's task step by step using tools.
Commands run with {SHELL}; use commands for that shell.

On EVERY turn reply with exactly one JSON object and nothing else:
{{"thought": "short reasoning", "tool": "<tool name>", "args": {{...}}}}

Tools:
- list_dir     args: {{"path": "."}}
- read_file    args: {{"path": "main.py"}}
- write_file   args: {{"path": "main.py", "content": "full file content"}}
- run_command  args: {{"command": "python main.py"}}
- finish       args: {{"message": "summary for the user"}}

Rules:
- Look at the files before changing them.
- After writing code, run it or its tests to check that it works.
- If something fails, read the error and fix it.
- Call finish when the task is done.
"""


# ---------- tools ----------
def safe_path(p: str) -> Path:
    full = (WORKDIR / p).resolve()
    if WORKDIR not in full.parents and full != WORKDIR:
        raise ValueError("path is outside the workspace")
    return full


def list_dir(path="."):
    items = sorted(safe_path(path).iterdir())
    return "\n".join(i.name + ("/" if i.is_dir() else "") for i in items) or "(empty)"


def read_file(path):
    return safe_path(path).read_text(encoding="utf-8")


def write_file(path, content):
    f = safe_path(path)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content,encoding="utf-8")
    return f"wrote {len(content)} characters to {path}"


def run_command(command):
    print(f"\n  Agent wants to run: {command}")
    if input("  Allow? [y/N] ").strip().lower() != "y":
        return "The user denied this command."
    try:
        r = subprocess.run(command, shell=True, cwd=WORKDIR,
                           capture_output=True, text=True, timeout=30)
        return f"exit code {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."


def clip(text):
    """Cut tool output to MAX_OUTPUT and say so, so the model knows it saw only part."""
    if len(text) <= MAX_OUTPUT:
        return text
    return text[:MAX_OUTPUT] + f"\n[truncated: showed {MAX_OUTPUT} of {len(text)} characters]"


TOOLS = {"list_dir": list_dir, "read_file": read_file,
         "write_file": write_file, "run_command": run_command}


# ---------- model call ----------
def ask_model(messages):
    r = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "format": "json",  # forces valid JSON output
        "think": False,  # qwen3.5 thinking mode + json format gave empty replies
        "options": {"temperature": 0.2, "num_ctx": NUM_CTX, "num_predict": 4096},
    }, timeout=600)
    r.raise_for_status()
    return r.json()["message"]["content"]


# ---------- context size ----------
def model_max_ctx(model):
    """Context length the model was trained for, from `ollama show`."""
    r = requests.post(f"{OLLAMA_BASE}/api/show", json={"model": model}, timeout=60)
    r.raise_for_status()
    info = r.json().get("model_info", {})
    return next((v for k, v in info.items() if k.endswith(".context_length")), CTX_STEP)


def fits_on_gpu(model, num_ctx):
    """Load the model with this num_ctx and check that `ollama ps` shows 100% GPU."""
    r = requests.post(f"{OLLAMA_BASE}/api/generate", json={
        "model": model, "prompt": "", "stream": False,  # empty prompt: load only
        "options": {"num_ctx": num_ctx},
    }, timeout=600)
    r.raise_for_status()
    loaded = requests.get(f"{OLLAMA_BASE}/api/ps", timeout=60).json()["models"]
    m = next(m for m in loaded if m["name"] == model or m["model"] == model)
    return m["size_vram"] >= m["size"]


def find_num_ctx(model):
    """Largest multiple of CTX_STEP (up to the model's max) that fits on the GPU."""
    lo, hi = 1, max(1, model_max_ctx(model) // CTX_STEP)
    if not fits_on_gpu(model, lo * CTX_STEP):
        return CTX_STEP  # even the smallest size spills to RAM: just use it
    while lo < hi:  # binary search: fits at lo, unknown above
        mid = (lo + hi + 1) // 2
        if fits_on_gpu(model, mid * CTX_STEP):
            lo = mid
        else:
            hi = mid - 1
    return lo * CTX_STEP


def pick_num_ctx(model):
    """AGENT_NUM_CTX if set, else the cached value if it still fits, else search again."""
    if os.environ.get("AGENT_NUM_CTX"):
        return int(os.environ["AGENT_NUM_CTX"])
    cache = json.loads(CTX_CACHE.read_text(encoding="utf-8")) if CTX_CACHE.exists() else {}
    if model in cache and fits_on_gpu(model, cache[model]):
        return cache[model]
    print("Finding the largest context that fits on the GPU (one-time, ~1 min)...")
    cache[model] = find_num_ctx(model)
    CTX_CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return cache[model]


# ---------- agent loop ----------
def run_agent(task):
    log_file = LOG_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    log_step(log_file, event="start", model=MODEL, num_ctx=NUM_CTX, task=task)
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task}]
    for step in range(1, MAX_STEPS + 1):
        t0 = time.time()
        raw = ask_model(messages)
        latency = round(time.time() - t0, 2)
        messages.append({"role": "assistant", "content": raw})
        try:
            action = json.loads(raw)
            tool, args = action["tool"], action.get("args", {})
        except (json.JSONDecodeError, KeyError, TypeError):
            log_step(log_file, step=step, raw=raw, latency=latency, error="invalid_format")
            messages.append({"role": "user",
                             "content": "Invalid format. Reply with one JSON object: thought, tool, args."})
            continue

        print(f"\n[{step}] {action.get('thought', '')}\n    -> {tool} {json.dumps(args)[:200]}")

        if tool == "finish":
            log_step(log_file, step=step, tool=tool, args=args, latency=latency)
            print("\nDONE:", args.get("message", ""))
            return
        if tool not in TOOLS:
            result = f"Unknown tool '{tool}'. Available: {list(TOOLS)} and finish."
        else:
            try:
                result = TOOLS[tool](**args)
            except Exception as e:
                result = f"Tool error: {e}"

        result = clip(str(result))
        log_step(log_file, step=step, tool=tool, args=args, result=result, latency=latency)
        messages.append({"role": "user", "content": f"Tool result:\n{result}"})
    log_step(log_file, event="step_limit")
    print("\nStopped: reached the step limit.")


if __name__ == "__main__":
    print(f"Workspace: {WORKDIR}")
    NUM_CTX = pick_num_ctx(MODEL)
    # ~4 chars per token, so one tool result can fill at most ~1/4 of the context
    MAX_OUTPUT = NUM_CTX
    print(f"Model: {MODEL}, num_ctx: {NUM_CTX}, max tool output: {MAX_OUTPUT} chars")
    while True:
        task = input("\nTask (empty to quit): ").strip()
        if not task:
            break
        run_agent(task)