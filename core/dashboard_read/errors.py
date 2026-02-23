class SnapshotBuildError(RuntimeError):
    """
    Raised only if snapshot atomicity is violated.
    In D-3 this should never be raised.
    """
    pass
