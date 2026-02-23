"""
Wrapper entrypoint for the live market feed when containerized.
It imports your Live_market_New.run() function and runs it.
"""

import os
import sys
from importlib import import_module

# ensure repo root on path
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# Attempt to import the run() function from your Live market module
try:
    # location: top-level Live_market_New.py -> module name 'Live_market_New'
    lm = import_module("Live_market_New")
    run = getattr(lm, "run", None)
    if run is None:
        raise RuntimeError("Live_market_New.run() not found")
except Exception as e:
    print("Failed to load Live_market_New:", e)
    raise

if __name__ == "__main__":
    run()
