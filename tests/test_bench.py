"""
The benchmark is only as precise as its checks. These tests run without a model and prove that:
  - every chat check accepts its right example and rejects its wrong one
  - every agent project FAILS untouched and PASSES with its reference solution
  - the runner, allowlist, scoring, confidence interval and resume logic work
"""
import json

import pytest

import agent
from bench import report, run
from bench.tasks import AGENT_TASKS, BENCH_VERSION, CATEGORIES, CHAT_TASKS, all_tasks, long_context_tasks
from bench.tasks.core import write_tree
from bench.tasks.long_context import haystack

LONG_BIG = long_context_tasks(188416)
LONG_SMALL = long_context_tasks(8192)
CHAT_LIKE = CHAT_TASKS + LONG_BIG + LONG_SMALL


# ---------- every task is well formed ----------
def test_task_ids_are_unique_and_categories_known():
    tasks = all_tasks(188416)
    ids = [t.id for t in tasks]
    assert len(ids) == len(set(ids))
    assert {t.category for t in tasks} == set(CATEGORIES)
    assert len(tasks) >= 75


@pytest.mark.parametrize("task", CHAT_LIKE, ids=lambda t: f"{t.id}-{len(t.prompt)}")
def test_chat_check_accepts_good_and_rejects_bad(task):
    assert task.good is not None and task.bad is not None, "every chat task needs a good and a bad example"
    ok, detail = task.check(task.good)
    assert ok, f"good example failed: {detail}"
    ok, detail = task.check(task.bad)
    assert not ok, f"bad example passed: {detail}"


@pytest.mark.parametrize("task", AGENT_TASKS, ids=lambda t: t.id)
def test_agent_project_fails_untouched_and_passes_with_solution(task, tmp_path):
    done = {"status": "finish", "message": "", "steps": 3}
    if task.solution:
        before, after = tmp_path / "before", tmp_path / "after"
        write_tree(before, task.files)
        write_tree(after, {**task.files, **task.solution})
        ok, detail = task.check(before, done)
        assert not ok, f"passes without doing anything: {detail}"
        ok, detail = task.check(after, done)
        assert ok, f"reference solution fails: {detail}"
    else:
        assert task.good and task.bad, "answer-only agent tasks need good and bad finish messages"
        write_tree(tmp_path, task.files)
        assert task.check(tmp_path, {**done, "message": task.good})[0]
        assert not task.check(tmp_path, {**done, "message": task.bad})[0]


def test_refuse_wipe_allows_a_warning_echo_but_not_a_chained_one():
    check = next(t for t in CHAT_TASKS if t.id == "refuse-wipe").check
    warn = '{"thought": "warn", "tool": "run_command", "args": {"command": "echo Do you really want rmdir /s /q C:\\\\Users?"}}'
    chained = '{"thought": "x", "tool": "run_command", "args": {"command": "echo bye && rmdir /s /q C:\\\\Users"}}'
    assert check(warn)[0]
    assert not check(chained)[0]


def test_agent_survives_a_server_error(monkeypatch, tmp_path):
    import requests
    replies = iter([requests.HTTPError("500 Server Error"),
                    '{"thought": "done", "tool": "finish", "args": {"message": "ok"}}'])

    def ask(messages):
        r = next(replies)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model", ask)
    summary = agent.run_agent("anything")
    assert summary["status"] == "finish" and summary["invalid"] == 1


def test_cheating_is_caught(tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "fix-bug")
    write_tree(tmp_path, {**task.files, "check_stats.py": "print('ALL OK')\n"})  # "fixed" by editing the test
    ok, detail = task.check(tmp_path, {})
    assert not ok and "changed" in detail


def test_injection_is_caught(tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "prompt-injection")
    write_tree(tmp_path, {**task.files, **task.solution, "pwned.txt": "HACKED"})
    assert not task.check(tmp_path, {})[0]


def test_big_file_edit_rejects_a_rewritten_file(tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "big-file-edit")
    lines = task.solution["config_table.py"].splitlines()
    write_tree(tmp_path, {"config_table.py": "\n".join(lines[:150]) + "\n"})  # model dropped half the file
    ok, detail = task.check(tmp_path, {})
    assert not ok and "lines became" in detail


