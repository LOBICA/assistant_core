from unittest import mock

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import MessagesState, StateGraph

from assistant_core.builder import BuilderContext
from assistant_core.factories import BaseAgentFactory
from assistant_core.nodes import AgentNode


@pytest.fixture
def mock_model():
    return mock.Mock(spec=BaseChatModel)


@pytest.fixture
def mock_config():
    return {"configurable": {"thread_id": "test"}}


@pytest.fixture
def agent_node(mock_model):
    return AgentNode(
        name="test_agent",
        model=mock_model,
        prompts=["You are a helpful assistant"],
    )


@pytest.fixture
def factory_config():
    return BaseAgentFactory.FactoryConfig(OPENAI_API_KEY="test_key")


@pytest.fixture
def agent_factory(mock_model, agent_node, factory_config):
    class MockAgentFactory(BaseAgentFactory):
        def create_model(self):
            return mock_model

        def create_graph_builder(self):
            return StateGraph(MessagesState)

        def create_agent_node(self):
            return agent_node

    return MockAgentFactory(factory_config)


@pytest.fixture
def builder_context(agent_factory):
    return BuilderContext(agent_factory=agent_factory)
