import inspect

from core.compliance.exports.json_export import JSONAuditExporter
from core.compliance.exports.pdf_export import PDFAuditExporter
from core.compliance.exports.seal import seal_export, verify_export


def test_export_modules_have_no_execution_authority():
    forbidden = {"run", "execute", "place_order", "submit", "trade"}

    for obj in [
        JSONAuditExporter,
        PDFAuditExporter,
        seal_export,
        verify_export,
    ]:
        names = dir(obj)
        for f in forbidden:
            assert f not in names, f"Forbidden method {f} found in {obj}"
