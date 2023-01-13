import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import logging

# Import logger
log = logging.getLogger()


def send(smtp_dict, mail_dict):
    """
    Send mail using SMTP configurations.

    :param smtp_dict: A dictionary with the following keys:
        - sender: The email address of the sender.
        - password: The password of the sender's email address.
        - host: The hostname of the SMTP server.
        - port: The port of the SMTP server.

    :param mail_dict: A dictionary with the following keys:
        - subject: The subject of the mail.
        - recipients: A list of the email addresses of the receivers.
        - cc: A list of the email addresses in the CC.
        - attachments: A list of the paths of the attachments.
        - message: The message to be sent.

    :return: None
    """

    # Create message
    msg = MIMEMultipart()

    # Set the subject of the mail
    msg['Subject'] = Header(mail_dict['subject'], 'utf-8')

    # Set the sender mail
    msg['From'] = formataddr((
        str(Header(mail_dict['subject'], 'utf-8')),
        smtp_dict['sender']
    ))

    # Send the recipients
    msg['To'] = ', '.join(mail_dict['recipients'])

    # Set the CCs
    msg['Cc'] = ', '.join(mail_dict['cc'])

    # Set the HTML message body
    body = MIMEMultipart('alternative')
    body.attach(MIMEText(mail_dict['message'], 'html'))
    msg.attach(body)

    # Set the attachments
    for file in mail_dict['attachments']:
        with open(file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file}",
        )
        msg.attach(part)

    # Create server object with SSL option
    server = smtplib.SMTP_SSL(smtp_dict['hostname'], smtp_dict['port'])

    # Perform operations via server
    server.login(smtp_dict['sender'], str(smtp_dict['password']))
    server.sendmail(
        smtp_dict['sender'],
        mail_dict['recipients'] + mail_dict['cc'],
        msg.as_string()
    )
    server.quit()


if __name__ == "__main__":

    smtp_dict = {
        'sender': 'support@automagicdeveloper.com',
        'password': 'ots@l4cG',
        'sender_title': 'AutoMagic Developer Support',
        'hostname': 'smtp.zoho.com',
        'port': 465,
    }

    mail_dict = {
        'subject': "Database Daily Backup Report",
        'recipients': [
            'muhammadabdelgawwad@gmail.com',
            'mohamed@automagicdeveloper.com',
        ],
        'cc': [
            'muhammadabdelgawwad@gmail.com',
            'mohamed@automagicdeveloper.com',
        ],
        'attachments': [
            'test1.txt',
            'test2.txt',
        ],
        'message': "<b>Test Message<b/><br>Thanks and best regards",
    }

    send(smtp_dict, mail_dict)
