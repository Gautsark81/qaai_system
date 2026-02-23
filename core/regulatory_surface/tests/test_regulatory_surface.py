import inspect

from core.regulatory_surface.export_policy import RegulatoryExportPolicy
from core.regulatory_surface.audit_bundle import AuditBundleBuilder
from core.regulatory_surface.explainability import ExplainabilityBuilder
from core.regulatory_surface.models import RegulatoryExport, AuditBundle, ExplainabilityPacket


def test_regulatory_export_creation():
    export = RegulatoryExportPolicy.create_export(
        export_type="SEBI_AUDIT",
        generated_at=1000,
        data={"status": "ok"},
    )

    assert isinstance(export, RegulatoryExport)
    assert export.payload["status"] == "ok"


def test_audit_bundle_is_built():
    export = RegulatoryExportPolicy.create_export(
        export_type="SEBI_AUDIT",
        generated_at=1000,
        data={"x": "y"},
    )

    bundle = AuditBundleBuilder.build(
        start_timestamp=900,
        end_timestamp=1100,
        exports=[export],
    )

    assert isinstance(bundle, AuditBundle)
    assert bundle.start_timestamp == 900
    assert len(bundle.artifacts) == 1


def test_explainability_packet():
    packet = ExplainabilityBuilder.build(
        timestamp=1200,
        summary={"reason": "operator acknowledged"},
    )

    assert isinstance(packet, ExplainabilityPacket)
    assert packet.summary["reason"] == "operator acknowledged"


def test_no_execution_authority_present():
    modules = [
        RegulatoryExportPolicy,
        AuditBundleBuilder,
        ExplainabilityBuilder,
    ]

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for obj in modules:
        source = inspect.getsource(obj).lower()
        for word in forbidden:
            assert word not in source
