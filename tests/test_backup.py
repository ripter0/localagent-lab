import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import backup  # noqa: E402

RULES = [(re.compile(re.escape("C:\\\\Users\\\\Anna"), re.I), "<HOME>"),
         (re.compile(re.escape("C:\\Users\\Anna"), re.I), "<HOME>"),
         (re.compile(r"\bAnna\b", re.I), "<me>")]


def test_redact_plain_json_and_name():
    text = 'path C:\\Users\\Anna\\x and {"p": "C:\\\\Users\\\\Anna\\\\y"} by anna@example.com'
    out = backup.redact(text, RULES)
    assert "Anna" not in out and "anna" not in out
    assert out.count("<HOME>") == 2 and "<me>@example.com" in out


def test_secrets_and_git_are_skipped():
    assert backup.skipped(Path(".env"))
    assert backup.skipped(Path("app/.env.local"))
    assert backup.skipped(Path(".git/config"))
    assert backup.skipped(Path("pkg/__pycache__/x.pyc"))
    assert not backup.skipped(Path(".env.example"))
    assert not backup.skipped(Path("templates/index.html"))


def test_copy_tree_redacts_text_and_keeps_binary(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    (src / ".git").mkdir(parents=True)
    (src / ".git" / "HEAD").write_text("ref")
    (src / ".env").write_text("SECRET_KEY=abc")
    (src / "notes.txt").write_text("hello Anna", encoding="utf-8")
    (src / "db.sqlite").write_bytes(b"\x00\xff\x10binary")
    copied, left_out = backup.copy_tree(src, dest, RULES)
    assert (copied, left_out) == (2, 2)
    assert (dest / "notes.txt").read_text(encoding="utf-8") == "hello <me>"
    assert (dest / "db.sqlite").read_bytes() == b"\x00\xff\x10binary"
    assert not (dest / ".env").exists() and not (dest / ".git").exists()
