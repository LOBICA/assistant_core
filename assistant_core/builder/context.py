from assistant_core.factories import BaseAgentFactory


class BuilderContext:
    def __init__(self, agent_factory: BaseAgentFactory):
        self.model = agent_factory.model
        self.graph_builder = agent_factory.create_graph_builder()
        self.agent_node = agent_factory.create_agent_node()
        self.resolver_node = agent_factory.create_resolver_node()
        self.tools = agent_factory.create_base_tools()

        self._entrypoint = None

    @property
    def entrypoint(self):
        return self._entrypoint or self.agent_node.name

    @entrypoint.setter
    def entrypoint(self, value: str):
        """Set the entrypoint for the graph.

        The default entrypoint is the agent node, new entrypoints will be added
        in a LIFO queue that finish with the agent node.
        """

        self.graph_builder.add_edge(value, self.entrypoint)
        self._entrypoint = value
