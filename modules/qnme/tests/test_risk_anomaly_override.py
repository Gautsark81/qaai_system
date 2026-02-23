# modules/qnme/tests/test_risk_anomaly_override.py
from modules.qnme.risk import RiskEngine
from modules.qnme.anomaly import detect_anomaly
from modules.qnme.override import MetaCognitiveOverride

def test_risk_and_override():
    re = RiskEngine()
    for i in range(10):
        re.update_returns(-0.01)  # bad returns
    mco = MetaCognitiveOverride(risk_engine=re)
    action = mco.evaluate({"name":"low_vol_range","conf":0.5}, False, {})
    assert action["action"] in ("allow","soft_halt","halt")
    # anomaly detection
    genome = {"genome":{"avg_dt":1,"imbalance":500}}
    tick = {"price":100.0,"spread":0.1}
    flag, reason = detect_anomaly(genome, tick)
    assert flag
