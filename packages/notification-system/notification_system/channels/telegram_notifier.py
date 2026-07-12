"""Telegram notification channel via Bot HTTP API.

Reads TELEGRAM_BOT_TOKEN from environment variables.
Gracefully no-ops (logs warning) if the token is not set.

To activate:
  1. Create a bot via @BotFather on Telegram
  2. Set TELEGRAM_BOT_TOKEN=<your-token> in your .env file
  3. Set TELEGRAM_CHAT_ID in the operator's adaptive profile

Usage:
  notifier = TelegramNotifier()
  notifier.send(payload, chat_id="your-chat-id")
"""

import os
import logging
import requests
from notification_system.models import NotificationPayload

logger = logging.getLogger("timeslice.notifications.telegram")

# Leave empty — user will add their token manually
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE: str = "https://api.telegram.org"


class TelegramNotifier:
    """Sends notifications via Telegram Bot API."""

    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN):
        self.bot_token = bot_token
        self._configured = bool(bot_token)

    def send(self, payload: NotificationPayload, chat_id: str) -> bool:
        """
        Sends a formatted message to the specified Telegram chat.

        Args:
            payload: The notification to send.
            chat_id: Telegram chat/user ID to send to.

        Returns:
            True if delivered, False on error or if not configured.
        """
        if not self._configured:
            logger.warning(
                "[Telegram] TELEGRAM_BOT_TOKEN not set — skipping notification '%s'. "
                "Set the env var to enable Telegram alerts.",
                payload.title,
            )
            return False

        text = self._format_message(payload)
        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/sendMessage"

        try:
            response = requests.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                timeout=10,
            )
            if response.ok:
                logger.info("[Telegram] Message sent to chat %s: '%s'", chat_id, payload.title)
                return True
            else:
                logger.error(
                    "[Telegram] API error %s: %s",
                    response.status_code,
                    response.text,
                )
                return False
        except Exception as e:
            logger.error("[Telegram] Request failed: %s", e)
            return False

    def _format_message(self, payload: NotificationPayload) -> str:
        """Formats a NotificationPayload as a Telegram Markdown message."""
        priority_emoji = {
            "low": "🔵", "normal": "✅", "high": "🟡", "critical": "🔴"
        }.get(payload.priority.value, "")

        type_emoji = {
            "time_slice_reminder": "⏰",
            "reflection_prompt": "💭",
            "deadline_alert": "🚨",
            "weekly_summary": "📊",
            "test": "🧪",
        }.get(payload.notification_type.value, "📌")

        lines = [
            f"{type_emoji} *{payload.title}* {priority_emoji}",
            "",
            payload.message,
        ]
        return "\n".join(lines)
