# tests/guardrails/test_strategy_import_block.py

import pytest
from modules.guardrails.strategy_guard import strategy_import_context


def test_strategy_cannot_import_data_layer():
    with strategy_import_context():
        with pytest.raises(ImportError):
            __import__("modules.data_pipeline.loader")
