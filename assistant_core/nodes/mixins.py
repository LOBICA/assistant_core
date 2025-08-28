"""Mixins that add additional functionality to nodes in the graph."""

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langgraph.graph import END

_logger = logging.getLogger(__name__)


class UsesModel:
    """Mixin class for nodes that use an LLM model."""

    def __init__(
        self,
        *args,
        model: BaseChatModel,
        tools: list = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if model is None:
            raise ValueError("Model must be provided.")
        self._base_model = model
        self.model = model
        self.tools = tools or []
        if tools:
            self.model = self.model.bind_tools(tools)

    def rebind_tools(self, tools: list):
        """Rebind tools to the model."""
        self.tools = tools
        self.model = self._base_model.bind_tools(tools)


class UsesJsonModel(UsesModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_model: BaseChatModel = self.model.with_structured_output(
            method="json_mode"
        )


class UsesSystemMessage:
    """Mixin class for nodes that return system messages."""

    def system_messages(self, messages: list[str]) -> list[SystemMessage]:
        """Convert a list of strings to system messages."""
        return [SystemMessage(message) for message in messages]

    def system_message(self, message: str) -> SystemMessage:
        """Convert a string to a system message."""
        return SystemMessage(message)


class IncludeQuestionNode:
    def __init__(
        self,
        *args,
        question_node: str = "question_node",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.question_node = question_node


class IncludeNextNode:
    def __init__(
        self,
        *args,
        next_node: str = END,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.next_node = next_node


class IncludeEndNode:
    def __init__(
        self,
        *args,
        end_node: str = END,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.end_node = end_node


class IncludeErrorNode:
    def __init__(
        self,
        *args,
        error_node: str = END,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.error_node = error_node
