from unittest import mock

import pytest
from langchain_core.language_models.chat_models import BaseChatModel


@pytest.fixture
def mock_model():
    return mock.Mock(spec=BaseChatModel)


@pytest.fixture
def mock_config():
    return {"configurable": {"thread_id": "test"}}
