import warnings
from typing import Callable, Self, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import MessagesState, StateGraph

from assistant_core.models import load_default_model
from assistant_core.nodes import AgentNode, ResolverNode

AgentFactory = Callable[[BaseChatModel], AgentNode] | None
GraphFactory = Callable[[], StateGraph] | None
ModelFactory = Callable[["ContextFactory.FactoryConfig"], BaseChatModel] | None
ResolverFactory = Callable[[], ResolverNode] | None
BaseToolsFactory = Callable[[], list[BaseTool]] | None


class ContextFactory:
    class FactoryConfig(TypedDict):
        OPENAI_API_KEY: str

    def __init__(
        self,
        config: FactoryConfig,
        *,
        agent_factory: AgentFactory = None,
        graph_factory: GraphFactory = None,
        model_factory: ModelFactory = None,
        resolver_factory: ResolverFactory = None,
        base_tools_factory: BaseToolsFactory = None,
    ):
        self._model: BaseChatModel | None = None
        self.config = config
        self._agent_factory = agent_factory
        self._graph_factory = graph_factory
        self._model_factory = model_factory
        self._resolver_factory = resolver_factory
        self._base_tools_factory = base_tools_factory

    def clone(
        self,
        *,
        agent_factory: AgentFactory = None,
        graph_factory: GraphFactory = None,
        model_factory: ModelFactory = None,
        resolver_factory: ResolverFactory = None,
        base_tools_factory: BaseToolsFactory = None,
    ) -> Self:

        agent_factory = agent_factory or self._agent_factory
        graph_factory = graph_factory or self._graph_factory
        model_factory = model_factory or self._model_factory
        resolver_factory = resolver_factory or self._resolver_factory
        base_tools_factory = base_tools_factory or self._base_tools_factory

        new_factory = self.__class__(
            self.config,
            agent_factory=agent_factory,
            graph_factory=graph_factory,
            model_factory=model_factory,
            resolver_factory=resolver_factory,
            base_tools_factory=base_tools_factory,
        )

        return new_factory

    @property
    def model(self) -> BaseChatModel:
        """
        Get the model instance.
        If not already created, it will create one using the factory method.
        """
        if self._model is None:
            self._model = self.create_model()
        return self._model

    def create_graph_builder(self) -> StateGraph:
        """
        Create a graph builder instance.
        """
        if self._graph_factory:
            return self._graph_factory()

        return StateGraph(MessagesState)

    def create_agent_node(self) -> AgentNode:
        """
        Create an agent instance.
        """
        if self._agent_factory:
            return self._agent_factory(self.model)

        raise NotImplementedError("Agent factory must be provided")

    def create_model(self) -> BaseChatModel:
        """
        Create a model instance.
        """
        if self._model_factory:
            return self._model_factory(self.config)

        return load_default_model(openai_api_key=self.config["OPENAI_API_KEY"])

    def create_resolver_node(self) -> ResolverNode:
        """
        Create a resolver instance.
        """
        if self._resolver_factory:
            return self._resolver_factory()

        return ResolverNode(name="resolver")

    def create_base_tools(self) -> list[BaseTool]:
        """
        Create a set of base tools for the agent.
        """
        if self._base_tools_factory:
            return self._base_tools_factory()

        return []


class BaseAgentFactory(ContextFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            "BaseAgentFactory is deprecated, use ContextFactory instead.",
            DeprecationWarning,
        )
