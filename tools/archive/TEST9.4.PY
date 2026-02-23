from core.paper.paper_executor import PaperExecutor

executor = PaperExecutor()

try:
    executor.execute(
        strategy_id="STRAT_TEST",
        symbol="RELIANCE",
        side="BUY",
        qty=10,
        price=None,  # INVALID
    )
except Exception as e:
    print("PASS:", e)
