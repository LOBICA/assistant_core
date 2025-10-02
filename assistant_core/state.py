from typing import Annotated

from langgraph.graph import MessagesState


def replace(old, new):
    return new


class QuestionState(MessagesState):
    question: str | None = None
    answer: str | None = None


class NextProcessState(MessagesState):
    next: Annotated[str | None, replace] = None


class LastResponseState(MessagesState):
    last_response_id: Annotated[str | None, replace] = None
