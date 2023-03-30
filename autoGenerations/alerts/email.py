import json
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def send_mail(subject: str, message: str,
              server="smtp.gmail.com", port=587, send_from='auto.generations.shop@gmail.com',
              username='auto.generations.shop@gmail.com',
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from collection_name
        subject (str): message title
        message (str): message body
        server (str): mail server host collection_name
        port (int): port number
        username (str): server auth username
        use_tls (bool): use TLS mode
    """
    with open(os.path.join(PROJECT_DIR, 'email_secrets.json'), 'r') as f:
        email_info = json.load(f)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ", ".join(email_info['RECIPIENTS'])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, email_info['APP_PASSWORD'])
    smtp.sendmail(send_from, email_info['RECIPIENTS'], msg.as_string())
    smtp.quit()
