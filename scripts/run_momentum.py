import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strategies.momentum import MomentumStrategy
from strategies.registry import get_deps

deps = get_deps()
strat = MomentumStrategy(deps)

signals = strat.generate_signals(["AAPL", "MSFT", "RELIANCE.NS"])
print(signals)
