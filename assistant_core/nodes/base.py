"""Define node objects for graph"""

import abc

from langchain_core.runnables import RunnableConfig


class BaseNode(abc.ABC):
    """Base class for nodes in the graph.

    Nodes should be callable objects that will be added to a graph.
    """

    def __init__(self, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    @abc.abstractmethod
    async def __call__(self, state: dict, config: RunnableConfig) -> dict:
        """Executes the node."""
        raise NotImplementedError("Subclasses must implement this method.")
