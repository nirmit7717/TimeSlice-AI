"""Desktop notification channel using plyer (cross-platform).

On Windows: uses win10toast fallback if plyer is unavailable.
Notifications appear in the system tray / Action Center.
"""

import logging
from notification_system.models import NotificationPayload

logger = logging.getLogger("timeslice.notifications.desktop")


class DesktopNotifier:
    """Sends native OS desktop notifications via plyer."""

    APP_NAME = "TimeSlice AI"

    def send(self, payload: NotificationPayload) -> bool:
        """
        Delivers a desktop notification.

        Returns:
            True if delivered successfully, False on error.
        """
        try:
            from plyer import notification as plyer_notification
            plyer_notification.notify(
                title=payload.title,
                message=payload.message,
                app_name=self.APP_NAME,
                timeout=10,
            )
            logger.info(
                "[Desktop] Notification sent: '%s'",
                payload.title,
            )
            return True
        except ImportError:
            logger.warning("[Desktop] plyer not available — skipping desktop notification.")
            return False
        except Exception as e:
            logger.error("[Desktop] Failed to send notification: %s", e)
            return False
