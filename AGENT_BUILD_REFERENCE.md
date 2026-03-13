# Agent Build Reference (assistant_core)

## Audience

This document is a prescriptive reference for AI agents (and developers) building projects that import assistant_core as an external library.

## Goal

Build a compiled LangGraph assistant that:
- uses assistant_core builder/context abstractions,
- supports tool calling,
- can be invoked with a thread id,
- and is easy to extend with custom builders.

## Hard Rules

1. Prefer `ContextFactory` and `BuilderContext.create(...)` for new code.
2. Do not introduce new implementations based on `BaseAgentFactory` (deprecated).
3. Use `SingleAgent` unless there is a real routing need for `MultiAgent`.
4. Keep custom builders small and side-effect only through `context`.
5. Group related tools in a single domain builder and register them together.
6. Do not pass tool objects as builder constructor parameters; builders should define the related tool set internally.

## Build From Scratch (Single Agent)

### 1) Install and import dependencies

```bash
# Install assistant_core from GitHub (project is not on PyPI yet).
# Choose one command based on your package manager.

# pip
pip install "git+https://github.com/LOBICA/assistant_core.git"

# uv
uv add "git+https://github.com/LOBICA/assistant_core.git"

# Poetry
poetry add "git+https://github.com/LOBICA/assistant_core.git"

# PDM
pdm add "git+https://github.com/LOBICA/assistant_core.git"
```

```python
from langgraph.checkpoint.memory import MemorySaver

from assistant_core.builder import BuilderContext, SingleAgent
from assistant_core.nodes import AgentNode
```

### 2) Define agent behavior

Create an `agent_factory(model)` that returns an `AgentNode`.

```python
SYSTEM_PROMPT = """
You are a concise and reliable assistant.
Use available tools when needed.
""".strip()


def agent_factory(model):
    return AgentNode(
        name="assistant",
        model=model,
        prompts=[SYSTEM_PROMPT],
    )
```

### 3) Create context

Use `BuilderContext.create(...)` and pass config with `OPENAI_API_KEY` when using the default model path.

```python
def build_context(openai_api_key: str) -> BuilderContext:
    return BuilderContext.create(
        {
            "OPENAI_API_KEY": openai_api_key,
        },
        agent_factory=agent_factory,
    )
```

### 4) Compose graph

Use `SingleAgent` and register optional builders before `make(...)`.

```python
def build_graph(openai_api_key: str):
    context = build_context(openai_api_key)

    director = SingleAgent()
    # Example: director.add_builder(MyCustomBuilder(...))

    workflow = director.make(context)
    return workflow.compile(checkpointer=MemorySaver())
```

### 5) Invoke graph

Always pass a stable `thread_id` in config.

```python
async def run_once(graph):
    config = {"configurable": {"thread_id": "my-thread-1"}}
    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        },
        config=config,
    )
    return result["messages"][-1]
```

## Add Tools

Tools are registered through builders by appending to `context.tools`.

Preferred pattern: one builder owns a related set of tools for a domain capability.

```python
from assistant_core.builder import BaseBuilder


class CustomerSupportToolsBuilder(BaseBuilder):
    """Register customer-support related tools as one cohesive capability set."""

    def build(self, context):
        context.tools.append(get_customer_profile)
        context.tools.append(get_open_tickets)
        context.tools.append(create_ticket)
        context.tools.append(update_ticket)
```

```python
director = SingleAgent()
director.add_builder(DateTimeBuilder())
director.add_builder(CustomerSupportToolsBuilder())
```

When `SingleAgent.make(...)` runs:
- tools are rebound to the `AgentNode`,
- a `ToolNode` is wired,
- control returns through `ResolverNode`.

## Add Pre-Agent Steps

To add preprocessing or context-injection steps, create builders that:
1. add one or more nodes,
2. set `context.entrypoint`.

Entrypoints are chained in LIFO order.

```python
from assistant_core.builder import BaseBuilder
from assistant_core.nodes import PromptNode


class IntakePromptBuilder(BaseBuilder):
    def build(self, context):
        node = PromptNode(
            name="intake_prompt",
            prompt="You are handling a support request.",
        )
        context.graph_builder.add_node(node.name, node)
        context.entrypoint = node.name
```

## Multi-Agent Routing (Only If Needed)

Use `MultiAgent` + `MultiAgentContext` when you need conditional entry points chosen by `state["active_agent"]`.

Minimal flow:
1. Build a `ContextFactory`.
2. Wrap it in `MultiAgentContext`.
3. Register builders that create named entrypoint nodes.
4. Populate `context.entrypoint_mapping`.
5. Build with `MultiAgent.make(context)`.

If `default` is missing, `MultiAgent` auto-fills it from the current entrypoint.

## Common Failure Modes

1. `NotImplementedError: Agent factory must be provided`
Cause: missing `agent_factory` in context creation.
Fix: always pass `agent_factory` to `BuilderContext.create(...)` or `ContextFactory`.

2. Model/key errors at runtime
Cause: default model path used without `OPENAI_API_KEY`.
Fix: pass key in context config, or provide custom `model_factory`.

3. Unexpected graph start node
Cause: multiple builders set entrypoint; last set becomes current entrypoint.
Fix: review builder order and entrypoint assignments.

4. Tools not being called
Cause: tools not appended to `context.tools` before director `make(...)`.
Fix: register tool builders before building workflow; keep each builder responsible for a related tool set.

## Quick Starter Template

Copy this into a new module and adapt names/prompts/tools:

```python
from langgraph.checkpoint.memory import MemorySaver

from assistant_core.builder import BuilderContext, SingleAgent
from assistant_core.nodes import AgentNode


def _agent_factory(model):
    return AgentNode(
        name="assistant",
        model=model,
        prompts=["You are a helpful assistant."],
    )


def build_assistant_graph(openai_api_key: str):
    context = BuilderContext.create(
        {"OPENAI_API_KEY": openai_api_key},
        agent_factory=_agent_factory,
    )

    director = SingleAgent()
    workflow = director.make(context)

    return workflow.compile(checkpointer=MemorySaver())
```
