# core/context/context_visibility.py

from typing import Optional


class ReadOnlyDict(dict):
    """
    Immutable, deepcopy-safe dictionary for audit surfaces.
    """

    def __readonly__(self, *args, **kwargs):
        raise TypeError("Context snapshot is read-only")

    __setitem__ = __readonly__
    __delitem__ = __readonly__
    clear = __readonly__
    pop = __readonly__
    popitem = __readonly__
    setdefault = __readonly__
    update = __readonly__

    def __deepcopy__(self, memo):
        # Preserve identity on deepcopy
        return self


class ContextVisibilitySurface:
    """
    Read-only context export surface.

    Purpose:
    - dashboards
    - audits
    - evidence / forensic inspection

    This surface MUST NOT influence execution.
    """

    __slots__ = ("_provider",)

    def __init__(self, provider=None):
        self._provider = provider

    def export(self, *, symbol: str) -> Optional[dict]:
        """
        Export a deterministic, immutable context snapshot for a symbol.
        """
        if self._provider is None:
            return None

        snapshot = self._provider.get(symbol)
        if snapshot is None:
            return None

        # IMPORTANT:
        # snapshot may be a mappingproxy → normalize to dict first
        return ReadOnlyDict(dict(snapshot))
