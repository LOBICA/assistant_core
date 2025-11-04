from assistant_core.builder import BaseBuilder, MultiAgent, SingleAgent
from assistant_core.nodes import PromptNode


def test_single_agent_build(builder_context):
    agent = SingleAgent()
    workflow = agent.make(builder_context)
    assert workflow is not None

    graph = workflow.compile()
    assert graph is not None


def test_single_agent_entrypoint(builder_context):
    class CustomBuilderWithEntrypoint(BaseBuilder):
        def __init__(self, custom_node_name: str):
            super().__init__()
            self.custom_node_name = custom_node_name

        def build(self, context):
            custom_node = PromptNode(
                name=self.custom_node_name,
                prompt=f"Testing the custom node {self.custom_node_name}",
            )

            context.graph_builder.add_node(
                custom_node.name,
                custom_node,
            )

            context.entrypoint = custom_node.name

    agent = SingleAgent()
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_1"))
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_2"))
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_3"))

    workflow = agent.make(builder_context)
    assert workflow is not None

    assert {
        ("__start__", "custom_node_3"),
        ("custom_node_3", "custom_node_2"),
        ("custom_node_2", "custom_node_1"),
        ("custom_node_1", "test_agent"),
        ("tools_test_agent", "resolver"),
    } == workflow.edges


def test_multi_agent_entrypoint_chain_and_default_mapping(multi_agent_context):
    class CustomBuilderWithEntrypoint(BaseBuilder):
        def __init__(self, custom_node_name: str):
            self.custom_node_name = custom_node_name

        def build(self, context):
            node = PromptNode(
                name=self.custom_node_name,
                prompt=f"Testing the custom node {self.custom_node_name}",
            )
            context.graph_builder.add_node(node.name, node)
            # Push this node as the new entrypoint (LIFO), linking to previous
            context.entrypoint = node.name

    ctx = multi_agent_context

    agent = MultiAgent()
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_1"))
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_2"))
    agent.add_builder(CustomBuilderWithEntrypoint("custom_node_3"))

    workflow = agent.make(ctx)
    assert workflow is not None

    # Default mapping should be set to last entrypoint when not provided
    assert ctx.entrypoint_mapping.get("default") == "custom_node_3"

    # Edges should reflect the LIFO chain and tools -> resolver wiring
    expected_edges = {
        ("custom_node_3", "custom_node_2"),
        ("custom_node_2", "custom_node_1"),
        ("custom_node_1", "test_agent"),
        ("tools_test_agent", "resolver"),
    }
    assert workflow.edges == expected_edges


def test_multi_agent_preserves_existing_default_mapping(multi_agent_context):
    class SimpleEntrypointBuilder(BaseBuilder):
        def build(self, context):
            node = PromptNode(name="ep_node", prompt="n")
            context.graph_builder.add_node(node.name, node)
            context.entrypoint = node.name
            context.entrypoint_mapping["ep_agent"] = node.name

    ctx = multi_agent_context
    # Predefine default mapping; director should not override it
    ctx.entrypoint_mapping["default"] = "predefined_node"

    agent = MultiAgent()
    agent.add_builder(SimpleEntrypointBuilder())

    workflow = agent.make(ctx)
    assert workflow is not None

    # Ensure mapping wasn't overwritten
    assert ctx.entrypoint_mapping["default"] == "predefined_node"
    assert ctx.entrypoint_mapping["ep_agent"] == "ep_node"
    # LIFO edge and tools wiring should still be present
    assert ("ep_node", "test_agent") in workflow.edges
    assert ("tools_test_agent", "resolver") in workflow.edges
