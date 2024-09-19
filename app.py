from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import autocalendar  
import json
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET'])
def index():
    events_id = request.args.get('events_id')
    return render_template('index.html', events_id=events_id)

# First step: Upload file or text, process and return events as response
@app.route('/upload', methods=['POST'])
def upload_file():
    text_input = request.form.get('textInput')
    calendar = request.form.get('calendar')
    start_date = request.form.get('startDate')
    file = request.files.get('fileInput')

    response = None
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        if file.filename.endswith('.txt'):
            response = autocalendar.process_text(file_path, start_date)
        else:
            response = autocalendar.process_image(file_path, start_date)
    elif text_input:
        temp_text_file = os.path.join(app.config['UPLOAD_FOLDER'], 'input.txt')
        with open(temp_text_file, 'w') as f:
            f.write(text_input)
        response = autocalendar.process_text(temp_text_file, start_date)
    else:
        flash('Please provide either text input or upload a file.', 'error')
        return redirect(url_for('index'))

    if isinstance(response, str):
        try:
            response = json.loads(response)  # Ensure it's a Python list
        except json.JSONDecodeError as e:
            return jsonify({"error": "Invalid JSON format returned from processing."}), 400

    # Store the events along with the calendar in temporary storage
    events_id = str(uuid.uuid4())
    app.config.setdefault('EVENTS_STORAGE', {})
    app.config['EVENTS_STORAGE'][events_id] = {'events': response, 'calendar': calendar}

    # Return the events and events_id to the frontend
    return jsonify({'events': response, 'events_id': events_id})

# Second step: Confirm and submit events to calendar
@app.route('/confirm', methods=['POST'])
def confirm_events():
    response = request.form.get('response')
    calendar = request.form.get('calendar')

    if response:
        events = json.loads(response)  # Load the updated events from the hidden input

        print(f"Submitting events to calendar: {calendar}")

        try:
            autocalendar.submit_to_calendar(events, calendar)
            return jsonify({"success": True, "message": "Events successfully processed and added to the calendar!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error submitting events to calendar: {e}"})

    return jsonify({"success": False, "message": "No events to submit."})

@app.route('/upload_from_shortcut', methods=['POST'])
def upload_from_shortcut():
    file = request.files.get('image')
    calendar = request.form.get('calendar')
    start_date = request.form.get('startDate')

    print("upload_from_shortcut")
    print(f"Calendar: {calendar}, Start Date: {start_date}")

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        response = autocalendar.process_image(file_path, start_date)

        if isinstance(response, str):
            try:
                response = json.loads(response)  # Ensure it's a Python list
            except json.JSONDecodeError:
                print("Invalid JSON format returned from processing.")
                return jsonify({"error": "Invalid JSON format returned from processing."}), 400

        # Store the events along with the calendar in temporary storage
        events_id = str(uuid.uuid4())
        app.config.setdefault('EVENTS_STORAGE', {})
        app.config['EVENTS_STORAGE'][events_id] = {'events': response, 'calendar': calendar}

        # Return the URL with the unique identifier
        url = url_for('index', events_id=events_id, _external=True)
        
        print(f"URL: {url}")

        return jsonify({'url': url}), 200

    else:
        print("No image uploaded")
        return jsonify({'error': 'No image uploaded'}), 400

@app.route('/get_events', methods=['GET'])
def get_events():
    events_id = request.args.get('events_id')
    if events_id:
        data = app.config.get('EVENTS_STORAGE', {}).get(events_id)
        try:
            if data:
                events = data['events']
                calendar = data.get('calendar', '')
                return jsonify({'success': True, 'events': events, 'calendar': calendar})
            else:
                return jsonify({'success': False, 'message': 'Invalid or expired events ID.'})
        except Exception as e:
            print(f"Error getting events: {e}")
            print(data)
            return jsonify({'success': False, 'message': 'An error occurred while retrieving events.'})
    else:
        return jsonify({'success': False, 'message': 'No events ID provided.'})

if __name__ == '__main__':
    app.run(debug=True)

# gunicorn --bind 0.0.0.0:8000 app:app
