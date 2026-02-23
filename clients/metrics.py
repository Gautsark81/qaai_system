# clients/metrics.py
from prometheus_client import Counter, Gauge

# tick metrics
ticks_received = Counter("amats_ticks_received_total", "Total ticks received by dispatcher")
ticks_dropped = Counter("amats_ticks_dropped_total", "Total ticks dropped by dispatcher")

# order metrics
orders_placed = Counter("amats_orders_placed_total", "Total orders placed via OrderManager")
orders_failed = Counter("amats_orders_failed_total", "Total orders failed via OrderManager")

# reconciler metrics
reconciler_runs = Counter("amats_reconciler_runs_total", "Total reconciler cycles run")

# queue gauge (updated by dispatcher optionally)
# For simplicity create a general gauge; per-instance queues can be implemented as needed
dispatcher_queue_size = Gauge("amats_dispatcher_queue_size", "Current dispatcher total queued ticks")
