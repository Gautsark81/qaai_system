import math


class AllocationCurves:
    """
    Pure capital allocation curve math.
    """

    @staticmethod
    def base_curve(*, ssr: float, health: float) -> float:
        ssr = max(0.0, min(1.0, ssr))
        health = max(0.0, min(1.0, health))
        return math.sqrt(ssr * health)
