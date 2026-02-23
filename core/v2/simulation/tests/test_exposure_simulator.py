from core.v2.simulation.exposure_simulator import ExposureSimulator


def test_excessive_exposure_is_blocked():
    sim = ExposureSimulator()

    safe = sim.evaluate({"AAPL": 0.3, "MSFT": 0.2})
    unsafe = sim.evaluate({"AAPL": 0.6})

    assert safe is True
    assert unsafe is False
