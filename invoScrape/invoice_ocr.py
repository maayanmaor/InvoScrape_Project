import requests
import logging
import json
import io
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level


def process_file(file_path):
    logging.info('Processing file...')
    url = 'https://app.nanonets.com/api/v2/OCR/Model/de0f441f-f6fa-42bb-bcb4-5b438657e3fe/LabelFile/?async=false'

    data = {'file': open(file_path, "rb")}

    response = requests.post(url, auth=requests.auth.HTTPBasicAuth('d66eaf92-c5af-11ed-8181-9a1d65f73763', ''),
                             files=data)

    json_str = response.text

    desired_keys = ['input', 'Card_Tender', 'Cash_Tender', 'currency', 'Date', 'Merchant_Address',
                    'Merchant_Name', 'Merchant_Phone', 'Receipt_Number', 'Subtax', 'Tax_Amount',
                    'Total_Amount']

    json_dict = json.loads(json_str)
    result_dict = {}

    if 'result' in json_dict and json_dict['result']:
        for item in json_dict['result'][0]['prediction']:
            if 'label' in item and item['label'] in desired_keys:
                result_dict[item['label']] = item['ocr_text']
        if 'input' in json_dict['result'][0]:
            result_dict['input'] = json_dict['result'][0]['input']

    logging.info('File processing complete.')
    print(result_dict)
    return result_dict


def dict_post(filename, result_dict):
    # Writing to database the file info.
    url = 'http://localhost:5000/write_file_info'
    headers = {'Content-Type': 'application/json'}
    data = {
        'filename': filename,
        'fileinfo': result_dict
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))


def send_email(result_dict, user_email):
    # Create Excel file in memory
    logging.info('Creating EXCEL file...')
    excel_data = io.BytesIO()
    df = pd.DataFrame.from_dict(result_dict, orient='index', columns=['value'])
    df.index.name = 'key'
    df.reset_index(inplace=True)
    df.to_excel(excel_data, index=False)
    logging.info('EXCEL file created.')

    logging.info('Sending email...')
    sender_email = 'invoscrape9@gmail.com'
    sender_password = 'c t i p h p i o e j t n z c i s'
    recipient_email = user_email

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Invoice OCR Results'

    # attach the file
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(excel_data.getvalue())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', 'attachment', filename='invoice_results.xlsx')
    message.attach(p)

    # send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)
        text = message.as_string()
        smtp_server.sendmail(sender_email, recipient_email, text)
        logging.info('Email sent.')