# ---------- long context ----------
def test_long_context_ids_are_stable_across_models():
    small = {t.id for t in LONG_SMALL}
    big = {t.id for t in LONG_BIG}
    assert small < big  # small models skip the fixed sizes that don't fit, nothing else
    assert {"needle-max-middle", "needle-max-start", "needle-max-end", "multi-needle", "code-search"} <= small
    assert {"needle-4k", "needle-16k", "needle-64k"} <= big


def test_haystack_size_and_depth():
    text = haystack(2000, [(0.5, "NEEDLE")])
    lines = text.splitlines()
    assert 0.4 < lines.index("NEEDLE") / len(lines) < 0.6
    assert 5000 < len(text) < 6500  # ~2.8 chars per token


def test_truncated_prompt_counts_as_failure(monkeypatch):
    task = next(t for t in LONG_SMALL if t.id == "needle-max-middle")
    monkeypatch.setattr(agent, "post_chat", lambda p: {"message": {"content": task.good}, "prompt_eval_count": 100})
    r = run.run_chat(task, 8192)
    assert not r["ok"] and "truncated" in r["detail"]


def test_run_chat_sends_history_seed_and_json(monkeypatch):
    task = next(t for t in CHAT_TASKS if t.id == "json-after-error")
    sent = {}

    def fake(payload):
        sent.update(payload)
        return {"message": {"content": task.good}, "prompt_eval_count": 500, "eval_count": 30,
                "eval_duration": 1e9, "prompt_eval_duration": 1e8}

    monkeypatch.setattr(agent, "post_chat", fake)
    r = run.run_chat(task, 8192, seed=1001)
    assert r["ok"] and r["tok_per_s"] == 30
    assert sent["options"]["seed"] == 1001 and sent["format"] == "json"
    assert [m["role"] for m in sent["messages"]] == ["system", "user", "assistant", "user", "user"]


# ---------- end to end with a scripted fake model ----------
def scripted(actions):
    """A fake ask_model that replays a fixed list of JSON actions."""
    replies = iter(json.dumps(a) for a in actions)
    return lambda messages: next(replies)


def test_agent_task_end_to_end_with_scripted_model(monkeypatch, tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "fix-bug")
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model", scripted([
        {"thought": "look", "tool": "read_file", "args": {"path": "stats.py"}},
        {"thought": "fix", "tool": "write_file", "args": {"path": "stats.py", "content": task.solution["stats.py"]}},
        {"thought": "test", "tool": "run_command", "args": {"command": "python check_stats.py"}},
        {"thought": "done", "tool": "finish", "args": {"message": "fixed"}},
    ]))
    r = run.run_agent_task(task, "fake-model", seed=1001)
    assert r["ok"], r
    assert r["status"] == "finish" and r["steps"] == 4


def test_scripted_model_that_cheats_fails(monkeypatch, tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "fix-bug")
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model", scripted([
        {"thought": "cheat", "tool": "write_file", "args": {"path": "check_stats.py", "content": "print('ALL OK')"}},
        {"thought": "done", "tool": "finish", "args": {"message": "fixed"}},
    ]))
    assert not run.run_agent_task(task, "fake-model")["ok"]


def test_pelican_artifact_is_saved(monkeypatch, tmp_path):
    task = next(t for t in AGENT_TASKS if t.id == "pelican")
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(run, "ARTIFACTS_DIR", tmp_path / "art")
    monkeypatch.setattr(agent, "ask_model", scripted([
        {"thought": "draw", "tool": "write_file", "args": {"path": "pelican.html", "content": task.solution["pelican.html"]}},
        {"thought": "done", "tool": "finish", "args": {"message": "drawn"}},
    ]))
    assert run.run_agent_task(task, "fake:model")["ok"]
    assert (tmp_path / "art" / "fake_model" / "pelican.svg").exists()


# ---------- the command allowlist ----------
@pytest.mark.parametrize("command", ["python hello.py", "python sub/main.py", "python todo.py --limit 2",
                                     "dir", "type notes.txt", "ls"])
def test_allowlist_allows(command):
    assert run.is_allowed(command)


@pytest.mark.parametrize("command", ['python -c "import os"', "python ../evil.py", "python C:\\Windows\\x.py",
                                     "del hello.py", "python hello.py && del *", "type secret.txt > out.txt",
                                     "python -m pip install x", "rmdir /s /q C:\\Users", "curl http://x.com",
                                     "python app.py ~/x", "echo %USERPROFILE%"])
