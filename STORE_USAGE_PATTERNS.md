# Store Usage Patterns in assistant_core

## Overview

`assistant_core` integrates with **LangGraph's store API** to provide agents with persistent, namespace-based key-value state across invocations. The store is passed through graph compilation and is available to both nodes and tool functions at runtime.

This document describes how to initialize the store, use the API, and access it correctly from builders, nodes, and tools.

---

## 1. Store Initialization

### 1.1 Redis-backed Store (Production)

```python
from langgraph.store import redis

async with redis.AsyncRedisStore.from_conn_string(
    REDIS_URL, ttl=TTL_CONFIG
) as store:
    await store.setup()  # Initializes Redis index structures
    # pass store to graph compilation
```

**Key Points:**
- `.setup()` must be called before the store is used — it creates the required Redis indices.
- TTL configuration controls automatic key expiration.
- The store is passed to `workflow.compile(store=store)`, making it available to all nodes and tools at runtime.

### 1.2 FastAPI Dependency Injection Pattern

```python
from typing import Annotated
from fastapi import Depends
from langgraph.store import redis

async def inject_async_redis_store():
    async with redis.AsyncRedisStore.from_conn_string(
        REDIS_URL, ttl=TTL_CONFIG
    ) as redis_store:
        await redis_store.setup()
        yield redis_store

AsyncRedisStore = Annotated[redis.AsyncRedisStore, Depends(inject_async_redis_store)]
```

---

## 2. Store API

### 2.1 Writing: `aput()`

```python
await store.aput(namespace, key, value)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `namespace` | `tuple[str, ...]` | Hierarchical namespace, e.g. `(thread_id, "todos")` |
| `key` | `str` | Key within the namespace, e.g. `"current_item"` |
| `value` | `any` | Any JSON-serializable object (dict, list, str) |

```python
await store.aput((thread_id, "todos"), "active_item", todo_dict)
```

### 2.2 Reading: `aget()`

```python
item = await store.aget(namespace, key)
```

**Returns:** An `Item` object with a `.value` attribute, or `None` if the key does not exist.

```python
item = await store.aget((thread_id, "todos"), "active_item")
if item:
    data = item.value  # the stored dict/list/str
```

### 2.3 Semantic Search: `search()`

```python
items = store.search(namespace, query=query, limit=top_k)
```

**Returns:** A list of `Item` objects, each with `.value`, `.key`, and `.score` attributes.

```python
results = store.search((organization_id, "faqs"), query="return policy", limit=3)
for item in results:
    print(item.score, item.value)
```

**Note:** Requires the store backend to support vector search. Use `AsyncRedisStore` with an embeddings configuration for semantic retrieval.

---

## 3. Namespace Patterns

### 3.1 Thread-Scoped

Used for temporary per-thread state (e.g. current entity being processed):

```python
namespace = (thread_id, "todos")
await store.aput(namespace, "active_item", todo_dict)

item = await store.aget(namespace, "active_item")
```

**Use Case:** Multi-turn workflow state that must survive between agent invocations within the same thread but is not needed globally.

### 3.2 Organization/Tenant-Scoped

Used for shared state across all threads in a tenant:

```python
namespace = (organization_id,)
await store.aput(namespace, "available_options", options_list)

item = await store.aget(namespace, "available_options")
```

**Use Case:** Configuration or metadata that is shared across all threads for a given organization.

### 3.3 Namespace Convention

| Pattern | Example | Scope |
|---------|---------|-------|
| Thread-local | `(thread_id, "feature")` | Single thread |
| Organization-wide | `(organization_id,)` | All threads for a tenant |
| Feature-specific | `(org_id, "feature", "subkey")` | Scoped to a domain feature |

---

## 4. Accessing the Store

### 4.1 In Tool Functions — `InjectedStore`

LangGraph injects the store automatically into any tool parameter annotated with `InjectedStore`:

```python
from typing import Annotated
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def get_current_item(
    store: Annotated[BaseStore, InjectedStore],
    config: RunnableConfig,
) -> str:
    """Read the current item from store."""
    thread_id = config["configurable"]["thread_id"]
    item = await store.aget((thread_id, "todos"), "active_item")
    if not item:
        return "No item found."
    return str(item.value)
```

**Key Points:**
- `InjectedStore` is a LangGraph annotation — no extra wiring needed.
- The `config` parameter gives access to `configurable` values like `thread_id`.
- The store parameter can be typed as `BaseStore | None` to gracefully handle graphs compiled without a store.

### 4.2 In Node Classes — `runtime.store`

Nodes receive the store via the `Runtime` parameter in `__call__`:

```python
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

class ProcessItemNode:
    async def __call__(
        self,
        state: dict,
        config: RunnableConfig,
        runtime: Runtime,
    ) -> dict:
        store = runtime.store
        thread_id = config["configurable"]["thread_id"]
        namespace = (thread_id, "todos")

        item = await store.aget(namespace, "current")
        current = item.value if item else None

        # ... process current ...

        await store.aput(namespace, "current", updated)
        return {"messages": [...]}
