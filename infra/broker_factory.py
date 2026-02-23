# qaai_system/infra/broker_factory.py

"""
Factory module to return the correct BrokerAdapter
depending on MODE (paper or live).
"""

import logging
import env_config as cfg  # ✅ local import (since env_config.py is at project root)
from infra.dhan_adapter import DhanAdapterSandbox  # ✅ local import

logger = logging.getLogger("broker_factory")


def get_broker_adapter():
    """
    Returns a BrokerAdapter depending on MODE.
    - MODE=paper → sandbox adapter
    - MODE=live  → real/live adapter (if available)
    """
    if cfg.MODE == "live":
        try:
            # For now, still using DhanAdapterSandbox as placeholder.
            # In future: plug in DhanAdapterLive here.
            logger.info("Using live broker adapter (currently sandbox fallback).")
            return DhanAdapterSandbox(api_key=cfg.DHAN_ACCESS_TOKEN)
        except Exception as e:
            logger.error(f"❌ Failed to init live broker adapter: {e}")
            raise
    else:
        logger.info("Using sandbox broker adapter (paper mode).")
        return DhanAdapterSandbox()
