"""
Run the personal benchmark on one or more Ollama models.

    python -m bench.run qwen3.5:9b                          standard suite: every task once (~20-30 min)
    python -m bench.run qwen3.5:9b gemma4:12b --suite full  every task 3 times (~1-1.5 h per model)
    python -m bench.run qwen3.5:9b+think                    the same model with thinking mode on
    python -m bench.run qwen3.5:9b --suite quick            chat tasks only, once (~3-5 min)
    python -m bench.run qwen3.5:9b --only code,fix-bug      some categories or task ids
    python -m bench.run qwen3.5:9b --resume                 continue an interrupted run
    python -m bench.run --list                              show every task

Results are saved after every task in bench/results/*.json, and bench/RESULTS.md is rebuilt at the end.
Agent tasks run model-written Python in a temp folder WITHOUT asking: only `python <file>.py [args]`
(inside that folder) and dir/type/ls/cat are allowed.
"""
import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

import agent
from bench import report
from bench.tasks import BENCH_VERSION, CATEGORIES, CHARS_PER_TOKEN, all_tasks
from bench.tasks.core import write_tree

RESULTS_DIR = Path(__file__).parent / "results"
ARTIFACTS_DIR = RESULTS_DIR / "artifacts"
SUITES = {  # name: (repeat, skip these categories)
    "quick": (1, {"agent", "long-context", "safety"}),
    "standard": (1, set()),
    "full": (3, set()),
}
BASE_SEED = 1000
slug = report.slug


# ---------- command allowlist for agent tasks ----------
def is_allowed(command):
    """Only `python file.py [args]` and read-only listing commands, with relative paths and no shell tricks."""
    if re.search(r"[&|;<>`$%^]", command) or ".." in command:
        return False
    parts = command.split()
    if not parts:
        return False
    head, args = parts[0].lower(), parts[1:]
    if any(re.match(r"^([a-z]:|/|\\|~)", a, re.I) for a in args):  # absolute paths
        return False
    if head == "python":
        return bool(args) and args[0].endswith(".py")
    return head in ("dir", "ls", "type", "cat")


def bench_approve(command):
    ok = is_allowed(command)
    print(f"\n  [bench] {'auto-allowed' if ok else 'denied'}: {command}")
    return ok


# ---------- running tasks ----------
def run_chat(task, num_ctx, seed=None):
    messages = ([{"role": "system", "content": task.system}] if task.system else []) + task.history + \
               [{"role": "user", "content": task.prompt}]
    budget = task.max_tokens + (4096 if agent.THINK else 0)  # thinking tokens count against num_predict
    options = {"temperature": agent.TEMPERATURE, "num_ctx": num_ctx, "num_predict": budget}
    if seed is not None:
        options["seed"] = seed
    payload = {"model": agent.MODEL, "messages": messages, "think": agent.THINK, "options": options}
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


def run_agent_task(task, name, seed=None):
    old = agent.WORKDIR, agent.approve, agent.SEED
    with tempfile.TemporaryDirectory(prefix="bench-") as d:
        workdir = Path(d).resolve()
        write_tree(workdir, task.files)
        agent.WORKDIR, agent.approve, agent.SEED = workdir, bench_approve, seed
        try:
            summary = agent.run_agent(task.prompt, max_steps=task.max_steps, max_seconds=task.max_seconds)
        finally:
            agent.WORKDIR, agent.approve, agent.SEED = old
        ok, detail = task.check(workdir, summary)
        save_artifacts(task, workdir, name)
    return {"ok": ok, "detail": detail, "seconds": summary["seconds"], "steps": summary["steps"],
            "status": summary["status"], "invalid": summary["invalid"], "log": summary["log"],
            "message": summary["message"][:300]}


def save_artifacts(task, workdir, name):
    """Keep files worth looking at (the pelican!) in bench/results/artifacts/<model>/."""
    for fname in task.keep:
        src = workdir / fname
        if not src.exists():
            continue
        dest = ARTIFACTS_DIR / slug(name)
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest / fname)
        svg = re.search(r"<svg.*?</svg>", src.read_text(encoding="utf-8", errors="replace"), re.S | re.I)
        if svg:  # a standalone .svg renders as an image on GitHub
            text = svg.group(0)
            if "xmlns=" not in text:
                text = text.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            (dest / (Path(fname).stem + ".svg")).write_text(text, encoding="utf-8")


# ---------- model and machine info ----------
def installed_models():
    return {m["name"] for m in requests.get(f"{agent.OLLAMA_BASE}/api/tags", timeout=30).json()["models"]}


