import ctypes
import os
import time

def create_event(events):    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dylib_path = os.path.join(current_dir, 'apple_calendar.dylib')
    lib = ctypes.CDLL(dylib_path)    
    lib.create_event.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    lib.create_event.restype = None
    
    for event in events:
        title = event['event_name_and_venue'].encode('utf-8')
        start_date = time.mktime(time.strptime(event['start_date'], "%Y-%m-%d %H:%M"))
        end_date = time.mktime(time.strptime(event['end_date'], "%Y-%m-%d %H:%M"))
        add_alarm = True
        repeat_weekly = event['repeat_weekly']
        
        print(f"Creating event: {title.decode()} from {start_date} to {end_date}")
        lib.create_event(title, start_date, end_date, add_alarm, repeat_weekly)
    
    