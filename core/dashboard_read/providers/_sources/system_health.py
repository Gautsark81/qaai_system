def read_data_feed_status():
    """
    Seam only.
    Must raise ImportError when not wired.
    """
    raise ImportError("Data feed source not wired")


def read_broker_status():
    """
    Seam only.
    Must raise ImportError when not wired.
    """
    raise ImportError("Broker status source not wired")


def read_service_status():
    """
    Seam only.
    Must raise ImportError when not wired.
    """
    raise ImportError("Service status source not wired")