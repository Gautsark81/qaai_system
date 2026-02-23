def read_pipeline_metrics():
    """
    Read raw pipeline metrics.

    Seam only — tests monkeypatch this.
    """
    from core.pipeline import metrics  # noqa: F401
    return metrics.get_pipeline_metrics()
