import os
import time
import logging
import requests
from typing import Optional

# === Logger Setup ===
logger = logging.getLogger(__name__)
TEST_MODE = os.environ.get("TEST_MODE", "0") in ("1", "true", "True")

# === Environment Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TEST_MODE = os.getenv("TEST_MODE", "false").lower() in ("true", "1", "yes")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    if not TEST_MODE:
        logger.warning("⚠️ Telegram credentials not set in environment variables.")

# === Constants ===
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    if TELEGRAM_BOT_TOKEN
    else None
)


def is_enabled():
    """Return whether real Telegram posting is enabled (not in TEST_MODE and token present)."""
    if TEST_MODE:
        return False
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    return bool(token and chat)


def send_telegram_alert(
    message: str, parse_mode: str = "Markdown", disable_notification: bool = False
) -> bool:
    """
    Sends a Telegram alert with retry logic, rich formatting, and test-mode support.
    MASTER UPGRADE OBJECTIVES:
    - Failover safe (does not crash the system)
    - Works identically in TEST_MODE (no live API calls)
    - Uniform logging for audit trail
    """
    if TEST_MODE:
        logger.info(f"[TEST_MODE] 🚀 Telegram alert simulated: {message}")
        return True

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ Missing Telegram Bot Token or Chat ID.")
        return False

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_notification": disable_notification,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(
                f"📤 Sending Telegram alert (attempt {attempt}): {message[:60]}..."
            )
            response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("✅ Telegram alert sent successfully.")
                return True
            else:
                logger.warning(
                    f"⚠️ Telegram API responded with {response.status_code}: {response.text}"
                )

        except requests.RequestException as e:
            logger.error(f"❌ Telegram alert failed (attempt {attempt}): {e}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    logger.critical("🚨 All attempts to send Telegram alert have failed.")
    return False


def send_trade_alert(
    symbol: str, action: str, price: float, confidence: Optional[float] = None
):
    """Pre-formatted trade alert — risk-adjusted, audit-friendly."""
    action_icon = "🟢 BUY" if action.upper() == "BUY" else "🔴 SELL"
    confidence_text = (
        f"\n📊 Confidence: *{confidence:.2%}*" if confidence is not None else ""
    )
    message = (
        f"{action_icon} Alert\n"
        f"📌 Symbol: *{symbol}*\n"
        f"💵 Price: `{price:.2f}`"
        f"{confidence_text}\n"
        f"🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    send_telegram_alert(message)


def send_system_alert(event: str, details: str):
    """System health/status alert — part of Self-Diagnostic Subsystems."""
    message = (
        f"⚙️ *System Alert: {event}*\n"
        f"📝 {details}\n"
        f"🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    send_telegram_alert(message)
