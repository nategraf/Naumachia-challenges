from datetime import datetime
from telnetlib import Telnet
from time import sleep
import string
import random
import os
import sys
import re

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

        self.name = m.group(9)

    def __str__(self):
        return self.source

    def __repr__(self):
        return self.source

class TelnetClient:
    """
    An interface for issuing and interpretting commands over telnet
    """
    timeout = 15
    port = 23

    def __init__(self, host, user=None, passwd=None):
        self.connected = False
        self.loggedin = False
        self.user = user
        self.passwd = passwd

        self.conn = Telnet(host, self.port, self.timeout)
        self.connected = True

        self.conn.read_until("login: ")
        self.conn.write("{0}\n".format(self.user))

        while not self.loggedin:
            self.conn.read_until("Password: ")
            self.conn.write("{0}\n".format(self.passwd))

            index, _, _ = self.conn.expect([r'\$ ', r'Password'])
            if index == 0:
                self.loggedin = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.write("exit\n")
        self.conn.close()

    def ls(self, *files):
        self.conn.write("ls -la {0}\n".format(' '.join(files)))
        response = self.conn.read_until("$ ")

        output = response.split('\n')[1:-1]
        files = []
        for line in output:
            if line.startswith('total'):
                continue
            files.append(FileListing(line))

        return files
        # No error chevking, because this is a dumb client

    def cd(self, directory):
        self.conn.write("cd {0}\n".format(directory))
        response = self.conn.read_until("$ ")
        # No error chevking, because this is a dumb client

HOST = 'shell'
USER = 'noob'
PASSWD = 'noob'

print("Telnet shell host is {0}".format(HOST))
sys.stdout.flush()

with TelnetClient(HOST, USER, PASSWD) as shell:
    shell.cd("/proc")
    for _ in range(10):
        files = shell.ls()
        print("ls: " + str(files))

        next = random.choice(filter(lambda f: f.is_directory, files))
        shell.cd(next.name)
        print("cd to " + str(next))
