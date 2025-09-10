from unittest.mock import patch

import pytest

from assistant_core.builder import BuilderError
from assistant_core.builder.tavily import TavilyBuilder, get_tavily_tool


class DummyTavily:
    def __init__(self, max_results=None, tavily_api_key=None, **kwargs):
        self.max_results = max_results
        self.api_key = tavily_api_key


def test_get_tavily_tool_creates():
    # Patch the TavilySearch class used by get_tavily_tool
    with patch("assistant_core.builder.tavily.TavilySearch", DummyTavily):
        tool = get_tavily_tool(tavily_api_key="sk-test", max_results=3)
        assert isinstance(tool, DummyTavily)
        assert tool.api_key == "sk-test"
        assert tool.max_results == 3


def test_builder_appends_tool(builder_context):
    # Replace the get_tavily_tool helper to return a sentinel object
    sentinel = object()
    with patch("assistant_core.builder.tavily.get_tavily_tool", lambda **kw: sentinel):
        ctx = builder_context
        builder = TavilyBuilder(tavily_api_key="sk-ok")
        builder.build(ctx)

    assert sentinel in ctx.tools


def test_builder_raises_when_no_key(builder_context):
    # If no API key is configured (neither env nor explicit), builder should raise
    # Patch the module-level TAVILY_API_KEY to None for this test.
    with patch("assistant_core.builder.tavily.TAVILY_API_KEY", None):
        ctx = builder_context
        builder = TavilyBuilder(tavily_api_key=None)
        with pytest.raises(BuilderError):
            builder.build(ctx)
