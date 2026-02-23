# core/adaptivity/parameter_registry.py

import json
from pathlib import Path
from dataclasses import asdict
from typing import Dict
from core.adaptivity.parameter_contract import AdaptiveParameter


class ParameterRegistry:
    """
    Persistent registry of adaptive parameters.
    """

    def __init__(self, path: str = "data/adaptivity/parameters.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._params: Dict[str, AdaptiveParameter] = {}
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        raw = json.loads(self.path.read_text())
        for name, p in raw.items():
            self._params[name] = AdaptiveParameter(**p)

    def _persist(self):
        payload = {
            name: asdict(param)
            for name, param in self._params.items()
        }
        self.path.write_text(json.dumps(payload, indent=2))

    def register(self, param: AdaptiveParameter):
        if param.name in self._params:
            raise RuntimeError("Parameter already registered")
        self._params[param.name] = param
        self._persist()

    def update(self, name: str, new_value: float):
        if name not in self._params:
            raise RuntimeError("Unknown parameter")

        param = self._params[name]
        param.validate(new_value)

        self._params[name] = AdaptiveParameter(
            name=param.name,
            current_value=new_value,
            min_value=param.min_value,
            max_value=param.max_value,
            description=param.description,
        )
        self._persist()

    def get(self, name: str) -> AdaptiveParameter:
        return self._params[name]

    def all(self):
        return self._params.copy()
