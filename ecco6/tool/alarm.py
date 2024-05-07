from firebase_admin import db
from langchain.pydantic_v1 import BaseModel, Field
import streamlit as st
import time
import datetime
import pyttsx3
import threading

class SetAlarmInput(BaseModel):
    day: str = Field(description="The day to set the alarm for.")
    date: str = Field(description="The date to set the alarm for.")
    clock: str = Field(description="The time to set the alarm for.")

# Implement the alarm function
def set_alarm(alarm_info: SetAlarmInput) -> str:
    # Construct the alarm data
    alarm_data = {
        "day": alarm_info.day,
        "date": alarm_info.date,
        "clock": alarm_info.clock
    }

    # Push the alarm data to Firebase
    db.reference(f'/users/{st.session_state.email.replace(".", "_")}/alarms').push(alarm_data)

    return "Alarm set successfully."



def check_and_notify_alarms(email):
    while True:
        # Get the current time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Query Firebase for alarms
        user_email = email.replace(".", "_")
        alarms_ref = db.reference(f'/users/{user_email}/alarms')
        alarms = alarms_ref.order_by_key().end_at(current_time).get()

        # Print available alarms
        if alarms:
            print("Available alarms:")
            for key, value in alarms.items():
                print(f"Alarm ID: {key}, Time: {value['clock']}, Day: {value['day']}, Date: {value['date']}")

        # If there are any alarms that have passed, notify and remove them
        if alarms:
            engine = pyttsx3.init()

            for key, value in alarms.items():
                alarm_time = datetime.datetime.strptime(f"{value['date']} {value['clock']}", "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
                print(alarm_time)
                if alarm_time <= current_time:
                    engine.say(f"Alarm at {value['clock']} on {value['day']}, {value['date']} has passed.")
                    print(f"Alarm at {value['clock']} on {value['day']}, {value['date']} has passed.")
                    alarms_ref.child(key).delete()
                else:
                    print(f"Alarm {alarm_time} is still pending.")

            engine.runAndWait()
        # Wait for some time before checking again (e.g., every 60 seconds)
        time.sleep(60)