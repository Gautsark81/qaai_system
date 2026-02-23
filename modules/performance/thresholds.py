"""
modules/performance/thresholds.py

Hard latency ceilings.
Any regression beyond these FAILS CI.
"""

# milliseconds
MAX_RISK_EVAL_MS = 2.0
MAX_EXECUTION_SUBMIT_MS = 5.0
MAX_PERSIST_WRITE_MS = 3.0
