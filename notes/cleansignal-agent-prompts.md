## 🛠️ Step 1: Configure `agent.py` Correctly

Update these 3 lines in `agent.py`:

```python
# Line 1: Set your coding agent model
MODEL = "qwen3.5-9b"  # OR whatever model name you have in Ollama

# Line 2: Set your workspace to the CleanSignal project folder
WORKDIR = Path("%USERPROFILE%\\Desktop\\ai test pazzi\\CleanSignal citizen pollution reports").resolve()

# Line 3: Update SYSTEM_PROMPT with CleanSignal context (see below)
```

---

## 📋 Step 2: Update `SYSTEM_PROMPT`

Replace the `SYSTEM_PROMPT` in `agent.py` with this:

```python
SYSTEM_PROMPT = """You are a coding agent building CleanSignal - a citizen pollution reporting web app.

PROJECT:
- CleanSignal: FastAPI pollution reporting app for citizens
- Tech: Python, FastAPI, PostgreSQL/SQLite, HTML/CSS/JS
- Model: Uses local AI for routing logic (not for code generation)
- Workspace: {WORKDIR}

TOOLS:
- list_dir, read_file, write_file, run_command, finish

RULES:
- Output JSON only: {"thought": "...", "tool": "...", "args": {...}}
- Work inside workspace folder only
- After writing code, verify it works
- Keep responses concise
- Follow project phases: Init → DB → API → Frontend → Security

PHASES TO BUILD:
1. Initialize project structure and config files
2. Define database models and schema
3. Build API endpoints and routing logic
4. Create frontend templates and static assets
5. Add security and deployment instructions

START: Phase 1 - Project Initialization
"""
```

---

## 📋 Step 3: Complete Prompt Set (Save to `clean_signal_prompts.txt`)

Here's everything you need to paste into the agent, one prompt at a time:

```
INITIALIZE CLEAN SIGNAL PROJECT
--------------------------------
Initialize CleanSignal project. Create project structure and configuration files. Create .env with placeholder
variables. Create requirements.txt with FastAPI dependencies. Create README.md with project documentation. Create
all directories: templates/, static/, data/. Create empty files with initial content.

CLEANUP DUPLICATE FILES
------------------------
Clean up any duplicate files from nested directories. Ensure all code is in a single directory structure. Remove
any files created in wrong locations. Verify project structure matches planned layout.
```

---

## 📋 Phase 2: Database & Data Models

```
PHASE 2: DATABASE & DATA MODELS
--------------------------------
Define database models and schema. Create model_config.py with Pydantic models for Report and User. Define fields
for location, pollutant type, severity, timestamp. Ensure compatibility with SQLAlchemy.
```

---

## 📋 Phase 3: API Endpoints & Routing Logic

```
PHASE 3: API ENDPOINTS & ROUTING LOGIC
---------------------------------------
Build API endpoints and routing logic. Create api.py with route handlers for submitting and retrieving reports.
Create routing.py for department routing logic using the decision model. Create prompts.py for AI model
classification. Create config.py for configuration settings.
```

---

## 📋 Phase 4: Frontend & Static Assets

```
PHASE 4: FRONTEND & STATIC ASSETS
----------------------------------
Create frontend templates and static assets. Create templates/index.html with pollution report form. Create
static/css/style.css with environmental color scheme. Create static/js/app.js with client-side logic. Ensure
responsive design for mobile devices.
```

---

## 📋 Phase 5: Security & Deployment

```
PHASE 5: SECURITY & DEPLOYMENT
------------------------------
Add security and deployment instructions. Review config.py for environment variable loading from .env file. Create
deployment instructions in README.md. Finalize project structure. Ensure all files are consistent with the defined
structure.
```

---

## 📋 Phase 6: Testing & Validation

```
PHASE 6: TESTING & VALIDATION
-----------------------------
Testing and validation. Create test files for API endpoints. Run tests to verify database connectivity. Test
frontend form submission and error handling. Verify routing logic with sample pollution reports.
```

---

## 📋 Phase 7: Decision Model Integration

```
PHASE 7: DECISION MODEL INTEGRATION
-----------------------------------
Decision model integration. Configure the decision model (rizzo-flow) for routing logic. Create integration points
in routing.py. Test decision model with sample pollution reports. Verify confidence scores and routing accuracy.
```

---

## 📋 Phase 8: Final Deployment

```
PHASE 8: FINAL DEPLOYMENT
-------------------------
Final deployment. Ensure all files are in the correct directory. Verify database connection. Test all API
endpoints. Check frontend responsiveness. Create deployment guide in README.md.
```

---

## 📋 Phase 9: Documentation & README

```
PHASE 9: DOCUMENTATION & README
-------------------------------
Documentation and README. Update README.md with complete installation and usage instructions. Add troubleshooting
section. Include model configuration details. Add API endpoint documentation.
```

---

## 📋 Phase 10: Final Verification

```
PHASE 10: FINAL VERIFICATION
----------------------------
Final verification. List all files in project directory. Verify all required files exist. Check for any missing
dependencies. Run a final test to ensure everything works together.
```

---

## 💾 Save This File

Save the above prompts to a file called `clean_signal_prompts.txt` and paste them one at a time into the agent.

---

## ⚠️ Important Reminders

- **One prompt at a time** - Don't paste multiple prompts together
- **Type `y`** when prompted for shell commands (installing dependencies)
- **Wait for phase completion** before proceeding
- **Check file structure** after each phase to ensure correct directory
- **Remove duplicate files** if the agent creates them in nested directories

---

Would you like me to create a cleanup script or prompt specifically for removing the duplicate files from the
nested directories?