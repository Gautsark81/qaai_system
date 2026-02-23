# modules/guardrails/strategy_guard.py

from contextlib import contextmanager
from modules.guardrails.import_guard import install_import_block

FORBIDDEN_IMPORT_PREFIXES = (
    "modules.data_pipeline",
    "modules.execution",
    "modules.broker",
    "modules.order_manager",
    "modules.risk",
)


@contextmanager
def strategy_import_context():
    install_import_block(FORBIDDEN_IMPORT_PREFIXES)
    yield
