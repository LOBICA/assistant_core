from assistant_core.factories import BaseAgentFactory


class BuilderContext:
    def __init__(self, agent_factory: BaseAgentFactory):
        self.model = agent_factory.model
        self.graph_builder = agent_factory.create_graph_builder()
        self.agent_node = agent_factory.create_agent_node()
        self.resolver_node = agent_factory.create_resolver_node()
        self.tools = agent_factory.create_base_tools()
