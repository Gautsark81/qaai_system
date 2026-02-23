from typing import Dict
from .models import RegulatoryExport


class RegulatoryExportPolicy:
    """
    Policy governing how regulatory exports are formed.

    No file IO.
    No external calls.
    Deterministic input → deterministic output.
    """

    @staticmethod
    def create_export(
        *,
        export_type: str,
        generated_at: int,
        data: Dict[str, str],
    ) -> RegulatoryExport:
        if not export_type:
            raise ValueError("export_type must be provided")

        if not isinstance(generated_at, int):
            raise ValueError("generated_at must be deterministic integer")

        if not isinstance(data, dict):
            raise ValueError("data must be a dict")

        return RegulatoryExport(
            export_type=export_type,
            generated_at=generated_at,
            payload=dict(data),
        )
