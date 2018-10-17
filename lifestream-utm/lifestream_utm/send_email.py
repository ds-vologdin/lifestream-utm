import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
import logging

from settings.private_settings import SMTP_CONFIG


logger = logging.getLogger(__name__)


def send_email(receivers, text, subject, filename=None, use_tls=False):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SMTP_CONFIG['sender']
    msg['To'] = ', '.join(receivers)
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(text))

    if filename:
        attachment = MIMEBase('application', "octet-stream")
        try:
            with open(filename, "rb") as fh:
                data = fh.read()

            attachment.set_payload(data)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition', 'attachment',
                filename=os.path.basename(filename)
            )
            msg.attach(attachment)
        except IOError:
            error = "Error opening attachment file {}".format(filename)
            logger.error(error)
            return -1

    with smtplib.SMTP(host=SMTP_CONFIG['host'], port=SMTP_CONFIG['port']) as s:
        s.ehlo()
        if use_tls:
            s.starttls()
        s.login(SMTP_CONFIG['user'], SMTP_CONFIG['passwd'])
        s.sendmail(SMTP_CONFIG['sender'], receivers, msg.as_string())


def send_report_to_email(receivers, status_change_user):
    if not receivers:
        return
    receivers = receivers.replace(',', ' ').split()
    subject = 'lifestream report'
    message = ''
    for user in status_change_user:
        message += '{0[user].login} {0[user].full_name}: {0[status_lifestream]} -> {0[status_utm]}\n'.format(
            user
        )
    if message:
        send_email(receivers, message, subject)
        logger.info('send email to {}'.format(','.join(receivers)))
