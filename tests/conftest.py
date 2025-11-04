from unittest import mock

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

from assistant_core.builder import BuilderContext, MultiAgentContext
from assistant_core.factories import ContextFactory
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
    return ContextFactory.FactoryConfig(OPENAI_API_KEY="test_key")


@pytest.fixture
def context_factory(mock_model, agent_node, factory_config):
    return ContextFactory(
        factory_config,
        agent_factory=lambda _: agent_node,
        model_factory=lambda _: mock_model,
    )


@pytest.fixture
def builder_context(context_factory):
    return BuilderContext(context_factory=context_factory)


@pytest.fixture
def multi_agent_context(context_factory):
    return MultiAgentContext(context_factory=context_factory)
