from abc import ABC, abstractmethod

from langgraph.graph import StateGraph

from .context import BuilderContext


class BaseBuilder(ABC):
    @abstractmethod
    def build(self, context: BuilderContext):
        raise NotImplementedError("Subclasses must implement this method")


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

        # Add the graph entrypoint
        context.graph_builder.set_entry_point(context.entrypoint)

        return context.graph_builder
