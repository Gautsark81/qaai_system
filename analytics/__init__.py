# analytics/__init__.py

# expose train_meta_model_main when available, but avoid forcing import-time side-effects
try:
    from . import train_meta_model as _train_meta
    train_meta_model_main = getattr(_train_meta, "main", None)
except Exception:
    # If anything goes wrong, present a harmless fallback (None)
    train_meta_model_main = None

# other imports in this file can remain, but ensure they do not execute heavy work
