from core.dashboard_read.snapshot import ScreeningState
from core.dashboard_read.providers._sources import screening as screening_source


def build_screening_state() -> ScreeningState:
    metrics = screening_source.read_screening_metrics()

    return ScreeningState(
        symbols_seen=metrics.symbols_seen,
        passed=metrics.passed,
        rejected_by_reason=dict(metrics.rejected_by_reason),
    )
