import warnings
from typing import Self

from assistant_core.factories import (
    AgentFactory,
    BaseToolsFactory,
    ContextFactory,
    GraphFactory,
    ModelFactory,
    ResolverFactory,
)


class BuilderContext:
    def __init__(
        self,
        context_factory: ContextFactory = None,
        agent_factory: ContextFactory = None,
    ):
        if context_factory is None:
            if agent_factory is None:
                raise ValueError("context_factory must be provided")

            warnings.warn(
                "BuilderContext: 'agent_factory' is deprecated, "
                "use 'context_factory' instead",
                DeprecationWarning,
            )
            context_factory = agent_factory

        # Keep a reference to enable cloning/customization
        self._factory = context_factory

        self.model = context_factory.model
        self.graph_builder = context_factory.create_graph_builder()
        self.agent_node = context_factory.create_agent_node()
        self.resolver_node = context_factory.create_resolver_node()
        self.tools = context_factory.create_base_tools()

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

    @classmethod
    def create(
        cls,
        config: ContextFactory.FactoryConfig,
        *,
        agent_factory: AgentFactory,
        graph_factory: GraphFactory = None,
        model_factory: ModelFactory = None,
        resolver_factory: ResolverFactory = None,
        base_tools_factory: BaseToolsFactory = None,
    ) -> Self:
        factory = ContextFactory(
            config,
            agent_factory=agent_factory,
            graph_factory=graph_factory,
            model_factory=model_factory,
            resolver_factory=resolver_factory,
            base_tools_factory=base_tools_factory,
        )
        return cls(factory)

    def clone(
        self,
        *,
        agent_factory: AgentFactory = None,
        graph_factory: GraphFactory = None,
        model_factory: ModelFactory = None,
        resolver_factory: ResolverFactory = None,
        base_tools_factory: BaseToolsFactory = None,
    ) -> Self:

        new_factory = self._factory.clone(
            agent_factory=agent_factory,
            graph_factory=graph_factory,
            model_factory=model_factory,
            resolver_factory=resolver_factory,
            base_tools_factory=base_tools_factory,
        )

        return self.__class__(new_factory)
