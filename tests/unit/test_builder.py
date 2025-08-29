from assistant_core.builder import SingleAgent


def test_single_agent_build(builder_context):
    agent = SingleAgent()
    workflow = agent.make(builder_context)
    assert workflow is not None

    graph = workflow.compile()
    assert graph is not None
