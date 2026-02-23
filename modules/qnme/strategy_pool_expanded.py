# modules/qnme/strategy_pool_expanded.py
"""
Expands StrategyPool by auto-generating 30 strategy stubs and registering them
with the project's StrategyFactory. This file creates safe, testable stubs that
expose the interface expected by StrategyPool and StrategyFactory.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Attempt to import your existing StrategyFactory / Strategy base.
try:
    from modules.strategy.factory import StrategyFactory
    from modules.strategy.base import Strategy as RealStrategyBase, Signal as RealSignalClass
    _REAL_FACTORY = True
except Exception:
    _REAL_FACTORY = False
    RealStrategyBase = None
    RealSignalClass = None

# Always provide a StrategyStub and Signal stub in this module so configs can use
# module:ClassName import form (works whether or not real factory exists).
class StrategyStub:
    """
    Lightweight strategy stub that mimics the minimal Strategy interface used by StrategyPool.
    This class is intentionally simple and safe for unit tests.
    """
    def __init__(self, strategy_id: str, params: Dict[str, Any] = None):
        self.strategy_id = strategy_id
        self.params = params or {}
        self.mode = "default"

    def set_mode(self, mode: str):
        self.mode = mode

    def on_tick(self, tick, genome, regime):
        """
        Simple deterministic stub:
        - Emits a BUY signal if last digit of price is even, else no signal.
        - Attach a basic score and meta.
        """
        price = tick.get("price", 0)
        try:
            even = int(price) % 2 == 0
        except Exception:
            even = False
        if even:
            return [SignalStub(self.strategy_id, tick.get("symbol"), "BUY", 1.0, score=0.5, meta={"mode": self.mode})]
        return []

class SignalStub:
    def __init__(self, strategy_id, symbol, side, size, score=0.5, meta=None):
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.side = side
        self.size = size
        self.score = score
        self.meta = meta or {}

# Provide convenient aliases so StrategyFactory can instantiate this class via module:ClassName
Strategy = StrategyStub
Signal = SignalStub

# List of 30 advanced strategy names
STRATEGY_TEMPLATES = [
    "DeltaImbalanceScalper",
    "KeltnerCompressionSmasher",
    "GammaExposureStrategy",
    "MarketMakerShadowFollow",
    "AdaptiveBiasStrategy",
    "SmartMoneyTrapStrategy",
    "VWAPReversion",
    "MicrostructureScalper",
    "OrderFlowMomentum",
    "LiquidityGrabBreakout",
    "TrendExhaustionDetector",
    "MomentumContinuation",
    "MeanReversionProfile",
    "VolatilitySpikeArb",
    "GammaScalp",
    "FlowWeightedBias",
    "DeltaGammaHedger",
    "OptionsSkewPlay",
    "ImbalanceSniper",
    "RangeShiftTrader",
    "FractalMeanReverter",
    "LiquidationWatch",
    "AdaptiveMarketMaker",
    "MicroBurstHunter",
    "PriceActionSieve",
    "SpreadArbitrage",
    "TimeOfDayEdge",
    "CrossAssetBias",
    "MacroAligner",
    "NoiseSieve"
]

def generate_default_config(strategy_name: str, idx: int) -> Dict[str, Any]:
    """
    Return a config suitable for StrategyFactory.from_config.

    Use module:Class style so the factory imports this module's Strategy class
    (StrategyStub). That makes the config resolvable regardless of the project's
    registered strategy registry.
    """
    return {
        # instruct the factory to import Strategy from this module
        "type": f"{__name__}:Strategy",
        "strategy_id": f"{strategy_name}-{idx}",
        "params": {"seed_param": idx, "risk_factor": 0.01 + (idx % 5) * 0.01},
        "modes": ["default", "aggressive", "conservative"],
        "supported_regimes": None
    }

def register_all(pool):
    """
    Given a StrategyPool instance, populate it with 30 strategy instances.
    Uses StrategyFactory.from_config which supports module:Class style.
    """
    for idx, name in enumerate(STRATEGY_TEMPLATES):
        cfg = generate_default_config(name, idx)
        try:
            pool.add_from_config(cfg)
            logger.info("Registered strategy %s", cfg["strategy_id"])
        except Exception:
            # If your project's StrategyFactory raises, fallback to direct instantiation
            # using our local Strategy class.
            try:
                inst = Strategy(cfg["strategy_id"], cfg.get("params"))
                pool.registry[cfg["strategy_id"]] = type("Desc", (), {"name": cfg["strategy_id"], "instance": inst, "supported_modes": cfg.get("modes"), "supported_regimes": cfg.get("supported_regimes")})
                logger.info("Fallback registered %s directly", cfg["strategy_id"])
            except Exception:
                logger.exception("Failed to register strategy %s", cfg["strategy_id"])
