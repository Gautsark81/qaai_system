# scripts/health_check.py
#!/usr/bin/env python3
"""
Lightweight health endpoint (no Flask). Run: python scripts/health_check.py 8080
"""
import http.server
import json
import socketserver
import sys
from modules.observability.metrics import Metrics

metrics = Metrics()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            payload = {"status": "ok"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        elif self.path == "/metrics":
            m = metrics.prometheus_metrics()
            if m is not None:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.end_headers()
                self.wfile.write(m)
            else:
                self.send_response(501)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "prometheus client not installed"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving health on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
