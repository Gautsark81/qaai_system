# modules/strategy_tournament/strategy_adapter.py

from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy.factory import StrategyFactory


class StrategyAdapter:
    """
    Converts StrategyDNA into an executable strategy instance
    compatible with the existing backtest engine.
    """

    def __init__(self, dna: StrategyDNA):
        self.dna = dna

    def build(self):
        """
        Build a strategy using StrategyFactory.
        Strategy name is derived from DNA fingerprint.
        """
        strategy_type = self._resolve_strategy_type()
        params = self._build_params()

        return StrategyFactory.from_config(
            {
                "type": strategy_type,
                "strategy_id": self.dna.fingerprint(),
                "params": params,
            }
        )

    # ------------------------------------------------------------------

    def _resolve_strategy_type(self) -> str:
        """
        Maps DNA entry + structure → base strategy class.
        This mapping is intentionally simple & deterministic.
        """
        entry = self.dna.entry.value

        if entry in ("breakout", "continuation"):
            return "MomentumStrategy"
        if entry in ("fade", "reversion", "failed_breakout"):
            return "MeanReversionStrategy"

        raise ValueError(f"No strategy mapping for entry={entry}")

    def _build_params(self) -> dict:
        """
        Translate DNA axes into strategy parameters.
        NO tuning. NO optimization.
        """
        params = {
            "size": 1,
        }

        # Simple deterministic mapping
        if self.dna.regime.value == "high_vol":
            params["size"] = 1
        elif self.dna.regime.value == "low_vol":
            params["size"] = 2

        if self.dna.entry.value == "breakout":
            params.update({"fast": 5, "slow": 20})
        else:
            params.update({"window": 20, "z_entry": 0.5})

        return params
