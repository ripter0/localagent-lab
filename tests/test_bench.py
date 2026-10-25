import json

import agent
from bench import report, tasks
from bench.run import is_allowed


def task(task_id):
    return next(t for t in tasks.CHAT_TASKS + tasks.AGENT_TASKS if t.id == task_id)


# ---------- chat checks: one right and one wrong answer each ----------
def test_tool_check():
    check = task("json-read").check
    assert check('{"thought": "x", "tool": "read_file", "args": {"path": "main.py"}}')[0]
    assert not check('{"thought": "x", "tool": "list_dir", "args": {"path": "."}}')[0]
    assert not check("I will read main.py")[0]


def test_number_check_accepts_json_and_text():
    check = task("discount-tax").check
    assert check('{"answer": 33}')[0]
    assert check('{"answer": "33.00 euros"}')[0]
    assert not check('{"answer": 30}')[0]


def test_instruction_checks():
    assert task("three-words").check("waves crash softly")[0]
    assert not task("three-words").check("The waves crash.")[0]
    assert task("yes-no").check("YES")[0]
    assert not task("yes-no").check("Yes, 17 is prime.")[0]
    assert task("no-letter-e").check("A big busy town with many old roads.")[0]
    assert not task("no-letter-e").check("Milan is a beautiful city.")[0]


def test_code_check_runs_hidden_tests():
    check = task("palindrome").check
    good = "```python\ndef is_palindrome(s):\n    t = [c.lower() for c in s if c.isalnum()]\n    return t == t[::-1]\n```"
    bad = "```python\ndef is_palindrome(s):\n    return s == s[::-1]\n```"
    assert check(good)[0]
    assert not check(bad)[0]


def test_italian_checks():
    assert task("it-to-en").check("The cat sleeps on the sofa.")[0]
    assert task("en-to-it").check("Il cane sta mangiando in cucina.")[0]
    assert task("it-fact").check("Po")[0]
    assert not task("it-fact").check("Il Tevere")[0]


def test_needle_tasks_scale_with_context():
    small = tasks.needle_tasks(8192)
    big = tasks.needle_tasks(188416)
    assert [t.id for t in small] == ["needle-4k", "needle-6k"]  # 4k, then 75% of 8k
    assert [t.id for t in big] == ["needle-4k", "needle-16k", "needle-64k", "needle-141k"]
    t = big[0]
    code = next(w for w in t.prompt.split() if w.rstrip(".").isdigit() and len(w.rstrip(".")) == 4)
    assert t.check(json.dumps({"code": code}))[0]
    assert not t.check('{"code": "0000"}')[0]


def test_haystack_contains_needle_at_depth():
    text = tasks.haystack(2000, "NEEDLE", 0.5)
    lines = text.splitlines()
    assert 0.4 < lines.index("NEEDLE") / len(lines) < 0.6
    assert 5000 < len(text) < 6500  # ~2.8 chars per token


# ---------- agent checks: reference solutions pass, untouched files fail ----------
def setup(tmp_path, files):
    for name, content in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(content, encoding="utf-8")
    return tmp_path


def test_bugfix_check(tmp_path):
    t = task("fix-bug")
    setup(tmp_path, t.files)
    assert not t.check(tmp_path, {})[0]  # still buggy
    (tmp_path / "stats.py").write_text("def average(n):\n    return sum(n) / len(n)\n\n"
                                       "def maximum(n):\n    return max(n)\n", encoding="utf-8")
    assert t.check(tmp_path, {})[0]
    (tmp_path / "check_stats.py").write_text("print('ALL OK')\n", encoding="utf-8")
    assert not t.check(tmp_path, {})[0]  # editing the check file is cheating


def test_multi_file_check(tmp_path):
    t = task("multi-file")
    setup(tmp_path, t.files)
    assert not t.check(tmp_path, {})[0]
    setup(tmp_path, {"mathlib.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n",
                     "main.py": "from mathlib import multiply\nprint(multiply(6, 7))\n"})
    assert t.check(tmp_path, {})[0]


def test_honesty_check(tmp_path):
    check = task("honesty").check
    assert check(tmp_path, {"status": "finish", "message": "secret.txt does not exist in the workspace."})[0]
    assert not check(tmp_path, {"status": "finish", "message": "It says: the password is 1234."})[0]


def test_pelican_check(tmp_path):
    check = task("pelican").check
    assert not check(tmp_path, {})[0]
    svg = "<svg>" + "<circle/>" * 3 + "<path/><rect/></svg>"
    (tmp_path / "pelican.html").write_text(f"<html>{svg}</html>", encoding="utf-8")
    assert check(tmp_path, {})[0]


# ---------- the command allowlist ----------
def test_allowlist():
    assert is_allowed("python hello.py")
    assert is_allowed("python sub/main.py")
    assert is_allowed("dir")
    assert not is_allowed("python -c \"import os\"")
    assert not is_allowed("python ../evil.py")
    assert not is_allowed("python C:\\Windows\\x.py")
    assert not is_allowed("del hello.py")
    assert not is_allowed("python hello.py && del *")
    assert not is_allowed("type secret.txt > out.txt")


# ---------- agent loop limits ----------
def test_agent_stops_after_repeated_bad_replies(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model", lambda messages: "not json")
    summary = agent.run_agent("anything")
    assert summary["status"] == "bad_format"
    assert summary["steps"] == agent.MAX_INVALID


def test_agent_returns_finish_message(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model",
                        lambda m: '{"thought": "done", "tool": "finish", "args": {"message": "all good"}}')
    summary = agent.run_agent("anything")
    assert summary["status"] == "finish" and summary["message"] == "all good" and summary["steps"] == 1


# ---------- report ----------
def fake_run(model, oks):
    results = [{"id": f"t{i}", "category": cat, "ok": ok, "seconds": 1.0}
               for i, (cat, ok) in enumerate(oks)]
    return {"meta": {"model": model, "date": "2026-10-25T12:00:00", "num_ctx": 8192}, "results": results,
            "file": f"{model}.json"}


def test_scores_weigh_categories_equally():
    results = fake_run("m", [("code", True), ("code", True), ("code", True), ("reasoning", False)])["results"]
    scores = report.category_scores(results)
    assert scores == {"reasoning": 0.0, "code": 1.0}
    assert report.overall(scores) == 0.5


def test_partial_rerun_replaces_only_its_tasks():
    full = fake_run("m", [("code", False), ("reasoning", False)])  # ids t0 (code), t1 (reasoning)
    rerun = fake_run("m", [("code", True)])  # id t0 again
    merged = report.latest_per_model([full, rerun])["m"]["results"]
    assert sorted((r["id"], r["ok"]) for r in merged) == [("t0", True), ("t1", False)]


def test_truncated_prompt_counts_as_failure(monkeypatch):
    from bench import run
    t = tasks.needle_tasks(8192)[0]
    code = t.check.__defaults__[0]
    monkeypatch.setattr(agent, "post_chat", lambda p: {"message": {"content": f'{{"code": "{code}"}}'},
                                                        "prompt_eval_count": 100})
    r = run.run_chat(t, 8192)
    assert not r["ok"] and "truncated" in r["detail"]


def test_markdown_ranks_models(tmp_path):
    runs = [fake_run("weak", [("code", False)]), fake_run("strong", [("code", True)])]
    md = report.build_markdown(runs, tmp_path)
    assert md.index("`strong`") < md.index("`weak`")
    assert "xychart-beta" in md
