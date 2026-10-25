`"""`

`Minimal local coding agent for Ollama.`

`Setup:`

`pip install requests`

`ollama list # copy the exact model name into MODEL below`

`python agent.py`

`The agent works only inside ./workspace. Shell commands need your approval.`

`"""`

`import json`

`import subprocess`

`from pathlib import Path`

`import requests`

`` MODEL = "qwen3.8-27b-gsq-rco-iq2_xs" # <- replace with the name shown by `ollama list` ``

`OLLAMA_URL = "http://localhost:11434/api/chat"`

`WORKDIR = Path("workspace").resolve()`

`WORKDIR.mkdir(exist_ok=True)`

`MAX_STEPS = 15`

`MAX_OUTPUT = 4000 # characters of tool output sent back to the model`

`SYSTEM_PROMPT = """You are a coding agent working inside a project folder.`

`You solve the user's task step by step using tools.`

`On EVERY turn reply with exactly one JSON object and nothing else:`

`{"thought": "short reasoning", "tool": "<tool name>", "args": {...}}`

`Tools:`

`- list_dir args: {"path": "."}`

`- read_file args: {"path": "main.py"}`

`- write_file args: {"path": "main.py", "content": "full file content"}`

`- run_command args: {"command": "python main.py"}`

`- finish args: {"message": "summary for the user"}`

`Rules:`

`- Look at the files before changing them.`

`- After writing code, run it or its tests to check that it works.`

`- If something fails, read the error and fix it.`

`- Call finish when the task is done.`

`"""`

`# ---------- tools ----------`

`def safe_path(p: str) -> Path:`

`full = (WORKDIR / p).resolve()`

`if WORKDIR not in full.parents and full != WORKDIR:`

`raise ValueError("path is outside the workspace")`

`return full`

`def list_dir(path="."):`

`items = sorted(safe_path(path).iterdir())`

`return "\n".join(i.name + ("/" if i.is_dir() else "") for i in items) or "(empty)"`

`def read_file(path):`

`return safe_path(path).read_text()`

`def write_file(path, content):`

`f = safe_path(path)`

`f.parent.mkdir(parents=True, exist_ok=True)`

`f.write_text(content)`

`return f"wrote {len(content)} characters to {path}"`

`def run_command(command):`

`print(f"\n Agent wants to run: {command}")`

`if input(" Allow? [y/N] ").strip().lower() != "y":`

`return "The user denied this command."`

`try:`

`r = subprocess.run(command, shell=True, cwd=WORKDIR,`

`capture_output=True, text=True, timeout=30)`

`return f"exit code {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"`

`except subprocess.TimeoutExpired:`

`return "Command timed out after 30 seconds."`

`TOOLS = {"list_dir": list_dir, "read_file": read_file,`

`"write_file": write_file, "run_command": run_command}`

`# ---------- model call ----------`

`def ask_model(messages):`

`r = requests.post(OLLAMA_URL, json={`

`"model": MODEL,`

`"messages": messages,`

`"stream": False,`

`"format": "json", # forces valid JSON output`

`"options": {"temperature": 0.2, "num_ctx": 8192},`

`}, timeout=600)`

`r.raise_for_status()`

`return r.json()["message"]["content"]`

`# ---------- agent loop ----------`

`def run_agent(task):`

`messages = [{"role": "system", "content": SYSTEM_PROMPT},`

`{"role": "user", "content": task}]`

`for step in range(1, MAX_STEPS + 1):`

`raw = ask_model(messages)`

`messages.append({"role": "assistant", "content": raw})`

`try:`

`action = json.loads(raw)`

`tool, args = action["tool"], action.get("args", {})`

`except (json.JSONDecodeError, KeyError):`

`messages.append({"role": "user",`

`"content": "Invalid format. Reply with one JSON object: thought, tool, args."})`

`continue`

`print(f"\n[{step}] {action.get('thought', '')}\n -> {tool} {json.dumps(args)[:200]}")`

`if tool == "finish":`

`print("\nDONE:", args.get("message", ""))`

`return`

`if tool not in TOOLS:`

`result = f"Unknown tool '{tool}'. Available: {list(TOOLS)} and finish."`

`else:`

`try:`

`result = TOOLS[tool](**args)`

`except Exception as e:`

`result = f"Tool error: {e}"`

`messages.append({"role": "user",`

`"content": f"Tool result:\n{str(result)[:MAX_OUTPUT]}"})`

`print("\nStopped: reached the step limit.")`

`if __name__ == "__main__":`

`print(f"Workspace: {WORKDIR}")`

`while True:`

`task = input("\nTask (empty to quit): ").strip()`

`if not task:`

`break`

`run_agent(task)`