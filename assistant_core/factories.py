from abc import ABC, abstractmethod
from typing import TypedDict

from langgraph.graph import StateGraph

from assistant_core.models import load_openai_model
from assistant_core.nodes import AgentNode, ResolverNode


class BaseAgentFactory(ABC):
    class FactoryConfig(TypedDict):
        OPENAI_API_KEY: str

    def __init__(self, config: FactoryConfig):
        super().__init__()
        self._model = None
        self.config = config

    @property
    def model(self):
        """
        Get the model instance.
        If not already created, it will create one using the factory method.
        """
        if self._model is None:
            self._model = self.create_model()
        return self._model

    @abstractmethod
    def create_graph_builder(self) -> StateGraph:
        """
        Create a graph builder instance.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def create_agent_node(self) -> AgentNode:
        """
        Create an agent instance.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def create_model(self):
        """
        Create a model instance.
        """
        return load_openai_model(openai_api_key=self.config.get("OPENAI_API_KEY"))

    def create_resolver_node(self) -> ResolverNode:
        """
        Create a resolver instance.
        """
        return ResolverNode(name="resolver")

    def create_base_tools(self) -> list:
        """
        Create a set of base tools for the agent.
        """
        return []
