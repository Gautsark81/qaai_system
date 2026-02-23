# modules/bootstrap/runtime.py

from modules.bootstrap.wiring import wire_application


def start_runtime() -> None:
    app = wire_application()
    app.run()
