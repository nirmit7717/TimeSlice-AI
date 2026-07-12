"""Reminder Scheduler.

Uses APScheduler to set up cron and interval tasks for sending notifications:
  1. Time Slice Reminders (5 mins before start)
  2. Reflection Prompts (10 mins after end)
  3. Deadline Alerts (Critical/High risk deadlines approaching)
  4. Weekly Summary (Monday morning digest)
"""

import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from notification_system.models import NotificationPayload, NotificationType, NotificationPriority, NotificationChannel
from notification_system.dispatcher import NotificationDispatcher

logger = logging.getLogger("timeslice.notifications.scheduler")

# Background scheduler instance
scheduler = BackgroundScheduler()


def initialize_notification_scheduler(get_db_session_fn):
    """
    Starts the APScheduler and adds background jobs.
    
    Args:
        get_db_session_fn: A function that returns a new DB session.
    """
    if scheduler.running:
        logger.info("[Scheduler] Notification scheduler is already running.")
        return

    # Job 1: Check for upcoming time slices (runs every minute)
    scheduler.add_job(
        check_upcoming_time_slices,
        "interval",
        minutes=1,
        args=[get_db_session_fn],
        id="upcoming_time_slices_job",
        replace_existing=True
    )

    # Job 2: Check for pending reflections (runs every minute)
    scheduler.add_job(
        check_pending_reflections,
        "interval",
        minutes=1,
        args=[get_db_session_fn],
        id="pending_reflections_job",
        replace_existing=True
    )

    # Job 3: Check for deadline risks (runs every 15 minutes)
    scheduler.add_job(
        check_deadline_risks,
        "interval",
        minutes=15,
        args=[get_db_session_fn],
        id="deadline_risks_job",
        replace_existing=True
    )

    # Job 4: Weekly performance summary (runs Monday at 9:00 AM)
    scheduler.add_job(
        send_weekly_summary,
        CronTrigger(day_of_week="mon", hour=9, minute=0),
        args=[get_db_session_fn],
        id="weekly_summary_job",
        replace_existing=True
    )

    scheduler.start()
    logger.info("[Scheduler] Notification scheduler started successfully.")


def check_upcoming_time_slices(get_db_session_fn):
    """Checks for time slices starting in exactly 5 minutes and alerts the operator."""
    db = get_db_session_fn()
    try:
        from database.models import DbTimeSlice, DbAdaptiveProfile
        now = datetime.utcnow()
        target_start = now + timedelta(minutes=5)
        
        # Find slices starting between now + 4 mins and now + 6 mins
        slices = db.query(DbTimeSlice).filter(
            DbTimeSlice.status == "Scheduled",
            DbTimeSlice.start_time >= target_start - timedelta(minutes=1),
            DbTimeSlice.start_time <= target_start + timedelta(minutes=1),
        ).all()

        for ts in slices:
            # Check if reminder has already been sent (stored in notification history)
            profile = db.query(DbAdaptiveProfile).filter(
                DbAdaptiveProfile.operator_id == "default_operator"
            ).first()
            
            already_sent = False
            if profile and profile.notification_prefs:
                prefs = json.loads(profile.notification_prefs)
                history = prefs.get("notification_history", [])
                already_sent = any(
                    h["type"] == "time_slice_reminder" and h["slice_id"] == ts.id
                    for h in history
                )

            if not already_sent:
                # Resolve channels
                channels = [NotificationChannel.DESKTOP]
                if profile and profile.notification_prefs:
                    prefs = json.loads(profile.notification_prefs)
                    if prefs.get("telegram_chat_id"):
                        channels.append(NotificationChannel.TELEGRAM)

                payload = NotificationPayload(
                    notification_type=NotificationType.TIME_SLICE_REMINDER,
                    title="Upcoming Focus Session",
                    message=f"Your focus session for process {ts.process_id[:8]} starts in 5 minutes.",
                    priority=NotificationPriority.NORMAL,
                    channels=channels,
                    process_id=ts.process_id,
                    slice_id=ts.id,
                )
                
                dispatcher = NotificationDispatcher(db)
                dispatcher.dispatch(payload)
    except Exception as e:
        logger.error("[Scheduler] Error checking upcoming time slices: %s", e)
    finally:
        db.close()