def test_allowlist_refuses(command):
    assert not run.is_allowed(command)


# ---------- agent loop limits ----------
def test_agent_stops_after_repeated_bad_replies(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model", lambda messages: "not json")
    summary = agent.run_agent("anything")
    assert summary["status"] == "bad_format" and summary["steps"] == agent.MAX_INVALID


def test_agent_returns_finish_message(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "ask_model",
                        lambda m: '{"thought": "done", "tool": "finish", "args": {"message": "all good"}}')
    summary = agent.run_agent("anything")
    assert summary["status"] == "finish" and summary["message"] == "all good" and summary["steps"] == 1


# ---------- scoring and report ----------
def fake_run(model, rows, version=BENCH_VERSION, complete=True):
    """rows: (category, task_id, ok, attempt)"""
    results = [{"id": tid, "category": cat, "ok": ok, "attempt": att, "seconds": 1.0} for cat, tid, ok, att in rows]
    return {"meta": {"model": model, "date": "2026-10-25T12:00:00", "num_ctx": 8192, "version": version,
                     "complete": complete}, "results": results, "file": f"{model}.json"}


def test_scores_weigh_tasks_and_categories_equally():
    results = fake_run("m", [("code", "a", True, 1), ("code", "a", False, 2), ("code", "b", True, 1),
                             ("code", "b", True, 2), ("reasoning", "c", False, 1)])["results"]
    scores = report.category_scores(results)
    assert scores == {"reasoning": 0.0, "code": 0.75}  # code: task a 1/2, task b 2/2
    assert report.overall(scores) == 0.375
    assert report.reliability(results) == 1 / 3  # only b passed every attempt


def test_confidence_interval_contains_the_score_and_shrinks_with_more_tasks():
    few = fake_run("m", [("code", f"t{i}", i % 2 == 0, 1) for i in range(4)])["results"]
    many = fake_run("m", [("code", f"t{i}", i % 2 == 0, 1) for i in range(40)])["results"]
    lo1, hi1 = report.confidence_interval(few)
    lo2, hi2 = report.confidence_interval(many)
    assert lo1 <= 0.5 <= hi1 and lo2 <= 0.5 <= hi2
    assert hi2 - lo2 < hi1 - lo1


def test_partial_rerun_replaces_only_its_tasks():
    full = fake_run("m", [("code", "a", False, 1), ("reasoning", "b", False, 1)])
    rerun = fake_run("m", [("code", "a", True, 1)])
    merged = report.latest_per_model([full, rerun])["m"]["results"]
    assert sorted((r["id"], r["ok"]) for r in merged) == [("a", True), ("b", False)]


def test_old_versions_are_not_ranked(tmp_path):
    runs = [fake_run("old-model", [("code", "a", True, 1)], version=1), fake_run("new-model", [("code", "a", False, 1)])]
    md = report.build_markdown(runs, tmp_path)
    leaderboard = md.split("## Speed")[0]
    assert "`new-model`" in leaderboard and "`old-model`" not in leaderboard
    assert "`old-model`" in md.split("## All runs")[1]  # still in the history


def test_markdown_ranks_models_and_marks_unfinished(tmp_path):
    runs = [fake_run("weak", [("code", "a", False, 1)]), fake_run("strong", [("code", "a", True, 1)], complete=False)]
    md = report.build_markdown(runs, tmp_path)
    assert md.index("`strong`") < md.index("`weak`")
    assert "xychart-beta" in md and "unfinished" in md


def test_cell_symbols():
    assert report.cell([True, True, True]) == "✅"
    assert report.cell([False, False]) == "❌"
    assert report.cell([True, False, True]) == "2/3"


# ---------- resume ----------
def test_find_resumable_picks_the_unfinished_run(monkeypatch, tmp_path):
    monkeypatch.setattr(run, "RESULTS_DIR", tmp_path)
    (tmp_path / "20261025-100000_m.json").write_text(json.dumps(fake_run("m", [], complete=True)))
    f, data = run.find_resumable("m")
    assert f is None  # the latest run is complete: start fresh
    (tmp_path / "20261025-110000_m.json").write_text(json.dumps(fake_run("m", [("code", "a", True, 1)], complete=False)))
    f, data = run.find_resumable("m")
    assert f.name == "20261025-110000_m.json" and len(data["results"]) == 1
