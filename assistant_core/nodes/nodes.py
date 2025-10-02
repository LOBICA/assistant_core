import logging
import warnings

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, MessagesState
from langgraph.types import Command, interrupt

from ..state import NextProcessState, QuestionState
from .base import BaseNode
from .mixins import IncludeNextNode, UsesModel, UsesSystemMessage

_logger = logging.getLogger(__name__)


class AgentNode(BaseNode, UsesModel):
    """Node for agent execution.

    This node is used to interact with the user.
    """

    def __init__(
        self, prompts: list[str] = None, use_responses_api=False, *args, **kwargs
    ):
        """Initialize the agent node with a prompt."""
        super().__init__(*args, **kwargs)
        prompts = prompts or []
        self.prompts = [SystemMessage(prompt) for prompt in prompts]
        self.use_responses_api = use_responses_api

    def _get_messages(self, state: MessagesState) -> list[BaseMessage]:
        """Get the messages to be sent to the model."""
        last_response_id = state.get("last_response_id")

        if self.use_responses_api is False or last_response_id is None:
            # include initial prompts for first messages
            # or if not using Responses API
            return self.prompts + state["messages"]

        new_messages = []
        for message in reversed(state["messages"]):
            if message.response_metadata.get("id") == last_response_id:
                break
            new_messages.append(message)

        new_messages.reverse()

        # only return messages after last response
        return new_messages

    async def __call__(self, state: dict, config: RunnableConfig) -> dict:
        """Execute the agent logic.

        Get a response from the model based on the provided prompts.
        """
        messages = self._get_messages(state)

        if self.use_responses_api:
            response = await self.model.ainvoke(
                messages,
                previous_response_id=state.get("last_response_id"),
                config=config,
            )
        else:
            response = await self.model.ainvoke(messages, config=config)

        return {"messages": [response]}


class PromptNode(BaseNode, UsesSystemMessage):
    """Node that adds a prompt to the state."""

    def __init__(self, prompt: str = "", state_values: dict = None, *args, **kwargs):
        if "model" in kwargs:
            _logger.warning(
                "PromptNode usually does not use a model, but a model was provided. "
            )
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.state_values = state_values or {}

    async def __call__(self, state: dict, config: RunnableConfig) -> dict:
        if self.state_values:
            data = {}
            for key, value in self.state_values.items():
                data[key] = state.get(value, "")
            prompt = self.prompt.format(**data)
        else:
            prompt = self.prompt
        return {"messages": self.system_messages([prompt])}


class DataNode(BaseNode, UsesSystemMessage):
    """Node that parses data from the state."""


class ProcessDataNode(BaseNode, UsesModel, UsesSystemMessage):
    """Node that processes data from the state using a model."""


class QuestionNode(BaseNode):
    async def __call__(
        self, state: QuestionState, config: RunnableConfig
    ) -> QuestionState:
        user_input = interrupt({"question": state["question"]})
        if isinstance(user_input, dict) and "answer" in user_input:
            answer = user_input["answer"]
        else:
            warnings.warn(
                "User input should be a dict with an 'answer' key. "
                "String format is deprecated and will be removed in a future version.",
                DeprecationWarning,
            )
            answer = user_input
        return {
            "question": state["question"],
            "answer": answer,
        }


class ResolverNode(BaseNode, IncludeNextNode):
    async def __call__(
        self, state: NextProcessState, config: RunnableConfig
    ) -> Command:
        next_step = state.get("next")
        if next_step == END:
            return Command(update={"next": None})
        if next_step is None:
            return Command(goto=self.next_node, update={"next": None})

        return Command(goto=next_step, update={"next": None})
