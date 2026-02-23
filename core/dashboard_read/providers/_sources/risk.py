# providers/_sources/risk.py
def read_risk_metrics():
    from core.risk import metrics
    return metrics.get_risk_metrics()
