# core/context/context_governance.py

from types import MappingProxyType


class GovernanceNotes(list):
    """
    Append-once governance notes channel.

    Contract:
    - Behaves like a list
    - Exactly ONE append allowed
    - No removal or mutation
    - Notes are immutable
    - Read-only after first write
    """

    __slots__ = ("_context_hash", "_sealed")

    def __init__(self, context_hash: str):
        super().__init__()
        self._context_hash = context_hash
        self._sealed = False

    # -----------------------------
    # Controlled append
    # -----------------------------
    def append(self, note: dict):
        if self._sealed:
            raise TypeError("Governance notes are sealed and read-only")

        if not isinstance(note, dict):
            raise TypeError("Governance note must be a dict")

        frozen = dict(note)
        frozen["context_hash"] = self._context_hash

        super().append(MappingProxyType(frozen))

        # Seal after first append
        self._sealed = True

    # -----------------------------
    # Block mutation/removal
    # -----------------------------
    def pop(self, *args, **kwargs):
        raise TypeError("Governance notes are read-only")

    def clear(self):
        raise TypeError("Governance notes are read-only")

    def __delitem__(self, key):
        raise TypeError("Governance notes are read-only")

    def __setitem__(self, key, value):
        raise TypeError("Governance notes are read-only")

    # -----------------------------
    # Export
    # -----------------------------
    def export(self):
        """
        Immutable, serializable snapshot.
        """
        return tuple(self)
