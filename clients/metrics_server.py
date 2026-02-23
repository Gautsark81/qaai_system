# clients/metrics_server.py
from prometheus_client import start_http_server
import threading
import logging

logger = logging.getLogger(__name__)

_server_thread = None

def start_metrics_server(port: int = 8000):
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        return
    def _target():
        logger.info("Starting Prometheus metrics server on port %d", port)
        start_http_server(port)
        # keep thread alive
        import time
        while True:
            time.sleep(3600)
    t = threading.Thread(target=_target, name="metrics-server", daemon=True)
    t.start()
    _server_thread = t