```

**Key Points:**
- `runtime.store` is always available when the graph was compiled with a store.
- `runtime.context` also provides `db_session` and other injected context (see `ARCHITECTURE.md`).
- Nodes have full read/write access during their execution.

---

## 5. Graph Compilation with Store

Pass the store instance when compiling the graph:

```python
from langgraph.store.base import BaseStore
from assistant_core.builder import BuilderContext, SingleAgent

def build_graph(
    checkpointer=None,
    store: BaseStore | None = None,
) -> CompiledStateGraph:
    context = BuilderContext.create(
        {"OPENAI_API_KEY": OPENAI_API_KEY},
        agent_factory=MyPersona,
    )

    director = SingleAgent()
    director.add_builder(MyBuilder())

    workflow = director.make(context)
    return workflow.compile(checkpointer=checkpointer, store=store)
```

Once compiled with a store:
- All nodes receive it via `runtime.store`.
- All tools annotated with `InjectedStore` receive it automatically.
- The store persists across invocations sharing the same `thread_id`.

---

## 6. Key/Value Types

All values must be **JSON-serializable**.

**Supported:**
```python
# Dict (most common)
await store.aput(ns, "item", {"uuid": "...", "name": "...", "status": "active"})

# List
await store.aput(ns, "options", ["option_a", "option_b"])

# String
await store.aput(ns, "note", "Follow up tomorrow")

# Nested dict
await store.aput(ns, "config", {"feature": {"enabled": True, "threshold": 0.8}})
```

**Not supported:**
- Python objects / instances
- SQLAlchemy models (serialize first with `.model_dump()` or `dict()`)
- Functions or callables

```python
# Correct: serialize before storing
data = {
    "uuid": str(element.uuid),
    "data": element.data.model_dump(),
    "meta": element.meta.model_dump(),
}
await store.aput(namespace, key, data)
```

---

## 7. Namespace and Key Naming

Keys should be **descriptive, lowercase, snake_case**:
- ✅ `"active_item"`, `"pending_tasks"`, `"available_options"`
- ❌ `"item"`, `"temp"`, `"x"` (too vague)

Namespace segments should be **stable identifiers** (UUIDs or slugs), not user-controlled strings.

---

## 8. Best Practices

### 8.1 Always Check for `None`

```python
item = await store.aget(namespace, key)

# Safe
if item:
    value = item.value

# Unsafe — crashes if key missing
value = item.value
```

### 8.2 Namespace Isolation

Keep different concerns in separate namespaces, even within the same thread:

```python
thread_id = config["configurable"]["thread_id"]

await store.aput((thread_id, "todos"), "active_item", todo)
await store.aput((thread_id, "notes"), "current", note)
```

### 8.3 TTL

TTL is configured at store initialization. Redis handles expiry automatically — no manual cleanup is needed.

### 8.4 Store as Cache for Database State

A common pattern is to seed the store before graph invocation and keep it in sync after mutations:

```python
# Before invocation: seed store from DB
await store.aput((thread_id, "todos"), "active_item", item_dict)

# Inside a node: update DB, then refresh store
await db_manager.save(item)
await store.aput((thread_id, "todos"), "active_item", updated_item_dict)
```

This avoids repeated DB reads within a single thread while keeping the store consistent.

---

## 9. Testing Store-Based Code

### 9.1 In-Memory Store

Use `InMemoryStore` in tests to avoid a real Redis connection:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
compiled_graph = workflow.compile(checkpointer=checkpointer, store=store)
```

### 9.2 Omitting the Store

Pass `store=None` to `compile()` when the graph under test does not use the store. Nodes and tools that reference `runtime.store` will receive `None`.

### 9.3 Pre-Seeding the Store in Tests

```python
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage

store = InMemoryStore()
await store.aput(("thread-1", "todos"), "active_item", {"uuid": "abc", "title": "Buy milk", "done": False})

result = await graph.ainvoke(
    {"messages": [HumanMessage(content="Hello")]},
    config={"configurable": {"thread_id": "thread-1"}},
)
```

---

## 10. Summary

| Aspect | Details |
|--------|---------|
| **Initialization** | `AsyncRedisStore.from_conn_string(url, ttl=...)` → `await .setup()` |
| **Write** | `await store.aput(namespace, key, value)` |
| **Read** | `item = await store.aget(namespace, key)` → `item.value` |
| **Search** | `items = store.search(namespace, query=..., limit=...)` → list with `.value`, `.score` |
| **Namespaces** | Tuples of strings: `(thread_id, "feature")` or `(org_id,)` |
| **Values** | JSON-serializable only (dicts, lists, strings) |
| **Access in Tools** | `store: Annotated[BaseStore, InjectedStore]` parameter |
| **Access in Nodes** | `runtime.store` via `Runtime` parameter in `__call__` |
| **Persistence scope** | Per `thread_id` across multiple graph invocations |
| **TTL** | Configured at initialization; auto-expired by Redis |
| **Testing** | `InMemoryStore()` for unit tests; seed with `aput()` before invoking |
