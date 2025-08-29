from abc import ABC, abstractmethod

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from assistant_core.factories import BaseAgentFactory


class BuilderContext:
    def __init__(self, agent_factory: BaseAgentFactory):
        self.model = agent_factory.model
        self.graph_builder = agent_factory.create_graph_builder()
        self.agent_node = agent_factory.create_agent_node()
        self.resolver_node = agent_factory.create_resolver_node()
        self.tools = agent_factory.create_base_tools()


class BaseBuilder(ABC):
    @abstractmethod
    def build(self, context: BuilderContext):
        raise NotImplementedError("Subclasses must implement this method")


class AgentBuilder(BaseBuilder):
    def build(self, context: BuilderContext) -> None:
        tools_node_name = f"tools_{context.agent_node.name}"

        # Agent Node
        context.agent_node.rebind_tools(context.tools)
        context.graph_builder.add_node(
            context.agent_node.name,
            context.agent_node,
        )
        context.graph_builder.add_conditional_edges(
            context.agent_node.name,
            tools_condition,
            {"tools": tools_node_name, END: END},
        )

        # Tool Node
        context.graph_builder.add_node(
            tools_node_name,
            ToolNode(context.tools),
        )
        context.graph_builder.add_edge(tools_node_name, context.resolver_node.name)

        # Resolver Node
        context.resolver_node.next_node = context.agent_node.name
        context.graph_builder.add_node(
            context.resolver_node.name,
            context.resolver_node,
        )


class BaseDirector(ABC):
    def __init__(self):
        self.builders: list[BaseBuilder] = []

    def add_builder(self, builder: BaseBuilder):
        """
        Add a builder to the director.

        :param builder: An instance of BaseBuilder to be added.
        """
        self.builders.append(builder)

    def make(self, context: BuilderContext) -> StateGraph:
        """
        Execute the build process for all registered builders.
        """
        for builder in self.builders:
            builder.build(context)

        return context.graph_builder


class SingleAgentDirector(BaseDirector):
    def make(self, context: BuilderContext) -> StateGraph:
        """
        Execute the build process for a single agent.
        """
        super().make(context)
        AgentBuilder().build(context)
        context.graph_builder.set_entry_point(context.agent_node.name)

        return context.graph_builder


SingleAgent = SingleAgentDirector