def gpu_info(model):
    loaded = requests.get(f"{agent.OLLAMA_BASE}/api/ps", timeout=30).json()["models"]
    m = next((m for m in loaded if m["name"] == model or m["model"] == model), None)
    if not m:
        return {}
    return {"size_gb": round(m["size"] / 2**30, 2), "gpu_percent": round(100 * m["size_vram"] / m["size"])}


def model_details(model):
    try:
        d = requests.post(f"{agent.OLLAMA_BASE}/api/show", json={"model": model}, timeout=30).json().get("details", {})
        return {"params": d.get("parameter_size"), "quant": d.get("quantization_level"), "family": d.get("family")}
    except requests.RequestException:
        return {}


def calibrate(model):
    """Generation speed (tok/s) on one fixed prompt, median of 3. Run before and after the tasks:
    if the two differ a lot, something else used the GPU and speed numbers can't be trusted."""
    speeds = []
    for _ in range(3):
        d = agent.post_chat({"model": model, "think": False,
                             "messages": [{"role": "user", "content": "Count from 1 to 150, separated by spaces."}],
                             "options": {"temperature": 0, "seed": 1, "num_ctx": agent.NUM_CTX, "num_predict": 200}})
        if d.get("eval_duration"):
            speeds.append(d["eval_count"] / (d["eval_duration"] / 1e9))
    return round(statistics.median(speeds), 1) if speeds else None


def gpu_utilization():
    """GPU use in % right now (highest of 3 samples), or None without nvidia-smi."""
    samples = []
    for _ in range(3):
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
            samples.append(int(out.splitlines()[0]))
        except (OSError, subprocess.SubprocessError, ValueError, IndexError):
            return None
        time.sleep(1)
    return max(samples)


def machine_info():
    info = {"python": sys.version.split()[0], "os": sys.platform}
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        info["gpu"] = gpu
    except (OSError, subprocess.SubprocessError):
        pass
    return info


# ---------- one model ----------
def select(tasks, only, skip):
    tasks = [t for t in tasks if t.category not in skip]
    if not only:
        return tasks
    wanted = set(only.split(","))
    return [t for t in tasks if t.category in wanted or t.id in wanted]


def find_resumable(name):
    """Latest unfinished results file for this model, if any."""
    for f in sorted(RESULTS_DIR.glob(f"*_{slug(name)}.json"), reverse=True):
        data = json.loads(f.read_text(encoding="utf-8"))
        if data["meta"]["model"] == name:
            return (f, data) if not data["meta"].get("complete", True) else (None, None)
    return None, None


def save(out, meta, results):
    out.write_text(json.dumps({"meta": meta, "results": results}, indent=1, ensure_ascii=False), encoding="utf-8")


def fmt_time(seconds):
    return f"{seconds // 3600:.0f}h{seconds % 3600 // 60:02.0f}m" if seconds >= 3600 else f"{seconds // 60:.0f}m{seconds % 60:02.0f}s"


