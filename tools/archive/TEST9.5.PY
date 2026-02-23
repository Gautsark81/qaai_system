from core.paper.paper_broker import PaperBroker

broker = PaperBroker(simulate_failure=True)

try:
    broker.place_order(
        symbol="RELIANCE",
        side="BUY",
        qty=10,
        price=2500,
    )
except Exception as e:
    print("PASS:", e)
