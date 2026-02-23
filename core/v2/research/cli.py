from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from core.v2.research.manifest import ResearchRunManifest
from core.v2.research.registry import ExperimentRegistry
from core.v2.research.contracts import ResearchExperimentError


class ReplayMismatchError(RuntimeError):
    """Raised when replayed results do not match the manifest."""


def replay_from_manifest(
    *,
    manifest_path: Path,
    registry: ExperimentRegistry,
) -> ResearchRunManifest:
    """
    Replay a research run from a manifest and verify determinism.
    """
    manifest = _load_manifest(manifest_path)

    # Re-run experiment via registry
    result = registry.run(
        manifest.experiment_id,
        start=_parse_iso(manifest.start),
        end=_parse_iso(manifest.end),
        seed=manifest.seed,
        metadata={},
    )

    # Verify result identity
    if result.result_id != manifest.result_id:
        raise ReplayMismatchError("result_id mismatch on replay")

    if result.payload_hash != manifest.payload_hash:
        raise ReplayMismatchError("payload_hash mismatch on replay")

    return manifest


def _load_manifest(path: Path) -> ResearchRunManifest:
    raw = json.loads(path.read_text())

    # Strip derived / computed fields
    raw.pop("manifest_id", None)
    raw.pop("created_at", None)

    try:
        return ResearchRunManifest(**raw)
    except TypeError as e:
        raise ResearchExperimentError(
            f"Invalid manifest format: {e}"
        ) from e


def _parse_iso(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="qaai-research")
    sub = parser.add_subparsers(dest="command", required=True)

    replay = sub.add_parser("replay", help="Replay a research manifest")
    replay.add_argument("--manifest", required=True)

    args = parser.parse_args(argv)

    if args.command == "replay":
        # NOTE: registry must be wired by caller in real usage
        raise SystemExit(
            "Replay CLI requires an injected ExperimentRegistry"
        )
