# core/dashboard_read/replay/context.py

from __future__ import annotations


class ReplayContext:
    """
    Canonical replay context.

    Contract (as enforced by tests):

    replay_input
      └── snapshot (ReplaySnapshotView)
          ├── components        ← REPLAY SURFACE (mutable)
          └── snapshot          ← SEALED SNAPSHOT (immutable)
    """

    def __init__(self, replay_input):
        if not hasattr(replay_input, "snapshot"):
            raise AttributeError("Missing required attribute: snapshot")

        self.view = replay_input.snapshot

        # 🔑 REPLAY SURFACE — THIS WAS THE BUG
        if not hasattr(self.view, "components"):
            raise AttributeError("Missing required attribute: components")

        self.components = self.view.components

        # 🔒 SEALED SNAPSHOT
        if not hasattr(self.view, "snapshot"):
            raise AttributeError("Missing required attribute: snapshot")

        self.sealed = self.view.snapshot

        for attr in ("snapshot_hash", "chain_hash"):
            if not hasattr(self.sealed, attr):
                raise AttributeError(f"Missing required attribute: {attr}")