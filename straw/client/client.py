from datetime import datetime
from telnetlib import Telnet
from time import sleep, time
from binascii import hexlify, unhexlify
from hashlib import sha256
from os import path, environ, getenv
import logging
import hmac
import string
import random
import sys
import re

# Init logging
if environ.get('LOG_LEVEL', None) is not None:
    loglevel = getattr(logging, environ.get('LOG_LEVEL').upper(), None)
    if not isinstance(loglevel, int):
            raise ValueError('Invalid log level: {}'.format(environ.get('LOG_LEVEL')))
else:
    loglevel = logging.INFO

logging.basicConfig(level=loglevel)

class FileListing:
    """
    A structure to represent a single entry in the `ls -l` output
    """
    pattern_str = r'(\S)(\S{9})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+,)?\s*(\d+)\s+(\S+\s+\d+\s+\S+)\s+(.+)'
    re_pattern = re.compile(pattern_str)
    datetime_pattern = '%b %d %H:%M'

    def __init__(self, line):
        m = self.re_pattern.match(line)
        self.source = line.strip()

        if m is None:
            raise ValueError("line does not match pattern: '{0}'".format(line))

        self.is_directory = m.group(1) == 'd'
        self.permissions = m.group(2)
        self.links = int(m.group(3))
        self.owner = m.group(4)
        self.group = m.group(5)
        self.size = int(m.group(7))

        try:
            self.timestamp = datetime.strptime(m.group(8), self.datetime_pattern)
        except ValueError:
            self.timestamp = None

        self.name = m.group(9).strip()

    def __str__(self):
        return self.source

    def __repr__(self):
        return self.source

class TelnetTimeoutError(Exception):
    def __init__(self, msg="telnet connection took too long to respond"):
        self.msg = msg

    def __str__(self):
        return "TelnetTimoutException: {msg}".format(msg=self.msg)

class TelnetClient:
    """
    An interface for issuing and interpretting commands over telnet
    """
    port = 23
    retry_period = 5
    retry_count = 5

    def __init__(self, host, user=None, passwd=None, timeout=10, naumotp_secret=None):
        self.connected = False
        self.loggedin = False
        self.host = host
        self.user = user
        self.passwd = passwd
        self.timeout = timeout
        self.cwd = None
        self.naumotp_secret = naumotp_secret

        if isinstance(self.naumotp_secret, str):
            self.naumotp_secret = self.naumotp_secret.encode('utf-8')

        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write("exit\n")
        self.conn.close()

    def connect(self):
        for i in range(self.retry_count + 1):
            start_time = time()
            try:
                self.conn = Telnet(self.host, self.port, self.timeout)
            except Exception as e: # Catch all errors: not very precise, but it shouldn't be an issue
                logging.info("Connect to shell server failed due to '{0}'".format(e))
                elapsed = time() - start_time
                remaining = self.retry_period - elapsed
                logging.debug("Retrying in {0:.2f}s".format(remaining))
                if remaining > 0: sleep(remaining)
                if i == self.retry_count: raise
            else:
                self.connected = True


    def login(self):
        self.read_until("login: ")
        self.write("{0}\n".format(self.user))

        self.read_until("Password: ")
        self.write("{0}\n".format(self.passwd))

        index, match, _ = self.expect([r'\$ ', r'challenge \[(?P<chal>[0-9a-f]+)\]'])
        if index == 0:
            self.loggedin = True
            self.cwd = '~'

        elif index == 1:
            if self.naumotp_secret is None:
                raise ValueError("Encountered naumotp challenge without a secret to compute the HMAC")

            resp = hexlify(hmac.new(self.naumotp_secret, unhexlify(match["chal"]), digestmod=sha256).digest())

            self.read_until("response: ")
            self.write("{0}\n".format(resp.decode('utf-8')))

            index, _, _ = self.expect([r'\$ '])
            if index == 0:
                self.loggedin = True
                self.cwd = '~'

    def expect(self, patterns):
        for i, pattern in enumerate(patterns):
            if isinstance(pattern, str):
                patterns[i] = pattern.encode('utf-8')

        index, match, text = self.conn.expect(patterns, self.timeout)

        try:
            logging.debug(text.decode('utf-8'))
        except UnicodeDecodeError:
            pass

        if index == -1:
            raise TelnetTimeoutError()
        else:
            return index, match, text.decode('utf-8')

    def read_until(self, expected):
        if isinstance(expected, str):
            expected = expected.encode('utf-8')

        text = self.conn.read_until(expected, self.timeout)

        try:
            result = text.decode('utf-8')
            logging.debug(result)
        except UnicodeDecodeError:
            result = None

        if not text.endswith(expected):
            raise TelnetTimeoutError()
        else:
            return result

    def write(self, text):
        if isinstance(text, str):
            text = text.encode('utf-8')

        try:
            logging.debug(text.decode('utf-8'))
        except UnicodeDecodeError:
            pass

        self.conn.write(text)

    def ls(self, *files):
        self.write("ls -la {0}\n".format(' '.join(files)))
        response = self.read_until("{}$ ".format(self.cwd or ""))

        output = response.split('\n')[1:-1]
        files = []

        for line in output:
            if line.startswith('total'):
                continue
            files.append(FileListing(line))

        return files
        # No error chevking, because this is a dumb client

    def cd(self, directory):
        self.write("cd {0}\n".format(directory))
        response = self.read_until("$ ")

        _, sep, cwd = response.rpartition(':')
        if sep is not None:
            self.cwd = cwd.strip('$ ')
        else:
            self.cwd = None

    def cat(self, file):
        self.write("cat {0}\n".format(file))
        response = self.read_until("{}$ ".format(self.cwd or ""))

HOST = environ.get('SHELL_HOST', 'shell')
USER = environ.get('SHELL_USER', 'noob')
PASSWD = environ.get('SHELL_PASS', 'noob')
NAUMOTP_SECRET = environ.get('NAUMOTP_SECRET', None)

DELAY_MEAN = 3
DELAY_VAR = 0.6
ACTION_COUNT = 10

def file_filter(files, cwd):
    for file in files:
        if file.name.startswith('.') and not file.name == '..':
            continue

        if file.is_directory:
            if file.name == '.':
                continue
            if (cwd == "~" or path.dirname(cwd) == '/') and file.name == '..':
                continue

        yield file

def delay():
    length = abs(random.gauss(DELAY_MEAN, DELAY_VAR))
    sleep(length)

if __name__ == "__main__":
    logging.info("Telnet shell host is '{0}'".format(HOST))

    while True:
        try:
            # Waiting a bit
            start_delay = 10
            if start_delay > 0:
                logging.info("Waiting {} seconds to start".format(start_delay))
                sleep(start_delay)

            with TelnetClient(HOST, USER, PASSWD, naumotp_secret=NAUMOTP_SECRET) as shell:
                delay()

                shell.login()

                delay()

                for _ in range(ACTION_COUNT):
                    files = shell.ls()

                    delay()

                    next = random.choice(list(file_filter(files, shell.cwd)))
                    if next.is_directory:
                        shell.cd(next.name)
                        logging.info("cd to " + str(next))
                    else:
                        shell.cat(next.name)
                        logging.info("cat " + str(next))

                    delay()
        # Catch and continue on any exception to avoid the need to recreate the container.
        # Main reason for this is to avoid changing the MAC address.
        except Exception as err:
            logging.exception("Exception in the main loop")
