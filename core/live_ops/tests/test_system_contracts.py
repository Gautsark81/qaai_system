from core.live_ops.system import SystemRunContext
from core.live_ops.enums import TradingMode


def test_system_run_context_contract():
    ctx = SystemRunContext(
        run_id="dry_run_001",
        trading_mode=TradingMode.PAPER,
        capital=1_000_000,
        max_positions=5,
    )

    assert ctx.run_id
    assert ctx.trading_mode == TradingMode.PAPER
    assert ctx.capital > 0
    assert ctx.max_positions > 0
