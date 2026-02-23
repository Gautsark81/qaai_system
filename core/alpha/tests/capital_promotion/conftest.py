def get_events(view):
    for name in ("get_evidence", "iter_evidence", "evidence"):
        if hasattr(view, name):
            obj = getattr(view, name)
            return list(obj()) if callable(obj) else list(obj)
    raise AssertionError("AuthorizedRuntimeView exposes no evidence surface")
