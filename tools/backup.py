"""
Back up everything that lives outside git into archive/, so it can be committed.

    python tools/backup.py

Copies (and overwrites the previous snapshot):
  workspace/                      -> archive/workspace/   the agent's sandbox (what it built)
  logs/                           -> archive/logs/        every run log + the num_ctx cache
  custom Ollama models            -> setup/ollama/*.Modelfile
  ~/.config/opencode/             -> setup/opencode/

The repo is public, so on the way it:
  - skips .env files (secrets), .git folders (a repo can't contain a repo) and __pycache__
  - replaces your home folder and user name with <HOME> / <me> in every text file
"""
import getpass
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
SKIP_FILES = re.compile(r"^\.env(\..+)?$")  # .env, .env.local ... but .env.example is kept below
KEEP_FILES = {".env.example"}


def redactions():
    """(pattern, replacement) pairs for the home folder and the user name, in plain and JSON-escaped form."""
    home, user = str(Path.home()), getpass.getuser()
    pairs = []
    for h in {home, home.replace("\\", "/")}:
        pairs.append((re.escape(h.replace("\\", "\\\\")), "<HOME>"))  # as it appears inside JSON strings
        pairs.append((re.escape(h), "<HOME>"))
    pairs.append((rf"\b{re.escape(user)}\b", "<me>"))
    return [(re.compile(p, re.I), r) for p, r in pairs]


def redact(text, rules):
    for pattern, replacement in rules:
        text = pattern.sub(replacement, text)
    return text


def skipped(path):
    return (any(part in SKIP_DIRS for part in path.parts)
            or (SKIP_FILES.match(path.name) and path.name not in KEEP_FILES))


def copy_tree(src, dest, rules):
    """Copy src to dest (replacing dest), redacting text files. Returns (copied, skipped) counts."""
    if dest.exists():
        shutil.rmtree(dest)
    copied = left_out = 0
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        if not p.is_file():
            continue
        if skipped(rel):
            left_out += 1
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = p.read_bytes()
        try:
            target.write_text(redact(data.decode("utf-8"), rules), encoding="utf-8")
        except UnicodeDecodeError:  # binary (images, databases): copy as is
            target.write_bytes(data)
        copied += 1
    return copied, left_out


def export_modelfiles(dest, rules):
    """Custom Ollama models (not from the library) as small Modelfiles, rebuilt with `ollama create`."""
    try:
        listing = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    names = [line.split()[0] for line in listing.splitlines()[1:] if line.strip()]
    blobs = {}  # weight blob -> a library model name that uses it
    for name in names:
        mf = subprocess.run(["ollama", "show", name, "--modelfile"], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"^FROM (.+)$", mf, re.M)
        blobs.setdefault(m.group(1).strip() if m else "", []).append((name, mf))
    exported = []
    dest.mkdir(parents=True, exist_ok=True)
    for blob, models in blobs.items():
        library = [n for n, _ in models if ":" in n and not n.endswith(":latest")]
        base = library[0] if library else None
        for name, mf in models:
            if name == base or not base:
                continue  # library models are re-downloaded with `ollama pull`
            # TEMPLATE/RENDERER/PARSER are left out on purpose: they come from the base model, and copying
            # the placeholder template Ollama prints would break the chat format
            params = [l for l in mf.splitlines() if re.match(r"^(PARAMETER|SYSTEM|ADAPTER|MESSAGE)\b", l)]
            text = (f"# Rebuild with: ollama create {name.removesuffix(':latest')} -f {name.removesuffix(':latest')}"
                    f".Modelfile\n# Same weights as {base} (ollama pull {base} first)\nFROM {base}\n\n"
                    + "\n".join(params) + "\n")
            (dest / f"{name.removesuffix(':latest')}.Modelfile").write_text(redact(text, rules), encoding="utf-8")
            exported.append(name)
    return exported


def main():
    rules = redactions()
    archive = ROOT / "archive"
    for name in ("workspace", "logs"):
        src = ROOT / name
        if src.exists():
            copied, left_out = copy_tree(src, archive / name, rules)
            print(f"{name}/: {copied} files copied, {left_out} left out (.env, .git, caches)")
    models = export_modelfiles(ROOT / "setup" / "ollama", rules)
    print(f"Ollama: {len(models)} custom model(s) exported: {', '.join(models) or 'none'}")
    opencode = Path.home() / ".config" / "opencode"
    for fname in ("opencode.jsonc", "AGENTS.md"):
        if (opencode / fname).exists():
            (ROOT / "setup" / "opencode").mkdir(parents=True, exist_ok=True)
            (ROOT / "setup" / "opencode" / fname).write_text(
                redact((opencode / fname).read_text(encoding="utf-8"), rules), encoding="utf-8")
    print("OpenCode config copied to setup/opencode/")
    (archive / "BACKUP.json").write_text(json.dumps(
        {"made_by": "python tools/backup.py", "sources": ["workspace/", "logs/", "ollama list", "~/.config/opencode"]},
        indent=2), encoding="utf-8")
    print("Done. Now: git add -A && git commit -m \"backup\" && git push")


if __name__ == "__main__":
    main()
