"""
Run the personal benchmark on one or more Ollama models.

    python -m bench.run qwen3.5:9b
    python -m bench.run qwen3.5:9b gemma4:12b --repeat 3
    python -m bench.run qwen3.5:9b --only code,reasoning     (categories or task ids)
    python -m bench.run qwen3.5:9b --quick                   (skip agent and long-context)

Results go to bench/results/*.json and bench/RESULTS.md is rebuilt.
Agent tasks run model-written Python in a temp folder WITHOUT asking:
only `python <file>.py` (inside that folder) and dir/type/ls/cat are allowed.
"""
import argparse
import json
import os
import re
import shutil
import statistics
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

import agent
from bench import report
from bench.tasks import AGENT_TASKS, CHARS_PER_TOKEN, CHAT_TASKS, needle_tasks

RESULTS_DIR = Path(__file__).parent / "results"
ARTIFACTS_DIR = RESULTS_DIR / "artifacts"
AGENT_MAX_STEPS = 15
AGENT_MAX_SECONDS = 240
slug = report.slug


# ---------- command allowlist for agent tasks ----------
def is_allowed(command):
    """Only `python file.py` and read-only listing commands, with relative paths and no shell tricks."""
    if re.search(r"[&|;<>`$%^]", command) or ".." in command:
        return False
    parts = command.split()
    if not parts:
        return False
    head, args = parts[0].lower(), parts[1:]
    if any(re.match(r"^([a-z]:|/|\\)", a, re.I) for a in args):  # absolute paths
        return False
    if head == "python":
        return len(args) == 1 and args[0].endswith(".py")
    return head in ("dir", "ls", "type", "cat")


def bench_approve(command):
    ok = is_allowed(command)
    print(f"\n  [bench] {'auto-allowed' if ok else 'denied'}: {command}")
    return ok


# ---------- running tasks ----------
def run_chat(task, num_ctx):
    messages = ([{"role": "system", "content": task.system}] if task.system else []) + \
               [{"role": "user", "content": task.prompt}]
    # thinking tokens count against num_predict, so give them room
    budget = task.max_tokens + (4096 if agent.THINK else 0)
    payload = {"model": agent.MODEL, "messages": messages, "think": agent.THINK,
               "options": {"temperature": 0.2, "num_ctx": num_ctx, "num_predict": budget}}
    if task.json_mode:
        payload["format"] = "json"
    t0 = time.time()
    data = agent.post_chat(payload)
    seconds = time.time() - t0
    reply = data["message"]["content"]
    ok, detail = task.check(reply)
    expected = len(task.prompt) / CHARS_PER_TOKEN
    if expected > 2000 and data.get("prompt_eval_count", 0) < 0.6 * expected:  # Ollama cut it to fit num_ctx
        ok, detail = False, f"prompt truncated by Ollama: {data.get('prompt_eval_count')} of ~{expected:.0f} tokens"
    gen_s = data.get("eval_duration", 0) / 1e9
    read_s = data.get("prompt_eval_duration", 0) / 1e9
    return {"ok": ok, "detail": detail, "seconds": round(seconds, 2), "reply": reply[:500],
            "tokens_out": data.get("eval_count", 0),
            "tok_per_s": round(data.get("eval_count", 0) / gen_s, 1) if gen_s else None,
            "prompt_tokens": data.get("prompt_eval_count", 0),
            "prompt_tok_per_s": round(data.get("prompt_eval_count", 0) / read_s, 1) if read_s else None}


def run_agent_task(task, model):
    old_workdir, old_approve = agent.WORKDIR, agent.approve
    with tempfile.TemporaryDirectory(prefix="bench-") as d:
        workdir = Path(d).resolve()
        for name, content in task.files.items():
            (workdir / name).parent.mkdir(parents=True, exist_ok=True)
            (workdir / name).write_text(content, encoding="utf-8")
        agent.WORKDIR, agent.approve = workdir, bench_approve
        try:
            summary = agent.run_agent(task.prompt, max_steps=AGENT_MAX_STEPS, max_seconds=AGENT_MAX_SECONDS)
        finally:
            agent.WORKDIR, agent.approve = old_workdir, old_approve
        ok, detail = task.check(workdir, summary)
        save_artifacts(task, workdir, model)
    return {"ok": ok, "detail": detail, "seconds": summary["seconds"], "steps": summary["steps"],
            "status": summary["status"], "invalid": summary["invalid"], "log": summary["log"]}


def save_artifacts(task, workdir, model):
    """Keep files worth looking at (the pelican!) in bench/results/artifacts/<model>/."""
    for name in task.keep:
        src = workdir / name
        if not src.exists():
            continue
        dest = ARTIFACTS_DIR / slug(model)
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest / name)
        svg = re.search(r"<svg.*?</svg>", src.read_text(encoding="utf-8", errors="replace"), re.S | re.I)
        if svg:  # a standalone .svg renders as an image on GitHub
            text = svg.group(0)
            if "xmlns=" not in text:
                text = text.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            (dest / (Path(name).stem + ".svg")).write_text(text, encoding="utf-8")


