from typing import Annotated

from langgraph.graph import MessagesState


def replace(old, new):
    return new


class QuestionState(MessagesState):
    question: str | None = None
    answer: str | None = None


class NextProcessState(MessagesState):
    next: Annotated[str | None, replace] = None


class MultiAgentState(MessagesState):
    """State for multi-agent workflows.

    When building graphs with conditional entry points, the value of
    `active_agent` selects which entrypoint to use.
    """

    active_agent: str | None = None
