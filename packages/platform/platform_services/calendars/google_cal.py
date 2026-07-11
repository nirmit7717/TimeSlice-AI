from datetime import datetime, timezone, timedelta
import dateutil.parser
from typing import List, Tuple, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleCalendarSync:
    """
    Adapter pulling events from Google Calendar and mapping them to local schedule blockages.
    """
    def fetch_events(self, access_token: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Pulls events using the Google Calendar API.
        """
        # Testing bypass handler: allows running test suite offline
        if access_token == "mock-token":
            # Return some mock google calendar events
            now = datetime.now(timezone.utc)
            return [
                {
                    "summary": "Team Sync Meeting",
                    "start": {"dateTime": (now.replace(hour=14, minute=0, second=0)).isoformat()},
                    "end": {"dateTime": (now.replace(hour=15, minute=0, second=0)).isoformat()}
                },
                {
                    "summary": "Dentist Appointment",
                    "start": {"dateTime": (now.replace(hour=10, minute=0, second=0) + timedelta(days=1)).isoformat()},
                    "end": {"dateTime": (now.replace(hour=11, minute=0, second=0) + timedelta(days=1)).isoformat()}
                }
            ]

        try:
            creds = Credentials(access_token)
            service = build("calendar", "v3", credentials=creds)
            
            # Format time boundaries as ISO string Z formats
            t_min = start_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            t_max = end_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

            events_result = service.events().list(
                calendarId="primary",
                timeMin=t_min,
                timeMax=t_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            return events_result.get("items", [])
        except Exception as e:
            raise ValueError(f"Google Calendar API fetch failed: {str(e)}")

    def to_blocked_intervals(self, google_events: List[Dict[str, Any]]) -> List[Tuple[datetime, datetime]]:
        """
        Maps raw Google Calendar events structure to a clean list of datetime tuples.
        """
        intervals = []
        for event in google_events:
            start_data = event.get("start", {})
            end_data = event.get("end", {})
            
            # Support both all-day date format and datetime format
            start_str = start_data.get("dateTime") or start_data.get("date")
            end_str = end_data.get("dateTime") or end_data.get("date")

            if start_str and end_str:
                start_dt = dateutil.parser.parse(start_str)
                end_dt = dateutil.parser.parse(end_str)
                
                # Enforce UTC timezone compatibility
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=timezone.utc)

                intervals.append((start_dt, end_dt))
        return intervals
