# AutoCalendar
Automatically extracts various event information from text or image and generates calendar events with concise titles, dates, and times, including alarms and weekly recurrence.

Support calendar: Apple Calendar(MacOS)

### Demo

![](https://s2.loli.net/2024/09/16/igWw3rokS2hpLtX.png)

![](https://s2.loli.net/2024/09/16/R7FyrDQEJ4Z2f8h.png)



### Usage

```bash
pip install -r requirements.txt
```

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```



### To Do List

- [x] Add Website GUI
- [ ] Add integration with iOS Shortcuts
- [ ] Add Support for Outlook Calendar
- [ ] Add Support for Google Calendar
- [ ] Add Support for iClould Calendar
- [ ] Add database and account login function.
- [ ] Add GUI for Windows, MacOS
