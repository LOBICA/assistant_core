from unittest.mock import patch

import pytest

from assistant_core.models import GPT_5, GPT_5_MINI, GPT_5_NANO, load_openai_model


@patch("assistant_core.models.OPENAI_API_KEY", None)
def test_api_key_not_set():
    with pytest.raises(ValueError):
        load_openai_model()


@patch("assistant_core.models.OPENAI_API_KEY", "test_key")
def test_default_model():
    model = load_openai_model()
    assert model is not None


@patch("assistant_core.models.OPENAI_API_KEY", "test_key")
def test_gpt_5_nano_model():
    model = load_openai_model(GPT_5_NANO)
    assert model is not None


@patch("assistant_core.models.OPENAI_API_KEY", "test_key")
def test_gpt_5_mini_model():
    model = load_openai_model(GPT_5_MINI)
    assert model is not None


@patch("assistant_core.models.OPENAI_API_KEY", "test_key")
def test_gpt_5_model():
    model = load_openai_model(GPT_5)
    assert model is not None
