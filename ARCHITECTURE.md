# Assistant Core Architecture

## Purpose and Scope

assistant_core provides reusable graph-building primitives for agent workflows built with LangGraph and LangChain.

This document covers assistant_core internals only, with emphasis on the builder subsystem used by downstream projects.

Out of scope:
- Webhooks, workers, Redis queues, and channel integrations outside this package.
- Product-specific business logic.

## Design Goals

- Keep workflow composition small, explicit, and testable.
- Separate graph wiring from agent/tool/model instantiation.
- Make extension points stable for downstream packages.
- Support both single-agent and multi-agent entrypoint strategies.

## High-Level Building Blocks

The package is organized around five layers:

- State types: typed state containers used by nodes and routing logic.
- Nodes: callable units that implement model invocation, prompting, and control flow.
- Context factory: pluggable creation of model, graph, nodes, and base tools.
- Builder context: runtime assembly state used by builders.
- Directors/builders: orchestration classes that mutate the graph wiring.

## Module Map

- assistant_core/models.py
  - Model loaders and defaults.
  - Default model is gpt-5-nano via ChatOpenAI.
- assistant_core/factories.py
  - ContextFactory and the deprecated BaseAgentFactory compatibility wrapper.
- assistant_core/state.py
  - QuestionState, NextProcessState, MultiAgentState.
- assistant_core/nodes/
  - BaseNode + mixins + concrete node implementations.
- assistant_core/builder/
  - BaseBuilder/BaseDirector, context objects, and concrete directors/builders.

## Core Build Pipeline

### 1) Context creation

ContextFactory is responsible for creating:
- graph builder (default StateGraph(MessagesState))
- model (default load_default_model with OPENAI_API_KEY)
- primary agent node
- resolver node (default name: resolver)
- base tools list (default empty)

BuilderContext materializes these dependencies and keeps mutable assembly state:
- graph_builder
- agent_node
- resolver_node
- tools
- entrypoint

### 2) Optional pre-builders

Before the agent wiring is finalized, directors run custom builders registered through add_builder.

A builder can:
- register extra nodes
- append tools to context.tools (prefer grouping related domain tools per builder)
- push a new entrypoint

Entrypoint behavior is intentionally LIFO:
- setting context.entrypoint adds an edge from new_entrypoint to previous_entrypoint
- repeated assignments build a chain ending at the agent node

### 3) Agent wiring

AgentBuilder performs the canonical final wiring:

- Rebinds tools to agent_node.
- Adds the agent node.
- Adds conditional edges from agent node using tools_condition:
  - tools branch -> tools_<agent_name>
  - END branch -> END
- Adds ToolNode(context.tools) as tools_<agent_name>.
- Adds edge tools_<agent_name> -> resolver node.
- Configures resolver.next_node to return to the agent node by default.

Result: model decisions can invoke tools, then route through resolver for next-step control.

## Directors

### SingleAgentDirector

Flow:
- Run registered custom builders.
- Set graph entry point to current context.entrypoint.
- Run AgentBuilder for canonical agent/tools/resolver wiring.

Alias exported as SingleAgent.

### MultiAgentDirector

Adds conditional entrypoint selection on top of the same builder model.

Flow:
- Run registered custom builders.
- Ensure entrypoint_mapping has default (falls back to current entrypoint if missing).
- Set conditional entry point selector from MultiAgentContext.
- Run AgentBuilder.

The selector reads active_agent from state and chooses the matching mapped entrypoint.

Alias exported as MultiAgent.

## Node Architecture

### Base contract

All nodes inherit from BaseNode and implement async __call__(state, config) -> dict or routing command.

### Mixins

- UsesModel
  - keeps base model reference
  - supports bind_tools/rebind_tools
- UsesJsonModel
  - structured JSON output helper
- UsesSystemMessage
  - helper methods to emit SystemMessage values
- Include*Node mixins
  - shared routing attributes (next_node, end_node, error_node, question_node)

### Concrete nodes

- AgentNode
  - prepends system prompts to state messages
  - invokes model asynchronously
- PromptNode
  - injects formatted system prompt into message stream
- QuestionNode
  - uses LangGraph interrupt for human-in-the-loop answer capture
- ResolverNode
  - routes with Command based on state.next
  - default goto is next_node; clears next after routing
- DataNode / ProcessDataNode
  - abstract extension points for data-oriented logic

## State Model

- QuestionState
  - question and answer slots for interactive steps.
- NextProcessState
  - next field with replacement reducer for resolver routing.
- MultiAgentState
  - active_agent selector used by conditional multi-entry workflows.

## Extension Patterns

### Recommended: ContextFactory with injected factories

Use BuilderContext.create(...) or a custom ContextFactory instance to inject:
- agent_factory
- graph_factory
- model_factory
- resolver_factory
- base_tools_factory

BuilderContext.clone(...) supports per-graph overrides while preserving the original configuration.

### Compatibility: BaseAgentFactory

BaseAgentFactory remains available as a deprecated wrapper over ContextFactory and is still used in examples for readability.

## Example-Backed Workflows

The examples directory demonstrates two key patterns:

- Basic graph assembly
  - create a factory
  - build context
  - register optional builders (for example TavilyBuilder)
  - compile and invoke/stream the graph
- Entrypoint chaining
  - multiple builders set context.entrypoint
  - final graph preserves LIFO chain before agent execution

## Guarantees Verified by Tests

Unit tests enforce the following architectural behaviors:

- BuilderContext defaults to agent node entrypoint.
- Entrypoint setter creates LIFO edge chains.
- Single-agent and multi-agent directors compile valid workflows.
- Multi-agent default mapping is auto-populated but not overwritten when already set.
- TavilyBuilder appends a tool into context.tools.
- DateTimeBuilder registers a pre-agent entrypoint node.
- ResolverNode emits Command values consistent with NextProcessState.next.

## Runtime Notes

- Environment values are loaded via dotenv in assistant_core/settings.py.
- OPENAI_API_KEY is required when using the default model factory path (load_default_model).
- A Tavily API key is required when using TavilySearch integrations; it can be provided from environment settings or passed explicitly to TavilyBuilder.

## Package Boundary

assistant_core intentionally stops at graph construction and node primitives.

Higher-level runtime concerns are out of scope here by design. This keeps the package focused on stable composition contracts for builders, contexts, state, and nodes.
