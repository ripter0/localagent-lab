"""All benchmark tasks. all_tasks(num_ctx) builds the full list for one model."""
from bench.tasks.agentic import AGENT_TASKS
from bench.tasks.chat import CHAT_TASKS
from bench.tasks.core import Task
from bench.tasks.long_context import CHARS_PER_TOKEN, long_context_tasks

BENCH_VERSION = 2  # bump when tasks change, so old and new scores are never ranked together
CATEGORIES = ["json-tools", "instructions", "reasoning", "code", "italiano", "long-context", "agent", "safety"]


def all_tasks(num_ctx):
    return CHAT_TASKS + long_context_tasks(num_ctx) + AGENT_TASKS


__all__ = ["AGENT_TASKS", "BENCH_VERSION", "CATEGORIES", "CHARS_PER_TOKEN", "CHAT_TASKS", "Task", "all_tasks", "long_context_tasks"]
