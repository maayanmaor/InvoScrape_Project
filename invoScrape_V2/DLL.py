import os
import smtplib
from flask import Flask, request, jsonify, render_template, session, send_file
import mysql.connector
import json
import logging
from invoice_ocr import send_email

DLL = Flask(__name__, template_folder=r"C:\test")
DLL.secret_key = "your-secret-key"  # Set secret key for session
DLL.template_engine = "jinja2"
DLL.jinja_env.auto_reload = True
DLL.config['TEMPLATES_AUTO_RELOAD'] = True

# Set the log level to DEBUG to capture all log messages
DLL.logger.setLevel(logging.DEBUG)

# Create a log formatter with the desired format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# Create a StreamHandler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the console handler to the logger
DLL.logger.addHandler(console_handler)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="main_db"
)


def check_db_connection():
    if not db.is_connected():
        db.reconnect()


# Authentication function
def authenticate(email_address, password, check_existence=False):
    cursor = db.cursor()
    query = "SELECT * FROM USERS WHERE email_address=%s"
    cursor.execute(query, (email_address,))
    user = cursor.fetchone()
    cursor.close()

    if check_existence:
        return user is not None
    else:
        if user is None or user[3] != password:
            return False
        else:
            return True


@DLL.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        check_db_connection()

        session.pop('user_email', None)

        email_address = request.form['email']
        password = request.form['password']

        # Authenticate the user
        authenticated = authenticate(email_address, password)
        if authenticated:
            # Store user data in the session
            session['user_email'] = email_address

            # Fetch user data from the database
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email_address = %s", (email_address,))
            user_data = cursor.fetchone()
            cursor.close()

            # Render the user_index template with user data
            return render_template('user_index_test.html', user_data=user_data, user_email=email_address)
        else:
            # Authentication failed
            # return jsonify({'message': 'Incorrect email or password'}), 401
            error_message = 'Incorrect email or password'
            return render_template('signin.html', error_message=error_message), 401
    else:
        # Render the login form
        return render_template('signin.html', error_message=None)


# Register function
@DLL.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        check_db_connection()

        full_name = request.form['fullname']
        company_name = request.form['companyname']
        email_address = request.form['email']
        password = request.form['password']

        # Validate form data
        if not full_name:
            error_message = "Full name is required"
            return render_template('signup.html', error_message=error_message)
        if not company_name:
            error_message = "Company name is required"
            return render_template('signup.html', error_message=error_message)
        if not email_address:
            error_message = "Email is required"
            return render_template('signup.html', error_message=error_message)
        if not password:
            error_message = "Password is required"
            return render_template('signup.html', error_message=error_message)

        # Check if the user already exists in the database
        if authenticate(email_address, password, check_existence=True):
            error_message = "User is already registered."
            return render_template('signup.html', error_message=error_message)

        # Insert the user into the database
        cursor = db.cursor()
        query = "INSERT INTO USERS (full_name, company_name, email_address, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (full_name, company_name, email_address, password))
        db.commit()
        cursor.close()

        # Redirect the user to the login page
        success_message = "You have registered successfully."
        return render_template('signin.html', success_message=success_message)
    else:
        error_message = ""  # Add this line to handle the case when the method is not POST
        return render_template('signup.html', error_message=error_message)


# Logging out function
@DLL.route('/logout', methods=['POST'])
def logout():
    check_db_connection()

    # Remove session variables for user ID and username
    session.pop('user_email', None)

    # return redirect(url_for('login'))
    return render_template('signin.html')


@DLL.route('/getInvoice', methods=['GET'])
def get_invoice():
    check_db_connection()

    # Get the file ID from the request query parameters
    file_id = request.args.get('file_id')
    DLL.logger.info('File ID: %s', file_id)

    # Define the directory where the invoice files are located
    directory = r"C:\test\files"

    # Check if the file exists in the directory
    file_path = os.path.join(directory, file_id)
    DLL.logger.info('File path: %s', file_path)

    if os.path.isfile(file_path):
        # Determine the file extension
        file_extension = os.path.splitext(file_path)[1].lower()

        # Return the file as a response with the appropriate mimetype
        if file_extension in ['.jpg', '.jpeg', '.png']:
            return send_file(file_path, mimetype='image/' + file_extension[1:])
        elif file_extension == '.pdf':
            return send_file(file_path, mimetype='application/pdf')
        else:
            DLL.logger.error('Invalid file format')
            return 'Invalid file format'
    else:
        DLL.logger.error('File not found')
        return 'File not found'


