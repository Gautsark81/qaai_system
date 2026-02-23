from core.capital_governance.correlation import build_correlation_warnings
from core.capital.correlation_matrix import CorrelationMatrix


def test_correlation_warning_emitted():
    matrix = CorrelationMatrix.from_pairs(
        ("s1", "s2", 0.91),
    )

    warnings = build_correlation_warnings(matrix, threshold=0.9)

    assert len(warnings) == 1
