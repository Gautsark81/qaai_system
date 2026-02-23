from dataclasses import dataclass
from typing import List

from modules.strategy_health.evaluator import HealthResult


# ==========================================================
# Result Contract
# ==========================================================

@dataclass(frozen=True)
class DecaySignal:
    level: str
    reasons: List[str]
    windows_confirmed: List[int]


# ==========================================================
# Decay Detector
# ==========================================================

class DecayDetector:
    """
    Pure, deterministic decay detector.

    Consumes ordered HealthResult history (oldest → newest).
    Emits decay events only (no state changes).
    """

    SHORT = 30
    MEDIUM = 60
    LONG = 120

    def evaluate(self, history: List[HealthResult]) -> DecaySignal:
        if len(history) < self.SHORT * 2:
            return DecaySignal(
                level="NO_DECAY",
                reasons=["Insufficient history for decay analysis"],
                windows_confirmed=[],
            )

        reasons: List[str] = []
        confirmed_windows: List[int] = []
        dimensions_confirmed = 0

        # -------------------------
        # Health Trend Decay
        # -------------------------
        health_trend_windows = self._health_trend_decay(history)
        if health_trend_windows:
            dimensions_confirmed += 1
            confirmed_windows.extend(health_trend_windows)
            reasons.append("Health score trending downward")

        # -------------------------
        # Drawdown Expansion
        # -------------------------
        drawdown_windows = self._drawdown_expansion(history)
        if drawdown_windows:
            dimensions_confirmed += 1
            confirmed_windows.extend(drawdown_windows)
            reasons.append("Drawdown band worsening")

        # -------------------------
        # Win-Rate Compression
        # -------------------------
        winrate_windows = self._winrate_compression(history)
        if winrate_windows:
            dimensions_confirmed += 1
            confirmed_windows.extend(winrate_windows)
            reasons.append("Win rate compression detected")

        # -------------------------
        # Final Level
        # -------------------------
        confirmed_windows = sorted(set(confirmed_windows))

        if dimensions_confirmed == 0:
            level = "NO_DECAY"
        elif dimensions_confirmed == 1:
            level = "SOFT_DECAY"
        elif dimensions_confirmed == 2:
            level = "HARD_DECAY"
        else:
            level = "STRUCTURAL_DECAY"

        # Long-horizon confirmation escalates
        if (
            level in {"HARD_DECAY", "STRUCTURAL_DECAY"}
            and self.LONG in confirmed_windows
        ):
            level = "STRUCTURAL_DECAY"

        return DecaySignal(
            level=level,
            reasons=reasons,
            windows_confirmed=confirmed_windows,
        )

    # ======================================================
    # Internal checks
    # ======================================================

    def _health_trend_decay(self, history: List[HealthResult]) -> List[int]:
        confirmed = []
        for w in (self.SHORT, self.MEDIUM, self.LONG):
            if len(history) < w * 2:
                continue
            prev = history[-2 * w : -w]
            curr = history[-w:]

            prev_mean = sum(h.health_score for h in prev) / w
            curr_mean = sum(h.health_score for h in curr) / w

            if curr_mean < prev_mean:
                confirmed.append(w)
        return confirmed

    def _drawdown_expansion(self, history: List[HealthResult]) -> List[int]:
        confirmed = []
        for w in (self.SHORT, self.MEDIUM, self.LONG):
            if len(history) < w * 2:
                continue
            prev = history[-2 * w : -w]
            curr = history[-w:]

            prev_dd = min(h.signals.get("drawdown", 1.0) for h in prev)
            curr_dd = min(h.signals.get("drawdown", 1.0) for h in curr)

            if curr_dd < prev_dd:
                confirmed.append(w)
        return confirmed

    def _winrate_compression(self, history: List[HealthResult]) -> List[int]:
        confirmed = []
        for w in (self.SHORT, self.MEDIUM, self.LONG):
            if len(history) < w * 2:
                continue
            prev = history[-2 * w : -w]
            curr = history[-w:]

            prev_wr = min(h.signals.get("win_rate", 1.0) for h in prev)
            curr_wr = min(h.signals.get("win_rate", 1.0) for h in curr)

            if curr_wr < prev_wr:
                confirmed.append(w)
        return confirmed
