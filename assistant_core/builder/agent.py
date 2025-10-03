from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .base import BaseBuilder, BaseDirector
from .context import BuilderContext


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


class SingleAgentDirector(BaseDirector):
    def make(self, context: BuilderContext) -> StateGraph:
        """
        Execute the build process for a single agent.
        """
        super().make(context)
        AgentBuilder().build(context)

        return context.graph_builder


SingleAgent = SingleAgentDirector
