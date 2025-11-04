from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .base import BaseBuilder, BaseDirector
from .context import BuilderContext, MultiAgentContext


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


class MultiAgentDirector(BaseDirector):
    def make(self, context: MultiAgentContext) -> StateGraph:
        """
        Execute the build process for multiple agents.
        """
        for builder in self.builders:
            builder.build(context)

        if "default" not in context.entrypoint_mapping:
            context.entrypoint_mapping["default"] = context.entrypoint

        # Use conditional entry depending on state["active_agent"]
        context.graph_builder.set_conditional_entry_point(
            context.conditional_entrypoint_factory()
        )
        AgentBuilder().build(context)

        return context.graph_builder


MultiAgent = MultiAgentDirector
