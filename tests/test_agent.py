import json
from agent import log_step


def test_log_step_appends_one_json_line_per_call(tmp_path):
    f = tmp_path / "run.jsonl"
    log_step(f, step=1, tool="finish")
    log_step(f, step=2, tool="list_dir")
    lines = f.read_text().splitlines()
    assert [json.loads(line)["step"] for line in lines] == [1, 2]
    assert "ts" in json.loads(lines[0])