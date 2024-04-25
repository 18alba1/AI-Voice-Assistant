import base64
import json
from datetime import datetime
from googleapiclient.discovery import build
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
from tzlocal import get_localzone
from email.message import EmailMessage
from typing import Dict
import re

#================== CALENDAR ==================================

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

class RemoveEventInput(BaseModel):
    event_title: str = Field(description="The title of the event.")
    date: str = Field(description="The date in YYYY-MM-DD format.")

def get_eventID(date: str, google_credentials, event_title: str) -> str:
    split_date = date.split('-')

    event_date = datetime(
        int(split_date[0]),  
        int(split_date[1]), 
        int(split_date[2]),
        00,  
        00,
        00,
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
    events_result = service.events().list(calendarId='primary', timeMin=event_date, timeMax=end_time).execute()
    all_events = events_result.get('items', [])
    
    event_ids = []

    for event in all_events:
        if 'summary' in event and event['summary'].lower() == event_title.lower():
            event_ids.append(event['id'])

    if event_ids:
        return event_ids[0]
    else:
        return None

def remove_event(event_title: str, date: str, google_credentials) -> str:
    event_id = get_eventID(date, google_credentials, event_title)
    
    if event_id:
        try:
            service = build("calendar", "v3", credentials=google_credentials)
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return f"Event '{event_title}' deleted successfully"
        except Exception as e:
            return f"An error occurred while deleting event '{event_title}': {str(e)}"
    else:
        return f"No event with title '{event_title}' found for the specified date"
    
class GetUnreadMessagesInput(BaseModel):
    pass 

#======================= GMAIL =======================

def get_unread_messages(google_credentials) -> str:
    creds = google_credentials
    service = build('gmail', 'v1', credentials=creds)

    query = 'in:inbox is:unread -category:(promotions OR social)'
    unread_msgs = service.users().messages().list(userId='me', q=query).execute()

    messages = unread_msgs.get('messages', [])
    if not messages:
        return "You have no unread messages in your primary inbox."

    unread_info = ""
    for msg in messages:
        msg_info = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_info['payload']['headers']
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown')
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        snippet = msg_info['snippet']
        unread_info += f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n\n"

    return unread_info

class SendEmailInput(BaseModel):
    recipient: str = Field(description="The email address of the recipient.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")

def preprocess_recipient(recipient: str) -> str:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    matches = re.findall(email_pattern, recipient)

    for match in matches:
        recipient = recipient.replace(match, match.replace(" at ", "@").replace(" dot ", "."))

    return recipient

def send_email(recipient: str, subject: str, body: str, google_credentials) -> str:
    recipient = preprocess_recipient(recipient)

    email_msg = EmailMessage()
    email_msg['To'] = recipient
    email_msg['Subject'] = subject
    email_msg.set_content(body)

    try:
        service = build('gmail', 'v1', credentials=google_credentials)
        message = {'raw': base64.urlsafe_b64encode(email_msg.as_bytes()).decode()}
        sent_message = service.users().messages().send(userId='me', body=message).execute()

        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred while sending the email: {str(e)}"
