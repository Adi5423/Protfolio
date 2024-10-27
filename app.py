from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/components')
def components():
    return render_template('components.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
