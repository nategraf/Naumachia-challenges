# coding: utf-8
from os import environ
from time import sleep
import sqlite3
import logging
import smtplib
import random
import ssl
import textwrap
import math

LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')
SMTP_ADDR = environ.get('SMTP_ADDR')
SMTP_PORT = int(environ.get('SMTP_PORT', 25))
CTF_FLAG = environ.get('CTF_FLAG')
EMAILDB_PATH = environ.get('EMAILDB_PATH')
TLS_CA = environ.get('TLS_CA')

INTERMISSION_MU = int(environ.get('INTERMISSION_MU', 10))
INTERMISSION_SIGMA = int(environ.get('INTERMISSION_SIGMA', 5))
BURST_MU = int(environ.get('BURST_MU', 2))
BURST_SIGMA = int(environ.get('BURST_SIGMA', 1))
TIMEOUT = int(environ.get('TIMEOUT', 15))

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('mailclient')

email_template = """
FROM: {sender:s}
TO: {to:s}
SUBJECT: {subject:s}

{body:s}

-hrod
{flag:s}
"""

class Email:
    def __init__(self, sender, recipients, subject, body):
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.body = body

    def __repr__(self):
        context = {k: self.__dict__[k] for k in ('sender', 'recipients', 'subject')}
        context['body'] = textwrap.shorten(self.body, width=25)
        return "< from:{sender!r}, to:{recipients!r}, subject:{subject!r}, body:{body!r} >".format(**context)

class EmailDB:
    RANDOM_EMAIL_QUERY = 'SELECT Id, Sender, Subject, Body FROM Emails ORDER BY RANDOM() LIMIT 1'
    RECIPIENTS_QUERY = 'SELECT Address FROM Recipients WHERE EmailId == ?'

    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def random(self):
        eid, sender, subject, body = self.cursor.execute(self.RANDOM_EMAIL_QUERY).fetchone()
        recipients = [row[0] for row in self.cursor.execute(self.RECIPIENTS_QUERY, (eid,))]
        return Email(sender, recipients, subject, body)

if __name__ == "__main__":
    if CTF_FLAG is None or SMTP_ADDR is None or EMAILDB_PATH is None:
        raise ValueError("CTF_FLAG, SMTP_ADDR, and EMAILDB_PATH must be set")

    logger.info("Opening connection to email database at %s", EMAILDB_PATH)
    db = EmailDB(sqlite3.connect(EMAILDB_PATH))

    tls_context = ssl.create_default_context(cafile=TLS_CA)
    tls_context.check_hostname = False

    while True:
        wait = abs(random.gauss(INTERMISSION_MU, INTERMISSION_SIGMA))
        logging.info("Sleeping for %.2f seconds", wait)
        sleep(wait)

        # Try to send an email
        try:
            logging.info("Let's go! Connecting to %s:%d", SMTP_ADDR, SMTP_PORT)
            with smtplib.SMTP(SMTP_ADDR, SMTP_PORT, timeout=TIMEOUT) as smtp:
                # Try to start TLS
                logger.info("Starting TLS")
                try:
                    smtp.starttls(context=tls_context)
                except smtplib.SMTPResponseException as e:
                    logger.warning("Recieved %d on STARTTLS. Proceding without TLS!", e.smtp_code)

                for _ in range(math.floor(abs(random.gauss(BURST_MU, BURST_SIGMA)))):
                    # Pick an email from the DB
                    email = db.random()
                    logger.info("Sending email: %r", email)

                    # Format and send it!
                    smtp.sendmail(
                        email.sender,
                        email.recipients,
                        email_template.format(
                            sender=email.sender,
                            to=", ".join(email.recipients),
                            subject=email.subject,
                            body=email.body,
                            flag=CTF_FLAG
                        )
                    )
        except Exception as e:
            logger.error(e)
