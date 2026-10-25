# Curriculum map

Which lessons of [ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) to use for each milestone. The milestones are the plan. The course is the reference. Never aim to finish the whole course.

Rules:
- Use only the original `rohitg00/ai-engineering-from-scratch` repo (forks may carry malware).
- For each lesson: read `docs/en.md`, then retype the idea into **this** repo, with a test. Don't copy their `code/` folder in.
- Read a lesson when the milestone needs it, not before.
- Math-heavy phases (1, 3 and the end of 10) wait until year 2.

Lesson folder names checked on 2026-10-25. Links point to `phases/<phase>/<lesson>`.

| Milestone | Lessons | Why |
|---|---|---|
| M1 Python basics | none. CS50P only | Learn the language first |
| M2 Talk to the model | [11/01 prompt-engineering], [11/03 structured-outputs], [13/04 structured-output] | Getting one reliable JSON action back |
| M3 Tools | [13/01 the-tool-interface], [13/05 tool-schema-design], [14/06 tool-use-and-function-calling] | How to describe tools so a small model calls them right |
| M4 The loop | [14/01 the-agent-loop] (main one), [11/09 function-calling] | Compare with your `run_agent` |
| M5 Logging | [14/24 agent-observability-platforms] (just the ideas, no platform) | What is worth logging per step |
| M6 Eval harness | [11/10 evaluation], [14/30 eval-driven-agent-development], [14/19 benchmarks-swebench-gaia] (skim) | Your 10 pytest tasks are a tiny SWE-bench |
| M7 Better tools and safety | [14/26 failure-modes-agentic], [14/27 prompt-injection-defense], [14/38 verification-gates], [13/26 skill-permissions-sandboxes-and-trust] | Limits, sandboxing, and "never trust the model" |
| M8 Model comparison | [11/05 context-engineering], [10/11 quantization] (read only, no math) | Why `num_ctx` and Q4 change results |
| M9 Advisor mode | [14/07 memory-virtual-context-memgpt], [11/04 embeddings] | Reading `profile.md` and `notes.md` without overflowing context |
| M10 Decider experiment | [13/21 llm-routing-layer], [03/11 intro-to-pytorch], [05/22 embedding-models-deep-dive] | A small model or encoder that picks one decision |
| M11 Packaging | [14/32 minimal-agent-workbench] (structure ideas) | What a clean agent repo looks like |

Later (after M11 or in year 2): Phase 14 lessons 31-42 (agent workbench missions), Phase 13 lessons 06-10 (MCP: turn your tools into an MCP server), Phase 10 lessons 01-04 (build a tokenizer and a mini GPT).

[11/01 prompt-engineering]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/01-prompt-engineering
[11/03 structured-outputs]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/03-structured-outputs
[11/04 embeddings]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/04-embeddings
[11/05 context-engineering]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/05-context-engineering
[11/09 function-calling]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/09-function-calling
[11/10 evaluation]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-llm-engineering/10-evaluation
[13/01 the-tool-interface]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-tools-and-protocols/01-the-tool-interface
[13/04 structured-output]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-tools-and-protocols/04-structured-output
[13/05 tool-schema-design]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-tools-and-protocols/05-tool-schema-design
[13/21 llm-routing-layer]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-tools-and-protocols/21-llm-routing-layer
[13/26 skill-permissions-sandboxes-and-trust]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-tools-and-protocols/26-skill-permissions-sandboxes-and-trust
[14/01 the-agent-loop]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/01-the-agent-loop
[14/06 tool-use-and-function-calling]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/06-tool-use-and-function-calling
[14/07 memory-virtual-context-memgpt]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/07-memory-virtual-context-memgpt
[14/19 benchmarks-swebench-gaia]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/19-benchmarks-swebench-gaia
[14/24 agent-observability-platforms]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/24-agent-observability-platforms
[14/26 failure-modes-agentic]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/26-failure-modes-agentic
[14/27 prompt-injection-defense]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/27-prompt-injection-defense
[14/30 eval-driven-agent-development]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/30-eval-driven-agent-development
[14/32 minimal-agent-workbench]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/32-minimal-agent-workbench
[14/38 verification-gates]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-agent-engineering/38-verification-gates
[10/11 quantization]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/10-llms-from-scratch/11-quantization
[03/11 intro-to-pytorch]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/03-deep-learning-core/11-intro-to-pytorch
[05/22 embedding-models-deep-dive]: https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/05-nlp-foundations-to-advanced/22-embedding-models-deep-dive