def bench_model(name, args, repeat, skip):
    """`name` is an Ollama model, optionally with "+think" to turn thinking mode on."""
    model = name.removesuffix("+think")
    agent.MODEL, agent.THINK, agent.TEMPERATURE = model, name.endswith("+think"), args.temperature
    if args.num_ctx:
        os.environ["AGENT_NUM_CTX"] = str(args.num_ctx)
    agent.NUM_CTX = agent.pick_num_ctx(model)
    agent.MAX_OUTPUT = agent.NUM_CTX
    tasks = select(all_tasks(agent.NUM_CTX), args.only, skip)

    agent.post_chat({"model": model, "messages": [{"role": "user", "content": "hi"}],
                     "options": {"num_ctx": agent.NUM_CTX, "num_predict": 1}})  # load it, then read GPU fit
    out, previous = find_resumable(name) if args.resume else (None, None)
    results = previous["results"] if previous else []
    done = {(r["id"], r["attempt"]) for r in results}
    meta = previous["meta"] if previous else {
        "model": name, "date": datetime.now().isoformat(timespec="seconds"), "version": BENCH_VERSION,
        "suite": args.suite,
        "num_ctx": agent.NUM_CTX, "think": agent.THINK, "temperature": agent.TEMPERATURE, "repeat": repeat,
        "complete": False, **gpu_info(model), **model_details(model),
        "ollama": requests.get(f"{agent.OLLAMA_BASE}/api/version", timeout=30).json().get("version"),
        "settings": {k: os.environ.get(k) for k in ("OLLAMA_FLASH_ATTENTION", "OLLAMA_KV_CACHE_TYPE")},
        "machine": machine_info()}
    idle_gpu = gpu_utilization()  # the model is loaded but idle: anything here is another app
    if idle_gpu is not None and idle_gpu > 20:
        print(f"\n  WARNING: the GPU is {idle_gpu}% busy before starting. Close games, videos and other GPU apps,"
              " or speed and time-limited tasks will be unfair.")
    if not previous:
        meta.update(gpu_busy_at_start=idle_gpu, speed_start=calibrate(model))
    RESULTS_DIR.mkdir(exist_ok=True)
    out = out or RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}_{slug(name)}.json"

    todo = [(t, a) for a in range(1, repeat + 1) for t in tasks if (t.id, a) not in done]
    print(f"\n=== {name}: {meta.get('params')} {meta.get('quant')}, num_ctx {meta['num_ctx']:,}, "
          f"{meta.get('gpu_percent')}% GPU, {meta.get('size_gb')} GB | {len(tasks)} tasks x {repeat}"
          f"{f', resuming: {len(done)} done' if done else ''} ===")
    start = time.time()
    for i, (task, attempt) in enumerate(todo, 1):
        seed = BASE_SEED + attempt  # same seeds for every model: fair and reproducible
        try:
            r = run_chat(task, agent.NUM_CTX, seed) if task.kind == "chat" else run_agent_task(task, name, seed)
        except Exception as e:  # a crash is a failed task, not a failed benchmark
            r = {"ok": False, "detail": f"error: {e}"[:200], "seconds": 0}
        r.update(id=task.id, category=task.category, kind=task.kind, attempt=attempt)
        results.append(r)
        save(out, meta, results)  # after every task, so a crash or Ctrl+C loses nothing (--resume)
        elapsed = time.time() - start
        eta = elapsed / i * (len(todo) - i)
        print(f"  [{i:3}/{len(todo)}] {'PASS' if r['ok'] else 'FAIL'}  {task.category:12} {task.id:20} "
              f"{r['seconds']:6.1f}s  eta {fmt_time(eta):>7}  {str(r['detail'])[:50]}", flush=True)

    meta["complete"] = True
    earlier = previous["meta"].get("minutes", 0) if previous else 0  # time spent before a --resume
    meta["minutes"] = round(earlier + (time.time() - start) / 60, 1)
    meta["speed_end"] = calibrate(model)
    save(out, meta, results)
    if report.speed_unstable(meta):
        print(f"\n  WARNING: speed changed from {meta.get('speed_start')} to {meta['speed_end']} tok/s during the run."
              " Something else probably used the GPU: speed numbers are marked unreliable.")
    scores = report.category_scores(results)
    low, high = report.confidence_interval(results)
    print(f"\n  {name}: overall {report.overall(scores):.0%} (95% CI {low:.0%}-{high:.0%})  " +
          "  ".join(f"{c} {s:.0%}" for c, s in scores.items()))
    print(f"  saved: {out}")


def list_tasks():
    tasks = all_tasks(188416)
    for cat in CATEGORIES:
        group = [t for t in tasks if t.category == cat]
        print(f"\n{cat} ({len(group)})")
        for t in group:
            print(f"  {t.id:22} {t.kind:5}  {' '.join(t.prompt.split())[:70] if len(t.prompt) < 2000 else '(long prompt)'}")
    print(f"\n{len(tasks)} tasks (long-context count depends on the model's num_ctx)")


def main():
    p = argparse.ArgumentParser(description="Personal benchmark for local Ollama models")
    p.add_argument("models", nargs="*",
                   help="Ollama model names, e.g. qwen3.5:9b gemma4:12b; add +think for thinking mode")
    p.add_argument("--suite", choices=SUITES, default="standard",
                   help="quick: chat only, once | standard: everything once | full: everything 3 times")
    p.add_argument("--repeat", type=int, help="override the suite's repeat count")
    p.add_argument("--only", help="comma-separated categories or task ids")
    p.add_argument("--resume", action="store_true", help="continue the last unfinished run of each model")
    p.add_argument("--num-ctx", type=int, help="force the same num_ctx for every model (default: largest that fits)")
    p.add_argument("--temperature", type=float, default=0.2, help="sampling temperature (default 0.2)")
    p.add_argument("--list", action="store_true", help="list every task and exit")
    args = p.parse_args()
    if args.list:
        return list_tasks()
    if not args.models:
        p.error("give at least one model, e.g. python -m bench.run qwen3.5:9b")

    repeat, skip = SUITES[args.suite]
    repeat = args.repeat or repeat
    have = installed_models()
    for name in args.models:
        model, think = name.removesuffix("+think"), "+think" if name.endswith("+think") else ""
        if model not in have and f"{model}:latest" in have:
            model = f"{model}:latest"  # `ollama ps` reports the full name
        if model not in have:
            print(f"\n{model} is not installed. Run: ollama pull {model}")
            continue
        bench_model(model + think, args, repeat, skip)
    path = report.write_results_md(RESULTS_DIR)
    print(f"\nLeaderboard: {path}")


if __name__ == "__main__":
    main()
