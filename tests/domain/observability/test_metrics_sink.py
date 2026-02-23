from domain.observability.metrics_sink import MetricsSink


def test_metrics_emission():
    sink = MetricsSink()
    sink.emit({"name": "latency_ms", "value": 120})
    assert len(sink.all()) == 1