# ---------- model info ----------
def installed_models():
    return {m["name"] for m in requests.get(f"{agent.OLLAMA_BASE}/api/tags", timeout=30).json()["models"]}


def gpu_info(model):
    loaded = requests.get(f"{agent.OLLAMA_BASE}/api/ps", timeout=30).json()["models"]
    m = next((m for m in loaded if m["name"] == model or m["model"] == model), None)
    if not m:
        return {}
    return {"size_gb": round(m["size"] / 2**30, 2), "gpu_percent": round(100 * m["size_vram"] / m["size"])}


def select(tasks, only):
    if not only:
        return tasks
    wanted = set(only.split(","))
    return [t for t in tasks if t.category in wanted or t.id in wanted]


def bench_model(name, args):
    """`name` is an Ollama model, optionally with "+think" to turn thinking mode on."""
    model = name.removesuffix("+think")
    agent.MODEL, agent.THINK = model, name.endswith("+think")
    agent.NUM_CTX = agent.pick_num_ctx(model)
    agent.MAX_OUTPUT = agent.NUM_CTX
    tasks = CHAT_TASKS + needle_tasks(agent.NUM_CTX) + AGENT_TASKS
    if args.quick:
        tasks = [t for t in tasks if t.category not in ("agent", "long-context")]
    tasks = select(tasks, args.only)

    agent.post_chat({"model": model, "messages": [{"role": "user", "content": "hi"}],
                     "options": {"num_ctx": agent.NUM_CTX, "num_predict": 1}})  # load it, then read GPU fit
    meta = {"model": name, "date": datetime.now().isoformat(timespec="seconds"), "num_ctx": agent.NUM_CTX,
            "think": agent.THINK, "repeat": args.repeat, **gpu_info(model),
            "ollama": requests.get(f"{agent.OLLAMA_BASE}/api/version", timeout=30).json().get("version"),
            "settings": {k: os.environ.get(k) for k in ("OLLAMA_FLASH_ATTENTION", "OLLAMA_KV_CACHE_TYPE")}}
    print(f"\n=== {name}: num_ctx {meta['num_ctx']}, {meta.get('gpu_percent')}% GPU, "
          f"{meta.get('size_gb')} GB, {len(tasks)} tasks x {args.repeat} ===")

    results = []
    for task in tasks:
        for attempt in range(args.repeat):
            try:
                r = run_chat(task, agent.NUM_CTX) if task.kind == "chat" else run_agent_task(task, name)
            except Exception as e:  # a crash is a failed task, not a failed benchmark
                r = {"ok": False, "detail": f"error: {e}"[:200], "seconds": 0}
            r.update(id=task.id, category=task.category, kind=task.kind, attempt=attempt + 1)
            results.append(r)
            print(f"  {'PASS' if r['ok'] else 'FAIL'}  {task.category:13} {task.id:15} "
                  f"{r['seconds']:7.1f}s  {str(r['detail'])[:60]}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}_{slug(name)}.json"
    out.write_text(json.dumps({"meta": meta, "results": results}, indent=1, ensure_ascii=False), encoding="utf-8")
    scores = report.category_scores(results)
    print(f"\n  {name}: overall {report.overall(scores):.0%}  " +
          "  ".join(f"{c} {s:.0%}" for c, s in scores.items()))
    speeds = [r["tok_per_s"] for r in results if r.get("tok_per_s") and r.get("tokens_out", 0) >= 20]
    if speeds:
        print(f"  speed: {statistics.median(speeds):.0f} tokens/s")
    print(f"  saved: {out}")


def main():
    p = argparse.ArgumentParser(description="Personal benchmark for local Ollama models")
    p.add_argument("models", nargs="+",
                   help="Ollama model names, e.g. qwen3.5:9b gemma4:12b; add +think for thinking mode")
    p.add_argument("--repeat", type=int, default=1, help="run each task N times (models are random)")
    p.add_argument("--only", help="comma-separated categories or task ids")
    p.add_argument("--quick", action="store_true", help="skip agent and long-context tasks")
    args = p.parse_args()

    have = installed_models()
    for name in args.models:
        model, think = name.removesuffix("+think"), "+think" if name.endswith("+think") else ""
        if model not in have and f"{model}:latest" in have:
            model = f"{model}:latest"  # `ollama ps` reports the full name
        if model not in have:
            print(f"\n{model} is not installed. Run: ollama pull {model}")
            continue
        bench_model(model + think, args)
    path = report.write_results_md(RESULTS_DIR)
    print(f"\nLeaderboard: {path}")


if __name__ == "__main__":
    main()
