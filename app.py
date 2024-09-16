from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import autocalendar  
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

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
            response = autocalendar.process_text(file_path, start_date, calendar)
        else:
            response = autocalendar.process_image(file_path, start_date, calendar)
    elif text_input:
        temp_text_file = os.path.join(app.config['UPLOAD_FOLDER'], 'input.txt')
        with open(temp_text_file, 'w') as f:
            f.write(text_input)
        response = autocalendar.process_text(temp_text_file, start_date, calendar)
    else:
        flash('Please provide either text input or upload a file.', 'error')
        return redirect(url_for('index'))

    if isinstance(response, str):
        try:
            response = json.loads(response)  # Ensure it's a Python list
        except json.JSONDecodeError as e:
            return jsonify({"error": "Invalid JSON format returned from processing."}), 400
    
    return jsonify(response)

# Second step: Confirm and submit events to calendar
@app.route('/confirm', methods=['POST'])
def confirm_events():
    response = request.form.get('response')

    if response:
        events = json.loads(response)  # Load the updated events from the hidden input
        calendar = request.form.get('calendar')
        try:
            autocalendar.submit_to_calendar(events, calendar) 
            return jsonify({"success": True, "message": "Events successfully processed and added to the calendar!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error submitting events to calendar: {e}"})

    return jsonify({"success": False, "message": "No events to submit."})

if __name__ == '__main__':
    app.run(debug=True)

# gunicorn --bind 0.0.0.0:8000 app:app
