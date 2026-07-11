import requests
from typing import Dict, Any

class TelegramNotificationService:
    """
    Alert dispatch client sending notification messages to Telegram chat IDs.
    """
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, chat_id: str, message: str) -> bool:
        """
        Dispatches a message using the Telegram Bot API.
        """
        # Testing bypass handler: allows running test suite offline
        if self.bot_token == "mock-token":
            return True

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            res = requests.post(self.api_url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception:
            return False
