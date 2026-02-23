from typing import List
from .models import AuditBundle, RegulatoryExport


class AuditBundleBuilder:
    """
    Builds time-boxed audit bundles.

    Reads only prepared regulatory exports.
    Does not query systems or mutate state.
    """

    @staticmethod
    def build(
        *,
        start_timestamp: int,
        end_timestamp: int,
        exports: List[RegulatoryExport],
    ) -> AuditBundle:
        if end_timestamp < start_timestamp:
            raise ValueError("end_timestamp must be >= start_timestamp")

        return AuditBundle(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            artifacts=list(exports),
        )
