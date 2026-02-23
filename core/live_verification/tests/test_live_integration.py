from core.live_verification.integration import LiveVerificationEngine


def test_integration_records_artifact():

    engine = LiveVerificationEngine()

    artifact = engine.record(
        strategy_dna="TEST_STRAT",
        capital_decision={"fraction": 0.1},
        risk_verdict={"passed": True},
        execution_intent={"symbol": "NIFTY"},
        router_call_payload={"order_id": "123"},
        mode="SHADOW",
    )

    artifacts = engine.list_artifacts()

    assert len(artifacts) == 1
    assert artifacts[0].authority_validated is True