import ctypes
import time
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

prompt = PromptTemplate.from_template('''
{text}
Your task is to extract all events from the given text and output them in JSON format.
Example:
[
    {{
        "title": "ELC2011 SEM002 DE402",
        "start_date": "2024-09-02 18:30",
        "end_date": "2024-09-02 21:20"
    }},
    ...
]

Requirements:
1. For the `title`, the result should be as concise as possible, extracting the event name and location (use the course code instead of the full name to shorten the title).
2. The `start_date` and `end_date` should follow the "YYYY-MM-DD HH:MM" format.
3. {date} is Monday, please start from {date}. That is, if an event starts on Monday, its start_date should be {date}. If an event starts on Tuesday, its start_date should be the next day of {date}, and so on.


Please start your response with "[" and end with "]".
''')

# llm = ChatOpenAI(
#     model='deepseek-chat', 
#     openai_api_key=os.getenv('DEEPSEEK_API_KEY'), 
#     openai_api_base='https://api.deepseek.com',
#     max_tokens=4096
# )

llm = ChatOpenAI(model = "gpt-4")

parser = StrOutputParser()
chain = prompt | llm | parser

text = '''
Subject Code
Subject Title
Subject Group
Component Code
For Every (Week)
Start Week
End Week
Day of Week
Start Time
End Time
Venue
Teaching Staff
Remark
BME1D02	WEARABLE HEALTHCARE AND FITNESS DEVICES FOR EVERYONE	101	LEC001	1	1	13	Thu	18:30	21:20	
N003
Cheung, James ChungWai, WONG, Duo	
COMP2011	DATA STRUCTURES	1012	LAB004	1	2	13	Wed	17:30	18:20	
PQ604A
CAO, Yixin	
COMP2011	DATA STRUCTURES	1012	LEC001	1	1	13	Tue	15:30	18:20	
N002
CAO, Yixin	
COMP2012	DISCRETE MATHEMATICS	1011	LEC001	1	1	13	Thu	11:30	13:20	
HJ202
TANG, Kai Tai Jeff	
COMP2012	DISCRETE MATHEMATICS	1011	TUT001	1	2	13	Mon	10:30	11:20	
V312
TANG, Kai Tai Jeff	
COMP2021	OBJECT-ORIENTED PROGRAMMING	1011	LAB003	1	2	13	Mon	16:30	17:20	
PQ604B
YUEN, Kevin	
COMP2021	OBJECT-ORIENTED PROGRAMMING	1011	LEC001	1	1	13	Tue	08:30	11:20	
HJ202
YUEN, Kevin	
COMP2411	DATABASE SYSTEMS	1011	LAB004	1	2	13	Mon	15:30	16:20	
PQ604A
HUA, Wency, ZHOU, Alexander	
COMP2411	DATABASE SYSTEMS	1011	LEC001	1	1	13	Fri	12:30	15:20	
HJ202
HUA, Wency, ZHOU, Alexander	
ELC2011	ADVANCED ENGLISH READING AND WRITING SKILLS	139	SEM002	1	1	13	Mon	18:30	21:20	
DE402
FORRESTER Adam David	
'''

date = "2024-09-02"
response = chain.invoke({"text": text, "date" : date})
if response.startswith('```'):
    response = '\n'.join(response.split('\n')[1:])
if response.endswith('```'):
    response = '\n'.join(response.split('\n')[:-1])
print(response)

input("Press Enter to continue...")

try:
    events = json.loads(response)   
except Exception as e:
    print(e)
    exit(0)
    
lib = ctypes.CDLL('./libCalendarEvent.dylib')
lib.create_calendar_event.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double, ctypes.c_bool, ctypes.c_bool]
lib.create_calendar_event.restype = None

for event in events:
    title = event['title'].encode('utf-8')
    start_date = time.mktime(time.strptime(event['start_date'], "%Y-%m-%d %H:%M"))
    end_date = time.mktime(time.strptime(event['end_date'], "%Y-%m-%d %H:%M"))
    print(f"Creating event: {title} from {start_date} to {end_date}")
    add_alarm = True
    repeat_weekly = True
    lib.create_calendar_event(title, start_date, end_date, add_alarm, repeat_weekly)

input("Press Enter to exit...")