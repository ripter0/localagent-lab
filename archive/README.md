# Archive

Snapshots of things that live outside git, so nothing is lost. **Made by `python tools/backup.py`.** Run it again any time, then commit.

| Folder | What it is | Source |
|---|---|---|
| [`workspace/`](workspace) | Everything the agent built in its sandbox: the CleanSignal hackathon app, the snake game, the pelicans, etc. | `workspace/` (gitignored) |
| [`logs/`](logs) | Every agent run as JSONL, one line per step, plus `num_ctx.json` (the measured context per model) | `logs/` (gitignored) |

The repo is public, so the backup:
- **leaves out** `.env` files (secrets), `.git` folders and caches. `.env.example` is kept.
- **masks** the home folder and user name as `<HOME>` / `<me>` in every text file.

Two folders are leftovers of old agent bugs:
- **`{WORKDIR}/`:** an unformatted f-string in an old prompt.
- **`-p`:** `mkdir -p` run under `cmd.exe`.

They're kept as they were, as evidence.

To use a run log with the M1 summarizer: `python tools/summarize_log.py archive/logs/<file>.jsonl`.
