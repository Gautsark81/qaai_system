# modules/qnme/strategy_pool.py
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
import logging

from modules.strategy.factory import StrategyFactory, register_strategy  # reuse your factory
from modules.strategy.base import Strategy, Signal

logger = logging.getLogger(__name__)

@dataclass
class StrategyDescriptor:
    name: str
    instance: Strategy
    supported_modes: List[str]
    supported_regimes: Optional[List[str]]

class StrategyPool:
    """
    Layer 2: Adaptive Strategy Pool
    - Wraps StrategyFactory to instantiate a pool of strategies
    - Supports per-strategy modes and simple mode switching
    """

    def __init__(self):
        self.registry: Dict[str, StrategyDescriptor] = {}

    def add_from_config(self, cfg: Dict[str, Any]) -> None:
        """
        cfg example:
        {
           "type": "MeanReversionStrategy",
           "strategy_id": "mr1",
           "params": {...},
           "modes": ["default", "aggressive"],
           "supported_regimes": ["low_vol_range", ...]
        }
        """
        inst = StrategyFactory.from_config(cfg)
        desc = StrategyDescriptor(name=cfg["strategy_id"], instance=inst,
                                  supported_modes=cfg.get("modes", ["default"]),
                                  supported_regimes=cfg.get("supported_regimes"))
        self.registry[desc.name] = desc
        logger.info("StrategyPool: added %s", desc.name)

    def list_strategies(self) -> List[str]:
        return list(self.registry.keys())

    def set_mode_for_regime(self, regime: str, mode_map: Dict[str, str]) -> None:
        """
        mode_map: {strategy_id: mode_name}
        Called by MetaController to set modes according to regime.
        """
        for sid, mode in mode_map.items():
            desc = self.registry.get(sid)
            if desc and hasattr(desc.instance, "set_mode"):
                try:
                    desc.instance.set_mode(mode)
                except Exception:
                    logger.exception("Failed to set mode for %s", sid)

    def on_tick_all(self, tick: Dict[str, Any], genome: Dict[str, Any], regime: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Call each strategy's on_tick or generate_signals and return candidate matrix:
        Each element: {"strategy_id", "signal"(Signal), "confidence", "meta"}
        """
        out = []
        for sid, desc in self.registry.items():
            try:
                # support both 'on_tick' and 'generate_signals' style
                inst = desc.instance
                if hasattr(inst, "on_tick"):
                    sigs = inst.on_tick(tick, genome, regime)
                else:
                    sigs = inst.generate_signals(dict(symbol=tick.get("symbol"), price=tick.get("price")))
                for s in sigs:
                    out.append({
                        "strategy_id": sid,
                        "signal": s,
                        "confidence": getattr(s, "score", None) or 0.5,
                        "meta": getattr(s, "meta", None)
                    })
            except Exception:
                logger.exception("strategy %s raised", sid)
        return out
