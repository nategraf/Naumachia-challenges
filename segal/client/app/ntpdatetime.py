from datetime import datetime
from time import time
from warnings import warn
import ntplib

class NTPWarning(UserWarning):
    pass

class NtpDatetime:
    """A datetime class which synchronizes with NTP without changing system time"""

    def __init__(self, server, update_interval=16):
        self.ntp = ntplib.NTPClient()
        self.server = server
        self.offset = 0
        self.last_update = 0
        self.interval = update_interval

        self.update()

    def update(self):
        try:
            self.offset = self.ntp.request(self.server).offset
            self.last_update = time()
        except ntplib.NTPException as e:
            # Downgrade errors to warnings
            warn(str(e))

    def utcnow(self):
        t = time()

        # Assume system time is steady and monotomic
        if t - self.last_update > self.interval:
            self.update()

        t += self.offset 
        return datetime.utcfromtimestamp(t)