@DLL.route('/getData', methods=['GET'])
def get_files():
    check_db_connection()

    file_name = request.args.get('file_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    user_email = request.args.get('user_email')

    query = "SELECT * FROM file_info WHERE 1=1"

    if file_name:
        query += f" AND id LIKE '%{file_name}%'"

    if start_date:
        query += f" AND DATE(created_at) >= '{start_date}'"

    if end_date:
        query += f" AND DATE(created_at) <= '{end_date}'"

    if min_amount:
        query += f" AND Total_Amount >= {min_amount}"

    if max_amount:
        query += f" AND Total_Amount <= {max_amount}"

    query += f" AND id IN (SELECT CONCAT(f.id, '_', f.original_filename) FROM files f WHERE f.email = '{user_email}')"

    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        filtered_files = []
        columns = [desc[0] for desc in cursor.description]
        for row in rows:
            filtered_files.append(dict(zip(columns, row)))
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify(filtered_files)


@DLL.route('/add', methods=['POST'])
def add():
    check_db_connection()

    if request.method == 'POST':
        email = request.form['email']
        file_name = request.form['file_name']
        unique_id = request.form['unique_id']
        send_excel = request.form.get('send_email') == 'true'  # Get the value of the send_email checkbox

        # Insert the file into the database with the user's email and send_excel value
        cursor = db.cursor()
        query = "INSERT INTO files (id, original_filename, email, send_excel) VALUES (%s, %s, %s, %s)"
        print("Query:", query)
        print("Params:", (unique_id, file_name, email, send_excel))
        cursor.execute(query, (unique_id, file_name, email, send_excel))
        db.commit()
        cursor.close()
        print(cursor.rowcount, "record inserted.")

        # Fetch user data from the database
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email_address = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()

        # Render the user_index template with user data
        success_message = "The file uploaded successfully."
        return render_template('user_index_test.html', user_data=user_data, success_message=success_message)
    else:
        return render_template('signin.html')  # Redirect the user to the signin.html page


@DLL.route('/write_file_info', methods=['POST'])
def write_file_info():
    check_db_connection()

    print("Starting to write the file info into db...")
    # create a cursor
    cursor = db.cursor()

    data = request.json
    # convert the fileinfo string to a dictionary object
    try:
        fileinfo = data['fileinfo']
        if isinstance(fileinfo, str):
            fileinfo = json.loads(fileinfo)
    except (json.JSONDecodeError, KeyError) as e:
        logging.error("Error loading fileinfo data: %s", e)
        return jsonify({'message': 'invalid request data'})

    # execute the insert query
    query = "INSERT INTO file_info (id, Card_Tender, Cash_Tender, currency, Date, Merchant_Address, " \
            "Merchant_Name, Merchant_Phone, Receipt_Number, Subtax, Tax_Amount, Total_Amount) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    print("Query:", query)

    # use the `get` method to access dictionary values and handle missing keys
    params = (
        data['filename'],
        fileinfo.get('Card_Tender', ''),
        fileinfo.get('Cash_Tender', ''),
        fileinfo.get('currency', ''),
        fileinfo.get('Date', ''),
        fileinfo.get('Merchant_Address', ''),
        fileinfo.get('Merchant_Name', ''),
        fileinfo.get('Merchant_Phone', ''),
        fileinfo.get('Receipt_Number', ''),
        fileinfo.get('Subtax', ''),
        fileinfo.get('Tax_Amount', ''),
        fileinfo.get('Total_Amount', '')
    )
    print("Params:", params)

    cursor.execute(query, params)

    # commit the changes
    db.commit()

    # Check the send_excel value for the file ID in the files table
    # and sending the extracted excel if the user asked for.
    file_id_parts = data['filename'].split('_')
    file_id = file_id_parts[0]
    select_query = "SELECT email FROM files WHERE id = %s AND send_excel = true"
    cursor.execute(select_query, (file_id,))
    result = cursor.fetchone()
    if result:
        email = result[0]
        print("Email from files table:", email)

        # Check if the email is not empty and call the send_email function
        if email:
            send_email(fileinfo, email)

    # return a simple response
    return jsonify({'message': 'file info written into db successfully'})


@DLL.route('/contact', methods=['POST'])
def contact():
    check_db_connection()

    sender_email = 'invoscrape9@gmail.com'
    sender_password = 'c t i p h p i o e j t n z c i s'

    if request.method == 'POST':
        data = request.form

        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        # Set up email headers
        headers = f"From: {name} <{email}>\r\n"
        headers += f"To: {sender_email}\r\n"
        headers += f"Subject: {subject}\r\n"

        try:
            # Connect to the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)

            email_message = f"{headers}\r\n{message}"
            server.sendmail(email, sender_email, email_message)
            server.quit()

            response = {
                'success': True,
                'success_message': 'Your message has been sent. Thank you!'
            }
        except Exception as e:
            response = {
                'success': False,
                'error_message': f'Failed to send the email. Error: {str(e)}'
            }

        return json.dumps(response)


if __name__ == '__main__':
    DLL.run(debug=True, port=5000)
