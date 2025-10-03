import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from assistant_core.builder.datetime import (
    DateTimeBuilder,
    DateTimeNode,
    get_current_date_prompt,
    get_current_time,
    get_weekday,
)

UTC = ZoneInfo("UTC")


def _make_fixed_dt():
    # Fixed datetime to make outputs deterministic
    return datetime.datetime(2025, 10, 3, 12, 0, 0, tzinfo=UTC)


class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        fixed = _make_fixed_dt()
        if tz is None:
            return fixed
        return fixed.astimezone(tz)


def test_helpers_return_expected_strings():
    # Patch the datetime used in the module to our fixed datetime class
    with mock.patch("assistant_core.builder.datetime.datetime.datetime", FixedDateTime):
        assert get_weekday(UTC) == "Friday"
        assert get_current_time(UTC) == _make_fixed_dt().isoformat()
        expected_prompt = (
            f"Today is Friday and the time is {_make_fixed_dt().isoformat()}."
        )
        assert get_current_date_prompt(UTC) == expected_prompt


def test_datetime_node_has_prompt():
    with mock.patch("assistant_core.builder.datetime.datetime.datetime", FixedDateTime):
        node = DateTimeNode(TZ=UTC)
        assert isinstance(node, DateTimeNode)
        assert "Today is Friday" in node.prompt
        assert _make_fixed_dt().isoformat() in node.prompt


def test_datetime_builder_registers_node_and_entrypoint(builder_context):
    with mock.patch("assistant_core.builder.datetime.datetime.datetime", FixedDateTime):
        builder = DateTimeBuilder(TZ=UTC)
        builder.build(builder_context)

    # node should be registered in graph_builder
    assert "date_time_node" in builder_context.graph_builder.nodes
    node_spec = builder_context.graph_builder.nodes["date_time_node"]
    # StateGraph wraps registered nodes in a spec object with a 'runnable' attribute
    runnable = getattr(node_spec, "runnable", node_spec)
    # langgraph wraps callables in a RunnableCallable; assert the node name
    assert "date_time_node" in repr(runnable)

    # entrypoint should be set to the new node and an edge should have been created
    assert builder_context.entrypoint == "date_time_node"
    assert ("date_time_node", "test_agent") in builder_context.graph_builder.edges
