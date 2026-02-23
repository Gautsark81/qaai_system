import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra import config_loader


def test_config_exists():
    config = config_loader.load_config()
    assert isinstance(config, dict)
