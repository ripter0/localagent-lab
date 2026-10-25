import json

import pytest

import agent
from agent import log_step


def test_log_step_appends_one_json_line_per_call(tmp_path):
    f = tmp_path / "run.jsonl"
    log_step(f, step=1, tool="finish")
    log_step(f, step=2, tool="list_dir")
    lines = f.read_text().splitlines()
    assert [json.loads(line)["step"] for line in lines] == [1, 2]
    assert "ts" in json.loads(lines[0])


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(agent, "WORKDIR", tmp_path.resolve())
    return tmp_path


def test_replace_in_file_changes_exactly_one_occurrence(workspace):
    (workspace / "a.py").write_text("X = 1\nY = 2\n", encoding="utf-8")
    assert "replaced 1" in agent.replace_in_file("a.py", "Y = 2", "Y = 3")
    assert (workspace / "a.py").read_text(encoding="utf-8") == "X = 1\nY = 3\n"


@pytest.mark.parametrize("text, old", [("A\nA\n", "A"), ("A\n", "B"), ("A\n", "")])
def test_replace_in_file_refuses_missing_or_ambiguous_text(workspace, text, old):
    (workspace / "a.py").write_text(text, encoding="utf-8")
    assert agent.replace_in_file("a.py", old, "Z").startswith("Error")
    assert (workspace / "a.py").read_text(encoding="utf-8") == text  # untouched


def test_replace_in_file_stays_in_the_workspace(workspace):
    with pytest.raises(ValueError):
        agent.replace_in_file("../outside.py", "a", "b")


def test_call_tool_ignores_unknown_args(workspace):
    # the exact mistake seen in the benchmark: a stray "tool" key inside args
    out = agent.call_tool("write_file", {"path": "t.py", "content": "print(1)", "tool": "write_file"})
    assert "ignored unknown args: tool" in out and "wrote 8 characters" in out
    assert (workspace / "t.py").read_text(encoding="utf-8") == "print(1)"


def test_call_tool_rejects_non_object_args(workspace):
    assert agent.call_tool("list_dir", ["."]).startswith("Tool error")


def test_system_prompt_has_the_new_tool_and_rules():
    p = agent.SYSTEM_PROMPT
    assert "replace_in_file" in p
    assert "secrets" in p and "destructive" in p
    assert "docstring" in p
