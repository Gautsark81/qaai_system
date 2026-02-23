# core/oversight/tests/test_severity_policy.py

from core.oversight.correlation.severity_policy import compose_severity


def test_critical_dominates():
    result = compose_severity(
        severities=["INFO", "CRITICAL"],
        involved_domains=["capital"],
    )
    assert result == "CRITICAL"


def test_multi_domain_warning_escalates_to_critical():
    result = compose_severity(
        severities=["WARNING", "WARNING"],
        involved_domains=["capital", "governance"],
    )
    assert result == "CRITICAL"


def test_single_warning_does_not_escalate():
    result = compose_severity(
        severities=["WARNING"],
        involved_domains=["capital"],
    )
    assert result == "WARNING"


def test_info_only_remains_info():
    result = compose_severity(
        severities=["INFO"],
        involved_domains=["lifecycle"],
    )
    assert result == "INFO"


def test_empty_inputs_safe_default():
    result = compose_severity(
        severities=[],
        involved_domains=[],
    )
    assert result == "INFO"


def test_invalid_severity_downgrades_safely():
    result = compose_severity(
        severities=["UNKNOWN"],
        involved_domains=["capital"],
    )
    assert result == "INFO"


def test_mixed_info_and_warning_single_domain():
    result = compose_severity(
        severities=["INFO", "WARNING"],
        involved_domains=["capital"],
    )
    assert result == "WARNING"


def test_warning_multiple_domains_but_single_warning():
    result = compose_severity(
        severities=["WARNING"],
        involved_domains=["capital", "governance"],
    )
    assert result == "WARNING"
