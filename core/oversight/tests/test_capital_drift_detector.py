from datetime import datetime

from core.oversight.detectors import CapitalDriftDetector


def test_no_detection_with_insufficient_history():
    detector = CapitalDriftDetector()

    snapshots = [
        {"alpha": 0.2},
        {"alpha": 0.25},
    ]

    observations = detector.detect(
        snapshots=snapshots,
        detected_at=datetime.utcnow(),
    )

    assert observations == []


def test_warning_drift_detected():
    detector = CapitalDriftDetector()

    snapshots = [
        {"alpha": 0.20},
        {"alpha": 0.22},
        {"alpha": 0.21},
        {"alpha": 0.23},
        {"alpha": 0.22},
        {"alpha": 0.35},  # +~60% drift
    ]

    observations = detector.detect(
        snapshots=snapshots,
        detected_at=datetime.utcnow(),
    )

    assert len(observations) == 1
    assert observations[0].severity == "CRITICAL"


def test_no_false_positive_for_stable_allocation():
    detector = CapitalDriftDetector()

    snapshots = [
        {"alpha": 0.30},
        {"alpha": 0.31},
        {"alpha": 0.29},
        {"alpha": 0.30},
        {"alpha": 0.30},
        {"alpha": 0.31},
    ]

    observations = detector.detect(
        snapshots=snapshots,
        detected_at=datetime.utcnow(),
    )

    assert observations == []
