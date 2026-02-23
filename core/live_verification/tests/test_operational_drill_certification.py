import pytest

from core.live_trading.engine import run_live_trading_loop
from core.live_verification.integration import LiveVerificationEngine
from modules.operator_dashboard.state_assembler import DashboardStateAssembler


class DummySignalEngine:
    strategy_id = "DRILL_STRATEGY"

    def process(self):
        pass


class DummyOrderManager:
    pass


class DummyBroker:
    def submit(self, order):
        return "dummy-order-id"


class DummyLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def exception(self, *args, **kwargs): pass


def test_operational_drill_produces_valid_live_proof():
    verifier = LiveVerificationEngine.global_instance()
    verifier.reset()  # ensure clean state

    run_live_trading_loop(
        signal_engine=DummySignalEngine(),
        order_manager=DummyOrderManager(),
        safe_broker=DummyBroker(),
        logger=DummyLogger(),
        max_iterations=3,
        loop_sleep_seconds=0,
    )

    artifacts = verifier.list_artifacts()

    # 1️⃣ Artifacts created
    assert len(artifacts) > 0

    # 2️⃣ Authority validated for all
    assert all(a.authority_validated for a in artifacts)

    # 3️⃣ Chain hash continuity (no duplicates)
    hashes = [a.chain_hash for a in artifacts]
    assert len(set(hashes)) == len(hashes)

    # 4️⃣ Dashboard reflects proof state
    snapshot = DashboardStateAssembler().assemble_full()
    live_proof = snapshot.explainability["live_proof"]

    assert live_proof["total_artifacts"] == len(artifacts)
    assert live_proof["authority_all_valid"] is True