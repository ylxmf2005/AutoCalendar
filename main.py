import ctypes
import time
import os
import json
import sys
import argparse
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from IPython.display import Image, display, Audio, Markdown
import base64

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

llm = ChatOpenAI(model="gpt-4o")

parser = argparse.ArgumentParser(description='Process some integers.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-T', '--text', type=str, help='Path to the input text file')
group.add_argument('-I', '--image', type=str, help='Path to the input image file')
parser.add_argument('-D', '--date', type=str, default='2024-09-02', help='Date to start the weekly recurring events')
parser.add_argument('-C', '--calendar', type=str, default='Apple', help='Calender to add events to')


args = parser.parse_args()

template = '''
Your task is to extract all events and output them in JSON format.
Example:
[
    {{
        "event_name_and_venue": "ELC2011 SEM002 DE402",
        "start_date": "2024-09-02 18:30",
        "end_date": "2024-09-02 21:20",
        "repeat_weekly": true
    }},
    {{
        "event_name_and_venue": "COMP2011 Quiz 1 N001/N002/N003",
        "start_date": "2024-10-04 19:00",
        "end_date": "2024-10-04 20:00",
        "repeat_weekly": false
    }},
    ...
]

Requirements:
1. The `event_name_and_venue` must include a concise event name and accurate event venue(location).
2. The `start_date` and `end_date` should follow the "YYYY-MM-DD HH:MM" format.
3. Please set `repeat_weekly` to true for weekly recurring events, and false for non-recurring events.
4. {date} is Monday, please start from {date} for weekly recurring events. That is, if an weekly recurring event starts on Monday, its start_date should be {date}. If an weekly recurring event starts on Tuesday, its start_date should be the next day of {date}, and so on.
5. For unknown start_date or TBA events, please ignore them. 
6. If start_date is known but the end_date is unknown, please set the end_date to the same as the start_date.

Please start your response with "[" and end with "]".
'''

parser = StrOutputParser()
date = args.date

def get_events(response):
    if response.startswith('```'):
        response = '\n'.join(response.split('\n')[1:])
    if response.endswith('```'):
        response = '\n'.join(response.split('\n')[:-1])
    print(response)

    input("Press Enter to continue...")

    try:
        events = json.loads(response) 
        return events  
    except Exception as e:
        print(e)
        exit(0)

def process_apple_calendar(response):
    events = get_events(response)
    
    lib = ctypes.CDLL('./calendar_api/apple_calendar.dylib')
    lib.create_apple_calendar_event.argtypes = [ctypes.c_char_p, ctypes.c_double,     ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
    lib.create_apple_calendar_event.restype = None

    for event in events:
        title = event['event_name_and_venue'].encode('utf-8')
        start_date = time.mktime(time.strptime(event['start_date'],     "%Y-%m-%d %H:%M"))
        end_date = time.mktime(time.strptime(event['end_date'], "%Y-%m-%d   %H:%M"))
        print(f"Creating event: {title} from {start_date} to {end_date}")
        add_alarm = True
        repeat_weekly = event['repeat_weekly']
        
        lib.create_apple_calendar_event(title, start_date, end_date, add_alarm, repeat_weekly)

    input("Press Enter to exit...")

def process_text(text_path):
    with open(text_path, 'r') as f:
        text = f.read()
        
    prompt = PromptTemplate.from_template(text + '\n' + template)
    chain = prompt | llm | parser

    response = chain.invoke({"text": text, "date": date})
    if args.calendar == 'Apple':
        process_apple_calendar(response)

def process_image(image_path):
    display(Image(image_path))
    
    base64_image = encode_image(image_path)
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": template.format(date=date)},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ]
    
    response = llm.invoke(messages)
    if args.calendar == 'Apple':
        process_apple_calendar(response.content)

if args.image:
    process_image(args.image)
else:
    process_text(args.text)
