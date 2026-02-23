# core/strategy_factory/health/contracts.py

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StrategyHealthSnapshot:
    """
    Immutable snapshot of strategy health.

    Design rules:
    - Read-only
    - Deterministic
    - Serializable
    - Builder-compatible (C1.1)
    - Telemetry-compatible (C1.3+)
    """

    # --------------------------------------------------
    # 🆔 Identity (optional at build time)
    # --------------------------------------------------
    strategy_id: Optional[str] = None

    # --------------------------------------------------
    # 📊 Core Component Scores (C1.1)
    # --------------------------------------------------
    performance_score: Optional[float] = None
    risk_score: Optional[float] = None
    stability_score: Optional[float] = None

    # --------------------------------------------------
    # 🧠 Strategy Success Ratio
    # --------------------------------------------------
    ssr: float = 0.0
    ssr_components: Dict[str, float] = None

    # --------------------------------------------------
    # 📈 Performance Telemetry (C1.3+)
    # --------------------------------------------------
    total_trades: Optional[int] = None
    win_rate: Optional[float] = None
    expectancy: Optional[float] = None
    drawdown: Optional[float] = None

    # --------------------------------------------------
    # 🧯 Stability Telemetry (C1.3+)
    # --------------------------------------------------
    volatility: Optional[float] = None
    max_consecutive_losses: Optional[int] = None

    # --------------------------------------------------
    # 🧾 Diagnostics
    # --------------------------------------------------
    warnings: List[str] = None

    # --------------------------------------------------
    # 🔎 Canonical helpers
    # --------------------------------------------------
    def components(self) -> Dict[str, float]:
        """
        Return SSR components in canonical form.
        """
        return {
            k: v
            for k, v in {
                "performance": self.performance_score,
                "risk": self.risk_score,
                "stability": self.stability_score,
            }.items()
            if v is not None
        }
