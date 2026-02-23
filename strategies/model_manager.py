"""
strategies/model_manager.py

Simple model persistence + auto-reload helper.

Usage:
    mm = ModelManager("models/meta_model.pkl")
    adapter = mm.get_adapter()  # returns ModelAdapter loaded with latest artifact
    # To refresh if file changed:
    mm.poll_reload()  # checks mtime and reloads if changed
"""

from pathlib import Path
import time
import logging
from typing import Optional
from strategies.strategy_engine import ModelAdapter  # type: ignore

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class ModelManager:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else None
        self._adapter = None
        self._mtime = None
        if self.model_path and self.model_path.exists():
            self._load()

    def _load(self):
        try:
            self._adapter = ModelAdapter(self.model_path)
            self._mtime = self.model_path.stat().st_mtime if self.model_path.exists() else None
            logger.info("ModelManager: loaded model from %s", self.model_path)
        except Exception as e:
            logger.exception("ModelManager: failed to load model: %s", e)
            self._adapter = None
            self._mtime = None

    def get_adapter(self):
        # return current adapter or a ModelAdapter(empty) if None
        if self._adapter is None:
            return ModelAdapter(None)
        return self._adapter

    def poll_reload(self):
        """
        Check if the model file changed and reload if needed.
        Returns True if reloaded.
        """
        if not self.model_path:
            return False
        if not self.model_path.exists():
            if self._adapter is not None:
                logger.info("ModelManager: model file removed -> clearing adapter")
                self._adapter = None
                self._mtime = None
            return False
        m = self.model_path.stat().st_mtime
        if self._mtime is None or m > self._mtime:
            logger.info("ModelManager: detected model change; reloading")
            self._load()
            return True
        return False

    def set_path(self, new_path: Optional[str]):
        self.model_path = Path(new_path) if new_path else None
        self._load()
