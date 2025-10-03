from assistant_core.builder import BaseBuilder, SingleAgent
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
