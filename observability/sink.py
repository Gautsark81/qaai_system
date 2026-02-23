class EventSink:
    """
    Sink interface (stdout, file, Kafka, Prometheus adapter, etc.)
    """

    def emit(self, event):
        raise NotImplementedError
