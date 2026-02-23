from execution.orchestrator import ExecutionOrchestrator


def test_approved_for_live_defaults_false():
    orch = ExecutionOrchestrator(config={})
    assert orch.approved_for_live is False
