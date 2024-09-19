import time
import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from IPython.display import Image, display
import base64

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

template = '''
Your task is to extract all events and output them in JSON format.
Example:
[
    {{
        "event_name_and_venue": "ELC2011 SEM002 DE402",
        "start_date": "2024-09-02 18:30",
        "end_date": "2024-09-02 21:20",
        "repeat_weekly": True
    }},
    {{
        "event_name_and_venue": "COMP2011 Quiz 1 N001/N002/N003",
        "start_date": "2024-10-04 19:00",
        "end_date": "2024-10-04 20:00",
        "repeat_weekly": False
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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_events(response):
    if response.startswith('```'):
        response = '\n'.join(response.split('\n')[1:])
    if response.endswith('```'):
        response = '\n'.join(response.split('\n')[:-1])
    
    try:
        events = json.loads(response) 
        # print(f"Events: {events}")
        return events  
    except Exception as e:
        print(f"Error parsing response: {e}")
        raise

def submit_to_calendar(events, calendar = "iCloud"):
    if calendar == "MacOS":
        from calendar_api.macos_calendar import create_event
    elif calendar == "iCloud":
        from calendar_api.icloud_calendar import create_event
    else:
        raise ValueError(f"Unknown calendar: {calendar}")
    
    create_event(events)

def process_text(text_path, date):
    with open(text_path, 'r') as f:
        text = f.read()
        
    prompt = PromptTemplate.from_template(text + '\n' + template)
    parser = StrOutputParser()
    chain = prompt | llm | parser
    response = chain.invoke({"text": text, "date": date})
    return response

def process_image(image_path, date):
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
    return response

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-T', '--text', type=str, help='Path to the input text file')
    group.add_argument('-I', '--image', type=str, help='Path to the input image file')
    parser.add_argument('-D', '--date', type=str, default='2024-09-02', help='Date to start the weekly recurring events')
    parser.add_argument('-C', '--calendar', type=str, default='iCloud', help='Calendar to add events to')

    args = parser.parse_args()

    if args.image:
        process_image(args.image, args.date, args.calendar)
    else:
        process_text(args.text, args.date, args.calendar)
