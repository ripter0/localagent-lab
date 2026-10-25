"""All benchmark tasks. all_tasks(num_ctx) builds the full list for one model."""
from bench.tasks.agentic import AGENT_TASKS
from bench.tasks.chat import CHAT_TASKS
from bench.tasks.core import Task
from bench.tasks.long_context import CHARS_PER_TOKEN, long_context_tasks

# bump when tasks or the agent change, so old and new scores are never ranked together
# v3: agent got replace_in_file, safety and docstring rules, 8192-token replies; json-replace task; 10 min limit
BENCH_VERSION = 3
CATEGORIES = ["json-tools", "instructions", "reasoning", "code", "italiano", "long-context", "agent", "safety"]


def all_tasks(num_ctx):
    return CHAT_TASKS + long_context_tasks(num_ctx) + AGENT_TASKS


__all__ = ["AGENT_TASKS", "BENCH_VERSION", "CATEGORIES", "CHARS_PER_TOKEN", "CHAT_TASKS", "Task", "all_tasks", "long_context_tasks"]
