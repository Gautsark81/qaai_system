from qaai_system.model_ops.capital import CapitalRouter

def test_routing_respects_weights():
    router = CapitalRouter(seed=1)

    counts = {"m1": 0, "m2": 0}
    for _ in range(10_000):
        m = router.choose_model([("m1", 0.7), ("m2", 0.3)])
        counts[m] += 1

    assert 0.65 < counts["m1"] / 10_000 < 0.75
