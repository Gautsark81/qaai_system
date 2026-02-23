"""
Dashboard read adapter for compliance / audit domain.
All compliance imports must live here.
"""

def read_compliance_metrics():
    from compliance.metrics import get_compliance_metrics
    return get_compliance_metrics()
