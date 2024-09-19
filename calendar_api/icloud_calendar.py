import caldav
import datetime
import os
import time
import ctypes
from dotenv import load_dotenv

load_dotenv()

def create_event(events):
    caldav_url = os.getenv("icloud_caldav_url")
    username = os.getenv("icloud_username")
    password = os.getenv("icloud_password")

    with caldav.DAVClient(url=caldav_url, username=username, password=password) as client:
        my_principal = client.principal()
        calendars = my_principal.calendars()

        if not calendars:
            raise Exception("No calendars found.")

        calendar = calendars[0]
        
        for event in events:
            start_date = datetime.datetime.strptime(event['start_date'], "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(event['end_date'], "%Y-%m-%d %H:%M")
            title = event['event_name_and_venue']

            repeat_weekly = event.get('repeat_weekly', False)
            rrule = None
            if repeat_weekly:
                rrule = {'FREQ': 'WEEKLY'}

            print(f"Creating event: {title} from {start_date} to {end_date}")

            calendar.save_event(
                dtstart=start_date, 
                dtend=end_date, 
                summary=title, 
                rrule=rrule
            )

if __name__ == "__main__":
    events = [
        {
            "event_name_and_venue": "Do the needful",
            "start_date": "2024-09-20 08:00",
            "end_date": "2024-09-20 10:00",
            "repeat_weekly": True
        }
    ]
    create_event(events)