def check_pending_reflections(get_db_session_fn):
    """Alerts user to input reflection if focus session completed/abandoned and reflection is empty."""
    db = get_db_session_fn()
    try:
        from database.models import DbTimeSlice, DbAdaptiveProfile
        now = datetime.utcnow()
        # Slices completed/abandoned in the last 30 minutes with empty reflection
        cutoff = now - timedelta(minutes=30)
        
        slices = db.query(DbTimeSlice).filter(
            DbTimeSlice.status.in_(["Completed", "Abandoned"]),
            DbTimeSlice.end_time >= cutoff,
            (DbTimeSlice.reflection == None) | (DbTimeSlice.reflection == ""),
        ).all()

        for ts in slices:
            profile = db.query(DbAdaptiveProfile).filter(
                DbAdaptiveProfile.operator_id == "default_operator"
            ).first()
            
            already_sent = False
            if profile and profile.notification_prefs:
                prefs = json.loads(profile.notification_prefs)
                history = prefs.get("notification_history", [])
                already_sent = any(
                    h["type"] == "reflection_prompt" and h["slice_id"] == ts.id
                    for h in history
                )

            if not already_sent:
                channels = [NotificationChannel.DESKTOP]
                if profile and profile.notification_prefs:
                    prefs = json.loads(profile.notification_prefs)
                    if prefs.get("telegram_chat_id"):
                        channels.append(NotificationChannel.TELEGRAM)

                payload = NotificationPayload(
                    notification_type=NotificationType.REFLECTION_PROMPT,
                    title="Time Slice Reflection Required",
                    message="Please record a brief reflection on your completed session to help adapt your schedule.",
                    priority=NotificationPriority.LOW,
                    channels=channels,
                    process_id=ts.process_id,
                    slice_id=ts.id,
                )
                
                dispatcher = NotificationDispatcher(db)
                dispatcher.dispatch(payload)
    except Exception as e:
        logger.error("[Scheduler] Error checking pending reflections: %s", e)
    finally:
        db.close()


def check_deadline_risks(get_db_session_fn):
    """Sends a critical alert if any process has high deadline risk and deadline is under 48 hours."""
    db = get_db_session_fn()
    try:
        from database.models import DbProcess, DbAdaptiveProfile
        now = datetime.utcnow()
        target_deadline = now + timedelta(hours=48)
        
        processes = db.query(DbProcess).filter(
            DbProcess.status == "Active",
            DbProcess.deadline <= target_deadline,
            DbProcess.deadline_risk.in_(["High", "Critical"])
        ).all()

        for proc in processes:
            profile = db.query(DbAdaptiveProfile).filter(
                DbAdaptiveProfile.operator_id == "default_operator"
            ).first()
            
            already_sent = False
            if profile and profile.notification_prefs:
                prefs = json.loads(profile.notification_prefs)
                history = prefs.get("notification_history", [])
                already_sent = any(
                    h["type"] == "deadline_alert" and h["process_id"] == proc.id
                    and (now - datetime.fromisoformat(h["timestamp"])).hours < 24
                    for h in history if "timestamp" in h
                )

            if not already_sent:
                channels = [NotificationChannel.DESKTOP]
                if profile and profile.notification_prefs:
                    prefs = json.loads(profile.notification_prefs)
                    if prefs.get("telegram_chat_id"):
                        channels.append(NotificationChannel.TELEGRAM)

                payload = NotificationPayload(
                    notification_type=NotificationType.DEADLINE_ALERT,
                    title="CRITICAL Deadline Risk",
                    message=f"Process '{proc.name}' is due in less than 48 hours with high risk of missing deadline.",
                    priority=NotificationPriority.CRITICAL,
                    channels=channels,
                    process_id=proc.id,
                )
                
                dispatcher = NotificationDispatcher(db)
                dispatcher.dispatch(payload)
    except Exception as e:
        logger.error("[Scheduler] Error checking deadline risks: %s", e)
    finally:
        db.close()


def send_weekly_summary(get_db_session_fn):
    """Computes completion statistics for the previous week and alerts the user."""
    db = get_db_session_fn()
    try:
        from database.models import DbTimeSlice, DbAdaptiveProfile
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        
        slices = db.query(DbTimeSlice).filter(
            DbTimeSlice.end_time >= one_week_ago,
            DbTimeSlice.status.in_(["Completed", "Abandoned"])
        ).all()
        
        completed = [s for s in slices if s.status == "Completed"]
        total = len(slices)
        
        if total > 0:
            rate = (len(completed) / total) * 100
            hours = sum(s.duration_hours for s in completed)
            msg = f"Last week summary: You completed {len(completed)}/{total} focus sessions ({rate:.1f}%) totaling {hours:.1f} hours."
        else:
            msg = "Last week summary: No focus sessions recorded."
            
        profile = db.query(DbAdaptiveProfile).filter(
            DbAdaptiveProfile.operator_id == "default_operator"
        ).first()
        
        channels = [NotificationChannel.DESKTOP]
        if profile and profile.notification_prefs:
            prefs = json.loads(profile.notification_prefs)
            if prefs.get("telegram_chat_id"):
                channels.append(NotificationChannel.TELEGRAM)

        payload = NotificationPayload(
            notification_type=NotificationType.WEEKLY_SUMMARY,
            title="Weekly Focus Digest",
            message=msg,
            priority=NotificationPriority.NORMAL,
            channels=channels,
        )
        
        dispatcher = NotificationDispatcher(db)
        dispatcher.dispatch(payload)
    except Exception as e:
        logger.error("[Scheduler] Error sending weekly summary: %s", e)
    finally:
        db.close()
