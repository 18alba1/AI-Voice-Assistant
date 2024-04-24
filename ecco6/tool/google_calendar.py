import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
from tzlocal import get_localzone

class GetEventsByDateInput(BaseModel):
    date: str = Field(description="The date in YYYY-MM-DD format.")

def get_events_by_date(date: str, google_credentials) -> str:
    split_date = date.split('-')

    event_date = datetime(
        int(split_date[0]),  # YYYY
        int(split_date[1]),  # MM
        int(split_date[2]),  # DD
        00,  # HH
        00,  # MM
        00,  # SS
        0,
        tzinfo=get_localzone()
    ).isoformat()

    end_time = datetime(
        int(split_date[0]),
        int(split_date[1]),
        int(split_date[2]),
        23,
        59,
        59,
        999999,
        tzinfo=get_localzone()
    ).isoformat()

    service = build("calendar", "v3", credentials=google_credentials)
    events_result = service.events().list(calendarId='primary', timeMin=event_date,timeMax=end_time).execute()
    all_events = events_result.get('items', [])
    return '\n'.join(
        [json.dumps({key: event[key] for key in ["summary", "start", "end"]})
         for event in all_events]
    )

class AddEventInput(BaseModel):
    title: str = Field(description="The title of the event.")
    start_time: str = Field(description="The start time of the event.")
    end_time: str = Field(description="The end time of the event.")

def add_event(title: str, start_time: str, end_time: str, google_credentials) -> str:
    service = build("calendar", "v3", credentials=google_credentials)
    
    timezone = str(get_localzone())
    
    event = {
        'summary': title,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
