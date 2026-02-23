from core.capital.allocator import CapitalAllocator

allocator = CapitalAllocator(max_capital=1000)

# This must FAIL
allocator.allocate(order_value=5000)
