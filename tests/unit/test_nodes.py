from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command

from assistant_core.nodes import (
    AgentNode,
    DataNode,
    ProcessDataNode,
    PromptNode,
    QuestionNode,
    ResolverNode,
)
from assistant_core.nodes.mixins import (
    IncludeEndNode,
    IncludeErrorNode,
    IncludeNextNode,
    IncludeQuestionNode,
)
from assistant_core.state import NextProcessState, QuestionState


async def test_agent_node(mock_model, mock_config):
    mock_model.ainvoke.return_value = "Test response"

    agent_node = AgentNode(
        name="test_agent",
        model=mock_model,
        prompts=["You are a helpful assistant."],
    )

    response = await agent_node(
        {
            "messages": ["This is a test"],
        },
        config=mock_config,
    )

    mock_model.ainvoke.assert_awaited_once_with(
        agent_node.prompts + ["This is a test"],
        config=mock_config,
    )

    assert response["messages"][-1] == "Test response"


async def test_agent_node_with_last_response_id(mock_model, mock_config):
    mock_model.ainvoke.return_value = "Test response with last_response_id"

    agent_node = AgentNode(
        name="test_agent",
        model=mock_model,
        prompts=["You are a helpful assistant."],
        use_responses_api=True,
    )

    messages = [
        HumanMessage("This is a test"),
        AIMessage("Test response", response_metadata={"id": "msg_1"}),
        HumanMessage("Another message"),
    ]

    response = await agent_node(
        {
            "messages": messages,
            "last_response_id": None,
        },
        config=mock_config,
    )

    mock_model.ainvoke.assert_awaited_once_with(
        [SystemMessage("You are a helpful assistant.")] + messages,
        previous_response_id=None,
        config=mock_config,
    )

    mock_model.ainvoke.reset_mock()

    response = await agent_node(
        {
            "messages": messages,
            "last_response_id": "msg_1",
        },
        config=mock_config,
    )

    mock_model.ainvoke.assert_awaited_once_with(
        [HumanMessage("Another message")],
        previous_response_id="msg_1",
        config=mock_config,
    )

    assert response["messages"][-1] == "Test response with last_response_id"


async def test_prompt_node(mock_config):
    prompt_node = PromptNode(name="test_prompt", prompt="You are a helpful assistant.")

    response = await prompt_node({}, config=mock_config)
    assert response["messages"][-1] == SystemMessage("You are a helpful assistant.")


async def test_abstract_data_nodes(mock_model):
    # Data nodes are abstract and have to be inherited

    with pytest.raises(TypeError):
        DataNode(
            name="test_data",
        )

    with pytest.raises(TypeError):
        ProcessDataNode(
            name="test_process_data",
            model=mock_model,
        )


async def test_data_node_demo(mock_config):
    class DemoDataNode(DataNode):
        async def __call__(self, state: dict, config) -> dict:
            return "ok"

    demo_data_node = DemoDataNode(
        name="test_demo_data",
    )

    response = await demo_data_node({}, config=mock_config)
    assert response == "ok"


async def test_process_data_node_demo(mock_model, mock_config):
    class DemoProcessDataNode(ProcessDataNode):
        async def __call__(self, state: dict, config) -> dict:
            assert self.model == mock_model
            return "ok"

    demo_process_data_node = DemoProcessDataNode(
        name="test_demo_process_data",
        model=mock_model,
    )

    response = await demo_process_data_node({}, config=mock_config)
    assert response == "ok"


async def test_question_node(mock_config):
    state = QuestionState(question="Should we proceed?")
    question_node = QuestionNode(
        name="test_question",
    )

    with patch(
        "assistant_core.nodes.nodes.interrupt", return_value={"answer": "Yes"}
    ) as mock_interrupt:
        response = await question_node(state, config=mock_config)
        mock_interrupt.assert_called_once_with({"question": "Should we proceed?"})

    assert response["answer"] == "Yes"


async def test_resolver_node(mock_config):
    state = NextProcessState(next="next_step")
    resolver_node = ResolverNode(
        name="test_resolver",
    )

    assert state.get("next") == "next_step"

    response = await resolver_node(state, config=mock_config)
    assert isinstance(response, Command)
    assert response.goto == "next_step"
    assert response.update == {"next": None}


def test_extra_nodes_mixin():
    class TestNode(
        DataNode, IncludeNextNode, IncludeEndNode, IncludeErrorNode, IncludeQuestionNode
    ):
        def __call__(self, state, config):
            return "ok"

    test_node = TestNode(
        name="test_extra_nodes",
        next_node="next_node",
        end_node="end_node",
        error_node="error_node",
        question_node="question_node",
    )
    assert test_node.next_node == "next_node"
    assert test_node.end_node == "end_node"
    assert test_node.error_node == "error_node"
    assert test_node.question_node == "question_node"
