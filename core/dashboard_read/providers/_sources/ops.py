"""
Dashboard read adapter for operational state.
All ops / infrastructure imports must live here.
"""

def read_ops_metrics():
    from ops.metrics import get_ops_metrics
    return get_ops_metrics()
