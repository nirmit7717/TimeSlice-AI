"""Calendar API Router — local event store + Google Calendar stubs.

Endpoints:
  GET    /api/v1/calendar/events              → List events in date range
  POST   /api/v1/calendar/events              → Create manual event
  PUT    /api/v1/calendar/events/{id}         → Update event
  DELETE /api/v1/calendar/events/{id}         → Delete event
  GET    /api/v1/calendar/google/auth-url     → [STUB] Returns OAuth URL
  POST   /api/v1/calendar/google/callback     → [STUB] OAuth token exchange
  POST   /api/v1/calendar/sync/google         → [STUB] Trigger Google sync

Note: Google OAuth stubs are ready to receive real client credentials.
Integrate by setting GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET env vars
and implementing the OAuth flow in packages/integrations/google/.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from database.models import DbCalendarEvent, DbTimeSlice

router = APIRouter(tags=["calendar"])


# ── Request / Response schemas ─────────────────────────────────────────────────

class CalendarEventCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    color: str = "primary"
    is_rest_period: bool = False


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None


class CalendarEventOut(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    location: str
    is_google_event: bool
    is_rest_period: bool
    color: str
    source: str  # "local" | "google" | "execution_plan"

    class Config:
        from_attributes = True


# ── Helpers ────────────────────────────────────────────────────────────────────

def _db_event_to_out(ev: DbCalendarEvent) -> CalendarEventOut:
    source = "google" if ev.is_google_event else "rest_period" if ev.is_rest_period else "local"
    return CalendarEventOut(
        id=ev.id,
        title=ev.title,
        start_time=ev.start_time,
        end_time=ev.end_time,
        description=ev.description,
        location=ev.location,
        is_google_event=ev.is_google_event,
        is_rest_period=ev.is_rest_period,
        color=ev.color,
        source=source,
    )


# ── Calendar CRUD endpoints ────────────────────────────────────────────────────

@router.get("/events", response_model=List[CalendarEventOut])
def list_events(
    start: Optional[datetime] = Query(None, description="Range start (ISO 8601)"),
    end: Optional[datetime] = Query(None, description="Range end (ISO 8601)"),
    include_time_slices: bool = Query(True, description="Include scheduled execution windows"),
    db: Session = Depends(get_db),
):
    """
    Returns all calendar events in the requested date range.
    Merges local/Google events with scheduled execution windows (time slices).
    """
    query = db.query(DbCalendarEvent)
    if start:
        query = query.filter(DbCalendarEvent.end_time >= start)
    if end:
        query = query.filter(DbCalendarEvent.start_time <= end)
    events = query.order_by(DbCalendarEvent.start_time).all()
    result = [_db_event_to_out(e) for e in events]

    # Overlay scheduled execution windows as calendar events
    if include_time_slices:
        slice_query = db.query(DbTimeSlice).filter(DbTimeSlice.status.in_(["Scheduled", "Active"]))
        if start:
            slice_query = slice_query.filter(DbTimeSlice.end_time >= start)
        if end:
            slice_query = slice_query.filter(DbTimeSlice.start_time <= end)

        for ts in slice_query.order_by(DbTimeSlice.start_time).all():
            result.append(CalendarEventOut(
                id=ts.id,
                title=f"Focus: {ts.process_id[:8]}…" if ts.process_id else "Scheduled Focus",
                start_time=ts.start_time,
                end_time=ts.end_time,
                description=f"Execution window — {ts.duration_hours}h focus session",
                location="",
                is_google_event=False,
                is_rest_period=False,
                color="primary",
                source="execution_plan",
            ))

    return sorted(result, key=lambda e: e.start_time)


@router.post("/events", response_model=CalendarEventOut, status_code=201)
def create_event(body: CalendarEventCreate, db: Session = Depends(get_db)):
    """Creates a manual local calendar event."""
    ev = DbCalendarEvent(
        id=str(uuid.uuid4()),
        title=body.title,
        start_time=body.start_time,
        end_time=body.end_time,
        description=body.description,
        location=body.location,
        color=body.color,
        is_rest_period=body.is_rest_period,
        is_google_event=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return _db_event_to_out(ev)


@router.put("/events/{event_id}", response_model=CalendarEventOut)
def update_event(event_id: str, body: CalendarEventUpdate, db: Session = Depends(get_db)):
    """Updates a local calendar event."""
    ev = db.query(DbCalendarEvent).filter(DbCalendarEvent.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    if body.title is not None:
        ev.title = body.title
    if body.start_time is not None:
        ev.start_time = body.start_time
    if body.end_time is not None:
        ev.end_time = body.end_time
    if body.description is not None:
        ev.description = body.description
    if body.location is not None:
        ev.location = body.location
    if body.color is not None:
        ev.color = body.color
    ev.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ev)
    return _db_event_to_out(ev)


@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str, db: Session = Depends(get_db)):
    """Deletes a local calendar event."""
    ev = db.query(DbCalendarEvent).filter(DbCalendarEvent.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(ev)
    db.commit()


# ── Google Calendar stubs ──────────────────────────────────────────────────────

@router.get("/google/auth-url")
def get_google_auth_url():
    """
    [STUB] Returns the Google OAuth 2.0 authorization URL.
    Integrate by setting GOOGLE_CLIENT_ID env var and implementing
    packages/integrations/google/google_calendar.py OAuth flow.
    """
    import os
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        return {
            "status": "not_configured",
            "message": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars to enable Google Calendar sync.",
            "auth_url": None,
        }
    # When credentials are present, build the OAuth URL
    redirect_uri = "http://localhost:8000/api/v1/calendar/google/callback"
    scopes = "https://www.googleapis.com/auth/calendar.readonly"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scopes}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return {"status": "configured", "auth_url": auth_url}


@router.post("/google/callback")
def google_oauth_callback(code: str, db: Session = Depends(get_db)):
    """
    [STUB] Handles the OAuth 2.0 authorization code callback from Google.
    When GOOGLE_CLIENT_ID/SECRET are set, exchanges the code for tokens
    and stores them for use in subsequent sync calls.
    """
    import os
    if not os.getenv("GOOGLE_CLIENT_ID"):
        return {
            "status": "not_configured",
            "message": "Google Calendar credentials not configured. Set GOOGLE_CLIENT_ID env var.",
        }
    # TODO: Exchange code for access/refresh tokens via Google token endpoint
    # Store tokens securely for the authenticated user
    return {"status": "stub", "message": "OAuth callback handler ready — credentials pending."}


@router.post("/sync/google")
def sync_google_calendar(db: Session = Depends(get_db)):
    """
    [STUB] Triggers a Google Calendar sync.
    When credentials are available, fetches events from the user's primary
    calendar and upserts them into DbCalendarEvent.
    """
    import os
    if not os.getenv("GOOGLE_CLIENT_ID"):
        return {
            "status": "not_configured",
            "synced_count": 0,
            "message": "Google Calendar not connected. Use GET /api/v1/calendar/google/auth-url to authenticate.",
        }
    # TODO: Call GoogleCalendarClient.get_events() and upsert into DbCalendarEvent
    return {"status": "stub", "synced_count": 0, "message": "Sync ready — credentials pending."}
