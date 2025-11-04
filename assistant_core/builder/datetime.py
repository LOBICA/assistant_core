"""This builder adds a node that include date and time to the prompt."""

import datetime
from zoneinfo import ZoneInfo

from assistant_core.builder import BaseBuilder
from assistant_core.nodes import PromptNode

UTC = ZoneInfo("UTC")


def get_weekday(TZ: ZoneInfo) -> str:
    """Return the current weekday."""
    return datetime.datetime.now(tz=TZ).strftime("%A")


def get_current_time(TZ: ZoneInfo) -> str:
    """Return the current time in ISO format."""
    return datetime.datetime.now(tz=TZ).isoformat()


def get_current_date_prompt(TZ: ZoneInfo) -> str:
    """Return the current date prompt."""
    return (
        f"CONTEXT: Today is {get_weekday(TZ)} and the time is {get_current_time(TZ)}.\n"
        "This is for internal use only. Do not provide date or time unless asked."
    )


class DateTimeNode(PromptNode):
    """Includes a prompt with the current date and time."""

    def __init__(self, TZ: ZoneInfo = UTC, *args, **kwargs):
        """Initialize the date and time node."""
        super().__init__(
            name="date_time_node",
            prompt=get_current_date_prompt(TZ),
            *args,
            **kwargs,
        )


class DateTimeBuilder(BaseBuilder):
    """Builder for the date and time node."""

    def __init__(self, TZ: ZoneInfo = UTC):
        """Initialize the builder."""
        super().__init__()
        self.TZ = TZ

    def build(self, context):
        """Build the date and time node."""
        date_time_node = DateTimeNode(TZ=self.TZ)

        context.graph_builder.add_node(
            date_time_node.name,
            date_time_node,
        )

        context.entrypoint = date_time_node.name
