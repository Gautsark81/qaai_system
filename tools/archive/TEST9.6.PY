from core.capital.allocator import CapitalAllocator

allocator = CapitalAllocator(max_capital=1000)

ml_signal = {
    "confidence": 0.99,
    "order_value": 10_000_000,  # ILLEGAL
}

try:
    allocator.allocate(order_value=ml_signal["order_value"])
except Exception as e:
    print("PASS:", e)
