from types import NoneType
from typing import Annotated, get_args, get_type_hints
from unittest.mock import Mock

from langgraph.graph import MessagesState

from assistant_core.state import NextProcessState, QuestionState


def assign_to_state(State, values):
    """Emulate graph state assignment"""
    state = State()
    hints = get_type_hints(State, include_extras=True)
    for key, value in values.items():
        annot = hints.get(key)
        reducer = get_args(annot)[1]
        if reducer is NoneType:
            state[key] = value
        else:
            state[key] = reducer(state.get(key), value)
    return state


def test_reducer_call():
    """Test that our state assigment is working as expected"""
    reducer = Mock()
    reducer.return_value = "test2"

    class TestState(MessagesState):
        attribute: Annotated[str, reducer] = None

    state = assign_to_state(TestState, {"attribute": "test1"})

    assert state["attribute"] == "test2"
    reducer.assert_called_once_with(None, "test1")


def test_question_state():
    state = assign_to_state(
        QuestionState, {"question": "How are you?", "answer": "I am fine."}
    )

    assert state["question"] == "How are you?"
    assert state["answer"] == "I am fine."


def test_next_process_state():
    state = assign_to_state(NextProcessState, {"next": "test"})

    assert state["next"] == "test"
