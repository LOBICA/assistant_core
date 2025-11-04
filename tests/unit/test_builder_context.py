import warnings
from unittest import mock

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import MessagesState, StateGraph

from assistant_core.builder.context import BuilderContext, MultiAgentContext
from assistant_core.nodes import AgentNode, PromptNode, ResolverNode


def test_builder_context_initialization_defaults(builder_context):
    # Provided via fixture with ContextFactory using agent/model factories
    ctx = builder_context

    assert isinstance(ctx.graph_builder, StateGraph)
    assert ctx.agent_node.name == "test_agent"
    assert ctx.resolver_node.name == "resolver"
    assert isinstance(ctx.tools, list)
    # Default entrypoint is the agent node
    assert ctx.entrypoint == ctx.agent_node.name


def test_entrypoint_setter_creates_lifo_edges(builder_context):
    ctx = builder_context

    # Register two custom nodes
    n1 = PromptNode(name="node_1", prompt="n1")
    n2 = PromptNode(name="node_2", prompt="n2")
    ctx.graph_builder.add_node(n1.name, n1)
    ctx.graph_builder.add_node(n2.name, n2)

    # Initial entrypoint should be the agent
    assert ctx.entrypoint == "test_agent"

    # Setting entrypoint should add an edge to previous entrypoint
    ctx.entrypoint = n1.name
    ctx.entrypoint = n2.name

    assert ("node_1", "test_agent") in ctx.graph_builder.edges
    assert ("node_2", "node_1") in ctx.graph_builder.edges
    # Current entrypoint is the last set value
    assert ctx.entrypoint == "node_2"


def test_create_classmethod_uses_factories(mock_model, factory_config):
    def model_factory(cfg):
        assert cfg == factory_config
        return mock_model

    def agent_factory(model):
        assert model is mock_model
        return AgentNode(name="custom_agent", model=model, prompts=["Hi"])

    def graph_factory():
        return StateGraph(MessagesState)

    def resolver_factory():
        return ResolverNode(name="custom_resolver")

    tools = [mock.Mock(name="tool1"), mock.Mock(name="tool2")]

    ctx = BuilderContext.create(
        factory_config,
        agent_factory=agent_factory,
        graph_factory=graph_factory,
        model_factory=model_factory,
        resolver_factory=resolver_factory,
        base_tools_factory=lambda: tools,
    )

    assert isinstance(ctx, BuilderContext)
    assert isinstance(ctx.graph_builder, StateGraph)
    assert ctx.agent_node.name == "custom_agent"
    assert ctx.resolver_node.name == "custom_resolver"
    assert ctx.model is mock_model
    assert ctx.tools is tools
    assert ctx.entrypoint == "custom_agent"


def test_clone_same_factories(builder_context):
    # Clone without overrides should produce an independent but equivalent context
    original = builder_context

    cloned = original.clone()

    assert cloned is not original
    assert cloned.agent_node.name == original.agent_node.name
    assert cloned.resolver_node.name == original.resolver_node.name
    assert cloned.model is original.model
    assert cloned.tools == original.tools
    assert isinstance(cloned.graph_builder, StateGraph)
    # Original remains unchanged
    assert original.agent_node.name == "test_agent"
    assert original.resolver_node.name == "resolver"


def test_clone_overrides_factories(context_factory, builder_context):
    # Original context
    original = builder_context
    assert original.agent_node.name == "test_agent"
    assert original.resolver_node.name == "resolver"

    # New model and overrides
    new_model = mock.Mock(spec=BaseChatModel)

    def model_factory(_cfg):
        return new_model

    received_models: list[BaseChatModel] = []

    def agent_factory(model):
        # Record the model used to build the agent; cloning may keep cached model
        received_models.append(model)
        return AgentNode(name="agent_clone", model=model, prompts=["clone"])

    def graph_factory():
        return StateGraph(MessagesState)

    def resolver_factory():
        return ResolverNode(name="resolver_clone")

    tools = [mock.Mock(name="toolX")]

    cloned = original.clone(
        agent_factory=agent_factory,
        graph_factory=graph_factory,
        model_factory=model_factory,
        resolver_factory=resolver_factory,
        base_tools_factory=lambda: tools,
    )

    # Ensure the clone uses overrides and is independent from original
    assert cloned is not original
    assert cloned.agent_node.name == "agent_clone"
    assert cloned.resolver_node.name == "resolver_clone"
    # Model may be cached from the original factory; ensure consistency
    assert cloned.model is new_model
    assert received_models == [cloned.model]
    assert cloned.tools is tools
    assert isinstance(cloned.graph_builder, StateGraph)
    # Original remains unchanged
    assert original.agent_node.name == "test_agent"
    assert original.resolver_node.name == "resolver"


def test_init_with_deprecated_agent_factory_param(context_factory):
    # Passing a ContextFactory via deprecated param should warn and work
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        ctx = BuilderContext(agent_factory=context_factory)
    assert any(
        issubclass(w.category, DeprecationWarning) for w in rec
    ), "Expected a DeprecationWarning when using agent_factory param"
    assert ctx.agent_node.name == "test_agent"
    assert ctx.entrypoint == "test_agent"


def test_multi_agent_context_selector_behavior(context_factory):
    ctx = MultiAgentContext(context_factory)

    # Default entrypoint is agent name
    assert ctx.entrypoint == "test_agent"

    # Map some agents to custom entrypoints
    ctx.entrypoint_mapping["a1"] = "node_a1"
    ctx.entrypoint_mapping["default"] = "node_default"

    selector = ctx.conditional_entrypoint_factory()

    # When no active_agent present, use mapping['default']
    assert selector({}) == "node_default"
    # Known active_agent → mapped entrypoint
    assert selector({"active_agent": "a1"}) == "node_a1"
    # Unknown active_agent → fallback to context.entrypoint (agent node)
    assert selector({"active_agent": "unknown"}) == "test_agent"
