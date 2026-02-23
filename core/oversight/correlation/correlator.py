# core/oversight/correlation/correlator.py

class OversightCorrelator:
    """
    Correlates independent anomaly detectors into a single signal.
    """

    def correlate(
        self,
        *,
        capital_anomalies,
        governance_anomalies,
        lifecycle_anomalies,
        now: datetime,
    ) -> List[CorrelationSignal]:
        ...
