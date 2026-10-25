START OF KNOWLEDGE BASE TEXT

**Local AI Infrastructure Blueprint for RTX 4070 Super (12GB VRAM)**

**1. Hardware Constraints & Deployment Strategy**

- **Total Available VRAM:** 12 GB.
- **Operating Strategy:** Do not deploy large dense models (>20B) or use heavy low-bit quantizations (like Q2) as they destroy logical coherence. The optimal target for primary tasks is the **12B to 14B range quantized at 4-bit (Q4_K_M)** or 5-bit, which yields maximum token-per-second velocity (25–40 tok/s) and preserves logic.
- **Multi-Agent Workflow Rule:** For parallel or multi-agent environments (e.g., automated marketing agency via CrewAI/AutoGen), utilize a **Hub-and-Spoke** architecture. Host one heavy 14B model for creative/logical sign-off, or offload background, sequential tasks to specialized Small Language Models (SLMs) under 4B parameters to stay safely within the 12GB VRAM threshold without system memory offloading.

---

**2. Primary Tier Models (Heavy Tasks)**

Deploy these individually for focused, deep sessions where high-level cognitive capability is required.

- **Role: Personal Assistant / Generalist**
    - **Model:** Qwen3 14B (Quantized Q4_K_M) [~9.2 GB VRAM]
    - **Core Benchmarks:** Elite MMLU and human-instruction adherence.
    - **Best For:** Everyday productivity, creative writing, nuanced conversation, complex instruction following, and multilingual tasks.
- **Role: Advanced Logical Reasoning & Code Architecture**
    - **Model:** DeepSeek-R1 14B (Distilled) [~9.0 GB VRAM]
    - **Core Benchmarks:** Dominated local logic, math, and long-chain debugging via _Chain-of-Thought_ (CoT).
    - **Best For:** Complex algorithmic architecture, deep code debugging, heavy step-by-step problem-solving.
- **Role: Standard Fast Coding & Scripting**
    - **Model:** Qwen3-Coder 14B [~9.2 GB VRAM]
    - **Core Benchmarks:** Leading HumanEval scores for standalone syntax, direct API hook-ups, and raw coding speed.
    - **Best For:** IDE completions (via Continue.dev/Aider), rapid scripting, boilerplate generation.
- **Role: Fast Creative & Enterprise Text**
    - **Model:** Gemma 4 12B [~9.4 GB VRAM]
    - **Core Benchmarks:** Google’s top-tier small model, outperforming older 13B/15B architectures in conversational text and corporate reasoning.

---

**3. Niche & Small Language Model (SLM) Tier (Agent Swarms)**

Deploy these for multi-agent loops, high-context data ingestion, and function-calling automation. These are highly optimized architectures that execute narrow tasks using minimal VRAM.

- **Role: Mega-Context Ingestion & Agentic Orchestration**
    - **Model:** Spark-X2.5 4B [~3.5 GB VRAM]
    - **Unique Feature:** Hybrid attention mechanism boasting a massive **1-million token context window**. Exceptional high scores on AIME 2026 (90.7) and GPQA (67.4).
    - **Best For:** Parsing entire programming codebases, massive marketing brand books, complex tool-calling workflows, and parallel sub-agents.
- **Role: Looped Mechanical & Workflow Automation**
    - **Model:** Nan Beige 4.2 3B [~3.0 GB VRAM]
    - **Unique Feature:** Utilizes a _looped transformer_ architecture to pass data through identical layers multiple times, hitting a 63% success rate on real GitHub issues.
    - **Best For:** File management agents, structured automated formatting, and mechanical backend operations.
- **Role: Micro-Reasoning & API Hooking**
    - **Model:** Smollm3 3B / LFM 2.5 1.2B "Thinking" [~1.5 - 2.5 GB VRAM]
    - **Unique Feature:** Micro-edge models baked with deep-thinking processes and strict JSON schema enforcement.
    - **Best For:** Extracting raw data from unformatted text, parsing emails, triggering clean webhooks, and function routing.
- **Role: Data Extraction & RAG Search**
    - **Model:** IBM Granite 4 (1B or 7B variants)
    - **Unique Feature:** High-density Mixture-of-Experts (MoE) specialized in technical and corporate structures.
    - **Best For:** Analyzing complex Excel sheets, raw CSV files, database structures, and handling precise financial/analytical RAG injection.
- **Role: Autonomous Tool-Execution**
    - **Model:** xLAM-2 (Downstream small variants)
    - **Unique Feature:** Stripped of conversational fluff, hard-coded for the Berkeley Function Calling Leaderboard.
    - **Best For:** Browsing the web, scraping competitor domains, and directly interacting with live SaaS application APIs.

---

**4. Execution Prompt for Assistant Workflow Recommendations**

_When acting as my local infrastructure advisor, evaluate tasks using this stack. If a pipeline requires heavy multi-step agent creation (e.g., setting up an automated marketing agency with individual agents for Copywriting, SEO, and Strategy), always recommend clustering small specialized SLMs like Spark-X2.5 4B or Nan Beige 3B to respect the 12GB VRAM barrier, while designating Qwen3 14B or DeepSeek-R1 14B as the master sequential evaluator._

END OF KNOWLEDGE BASE TEXT