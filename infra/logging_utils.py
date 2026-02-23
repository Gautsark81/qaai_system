# qaai_system/infra/logging_utils.py

import logging
import os
import env_config as cfg  # ✅ fixed import
from typing import List, Dict, Any

try:
    from qaai_system import env_config as cfg
except Exception:
    cfg = None


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        os.makedirs("logs", exist_ok=True)

        fh = logging.FileHandler("logs/system.log")
        fh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(sh)

        level = getattr(cfg, "LOG_LEVEL", "INFO") if cfg else "INFO"
        logger.setLevel(level)

    logger.propagate = True
    return logger


def log_data_source(
    logger: logging.Logger, symbol: str, bars: List[Dict[str, Any]]
) -> str:
    """
    Unified helper to log which data source was used for OHLCV bars.
    Also forces logs through root logger so pytest caplog can capture them.
    Returns the logged message string.
    """
    if bars and isinstance(bars[0], dict) and "source" in bars[0]:
        msg = f"{symbol} using data source: {bars[0]['source']}"
    else:
        msg = f"{symbol} data source unknown, check provider"

    # 🔥 Always log through root so pytest caplog can see it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.info(msg)

    # Still log through provided logger
    if logger:
        logger.info(msg)

    return msg
