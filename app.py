from flask import Flask, render_template, request, redirect, jsonify
import sys
import os
import csv
# Use process_single_message instead of GenerateGroq
from projects.assistant.Aistie import process_single_message
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the projects directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'projects'))

app = Flask(__name__)

# Remove debug mode for production
app.debug = False

# Your existing route handlers...
@app.route('/submit_form', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict()
        write_to_csv(data)
        return redirect('/thankyou.html')
    else:
        return 'Something went wrong. Please try again.'

def write_to_file(data):
    with open('database.txt', mode='a') as database:
        email = data['email']
        subject = data['subject']
        message = data['message']
        database.write(f'\n{email},{subject},{message}')

def write_to_csv(data):
    with open('database2.csv', mode='a', newline='') as database2:
        email = data['email']
        subject = data['subject']
        message = data['message']
        csv_writer = csv.writer(database2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/process_message', methods=['POST'])
def process_message():
    message = request.json.get('message')
    logger.info(f"Received message: {message}")
    try:
        response = process_single_message(message)
        logger.info(f"Generated response: {response}")
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({'response': f"An error occurred: {str(e)}"})

@app.route('/initial_greeting')
def initial_greeting():
    greeting = "Hello! I'm Aistie, your personal AI assistant. How can I help you today?"
    logger.info("Sending initial greeting")
    return jsonify({'greeting': greeting})

@app.route('/assistant')
def assistant_page():
    logger.info("Serving assistant page")
    return render_template('assistant.html')

@app.route('/contact')
def contact():
    logger.info("Serving contact page")
    return render_template('contact.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    logger.info(f"Serving page: {page_name}")
    return render_template(page_name)

# Modified main block for production
if __name__ == '__main__':
    # Get port from environment variable (Render will set this)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)