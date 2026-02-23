from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StrategyHealthSnapshot:
    """
    Immutable snapshot of strategy health.

    Design rules:
    - Read-only
    - Deterministic
    - Serializable
    - No lifecycle / capital authority
    """

    # --------------------------------------------------
    # 🧬 Identity
    # --------------------------------------------------
    strategy_dna: str = ""
    timestamp: Optional[datetime] = None

    # --------------------------------------------------
    # 🧠 Aggregate Health (engine-level)
    # --------------------------------------------------
    health_score: float = 0.0
    confidence: float = 0.0
    decay_risk: float = 0.0

    # --------------------------------------------------
    # 📊 Detailed Metrics
    # --------------------------------------------------
    performance_metrics: Optional[Dict[str, float]] = None
    risk_metrics: Optional[Dict[str, float]] = None
    signal_metrics: Optional[Dict[str, float]] = None
    regime_alignment: Optional[Dict[str, float]] = None

    # --------------------------------------------------
    # 🧠 SSR (Strategy Success Ratio) — C1 Layer
    # --------------------------------------------------
    performance_score: float = 0.0
    risk_score: float = 0.0
    stability_score: float = 0.0

    ssr: float = 0.0
    ssr_components: Optional[Dict[str, float]] = None

    # --------------------------------------------------
    # 📈 Evidence Required for Governance (C1.4)
    # --------------------------------------------------
    total_trades: int = 0
    max_drawdown: float = 0.0

    # --------------------------------------------------
    # 🚨 Diagnostics
    # --------------------------------------------------
    flags: Optional[List[str]] = None

    # --------------------------------------------------
    # ✅ Validation
    # --------------------------------------------------
    def validate(self) -> None:
        if not (0.0 <= self.health_score <= 1.0):
            raise ValueError("health_score out of bounds")
        if not (0.0 <= self.decay_risk <= 1.0):
            raise ValueError("decay_risk out of bounds")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence out of bounds")
        if not (0.0 <= self.ssr <= 1.0):
            raise ValueError("ssr out of bounds")
        if self.total_trades < 0:
            raise ValueError("total_trades must be non-negative")
        if not (0.0 <= self.max_drawdown <= 1.0):
            raise ValueError("max_drawdown out of bounds")
