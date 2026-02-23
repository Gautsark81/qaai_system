from .models import CapitalCorrelationConcentrationView
from .correlation import build_correlation_warnings
from .concentration import build_concentration_warnings


def build_capital_risk_advisory(
    correlation_matrix,
    allocation_report,
    correlation_threshold: float,
    concentration_threshold: float,
):
    return CapitalCorrelationConcentrationView(
        correlation_warnings=build_correlation_warnings(
            correlation_matrix, correlation_threshold
        ),
        concentration_warnings=build_concentration_warnings(
            allocation_report, concentration_threshold
        ),
    )
