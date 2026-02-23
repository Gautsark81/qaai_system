class SSRDriftDetector:
    """
    Detects material degradation in strategy SSR.
    """

    MAX_RELATIVE_DROP = 0.20  # 20%

    @staticmethod
    def is_degraded(ssr_current: float, ssr_reference: float) -> bool:
        if ssr_reference <= 0:
            return False
        drop = (ssr_reference - ssr_current) / ssr_reference
        return drop >= SSRDriftDetector.MAX_RELATIVE_DROP
