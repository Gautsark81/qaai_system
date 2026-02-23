from abc import ABC, abstractmethod

from .metrics import LiveDecayMetrics


class DecayDetector(ABC):
    """
    Pure detector. Returns True if decay is detected.
    """

    @abstractmethod
    def detect(self, metrics: LiveDecayMetrics) -> bool:
        ...


# ----------------------------
# Concrete Detectors
# ----------------------------

class SharpeDecayDetector(DecayDetector):
    def __init__(self, drop_ratio: float):
        self.drop_ratio = drop_ratio

    def detect(self, metrics: LiveDecayMetrics) -> bool:
        if metrics.sharpe <= 0:
            return True
        return metrics.rolling_sharpe < metrics.sharpe * self.drop_ratio


class DriftDetector(DecayDetector):
    def __init__(self, psi_limit: float):
        self.psi_limit = psi_limit

    def detect(self, metrics: LiveDecayMetrics) -> bool:
        return metrics.psi > self.psi_limit


class EntropyExplosionDetector(DecayDetector):
    def __init__(self, multiplier: float):
        self.multiplier = multiplier

    def detect(self, metrics: LiveDecayMetrics) -> bool:
        return metrics.prediction_entropy > self.multiplier


class ShadowDivergenceDetector(DecayDetector):
    def __init__(self, disagreement_limit: float):
        self.disagreement_limit = disagreement_limit

    def detect(self, metrics: LiveDecayMetrics) -> bool:
        return metrics.shadow_disagreement_rate > self.disagreement_limit
