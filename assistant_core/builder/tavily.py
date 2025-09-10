"""Example Tavily builder.

This module provides a minimal example Builder that creates a
`TavilySearch` tool and appends it to the provided builder
`BuilderContext`'s `tools` list.

Important notes:
- This file is an intentionally small example to help contributors
    understand the builder pattern used in this project. Keep behaviour
    simple here so it's easy to copy and extend.
- The builder will use the `TAVILY_API_KEY` value from
    `assistant_core.settings` if no explicit API key is provided at
    construction time.
- The module depends on the `langchain_tavily` package. Callers may
    wrap or mock `TavilySearch` in tests to avoid requiring the real
    dependency.

Contract (inputs/outputs):
- get_tavily_tool(tavily_api_key: str, max_results: int, **kwargs) -> TavilySearch
- TavilyBuilder.build(context: BuilderContext) -> None
    - side-effect: appends the created tool to `context.tools`

Error handling / edge cases:
- If no API key is available the builder raises ``BuilderError``. This
    makes the behavior explicit for callers who expect the tool to be
    present (the caller can catch the error) instead of silently
    continuing.
"""

from langchain_tavily import TavilySearch

from assistant_core.builder import BaseBuilder, BuilderContext, BuilderError
from assistant_core.settings import TAVILY_API_KEY


def get_tavily_tool(*, tavily_api_key, max_results=2, **kwargs):
    """Create and return a TavilySearch tool instance.

    This is a tiny convenience wrapper around `TavilySearch`. It exists
    to make the builder code here readable in examples and tests.

    Parameters:
    - tavily_api_key: API key string for Tavily (required by TavilySearch)
    - max_results: maximum number of results the tool should return
    - **kwargs: passed through to TavilySearch

    Returns:
    - TavilySearch instance
    """
    return TavilySearch(
        max_results=max_results, tavily_api_key=tavily_api_key, **kwargs
    )


class TavilyBuilder(BaseBuilder):
    """Example builder that adds a Tavily search tool to the context.

    This builder is intentionally minimal and designed as an example for
    contributors. It demonstrates the builder contract: accept
    configuration at construction time, and register tools on the
    provided `BuilderContext` during `build`.
    """

    def __init__(self, tavily_api_key: str | None = None, **kwargs):
        super().__init__()
        # prefer explicit key passed to constructor; fall back to settings
        self.tavily_api_key = tavily_api_key or TAVILY_API_KEY
        # additional keyword arguments forwarded to TavilySearch
        self.kwargs = kwargs

    def build(self, context: BuilderContext) -> None:
        """Build and register the Tavily tool on the provided context.

        If the API key is not set the function logs a warning and returns
        without modifying the context. This keeps the example safe to run
        in environments where credentials are not available.
        """

        if self.tavily_api_key is None:
            raise BuilderError("Tavily API key is required to build Tavily tool.")

        tavily_tool = get_tavily_tool(tavily_api_key=self.tavily_api_key, **self.kwargs)
        context.tools.append(tavily_tool)
