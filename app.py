from flask import Flask

from flask import render_template

from flask import request

from flask import redirect

import csv
app = Flask(__name__)

@app.route('/submit_form', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': #if we have post method
        data = request.form.to_dict()
        write_to_csv(data)
        return redirect('thankyou.html')
    else:
        return 'Something is wrong'

#data = {'email': 'pratik@gmail.com', 'subject': 'Pratik', 'message': 'Hi'}

def write_to_file(data):
    with open('database.txt', mode='a') as database:
        email = data['email']
        subject = data['subject']
        message = data['message']
        file = database.write(f'\n {email},{subject},{message}')


def write_to_csv(data):
    with open('database2.csv', newline='', mode='a') as database2:  # opening our database.csv file in append mode (why append mode?)

        email = data['email']  # fetching data from our data dictionary created in html form

        subject = data['subject']  # fetching subject from our data dictionary created in html form

        message = data['message']  # fetching message from our data dictionary created in html form

        # csv.writer takes some parameters- 1-file in which to write, 2 - delimiter-Line/Column breaker, 3-quotechar, 4-quoting

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


#use this rule
@app.route('/<string:page_name>')  #index.html  about.html
def html_page(page_name):
    return render_template(page_name)  #index.html  about.html