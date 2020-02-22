from socket import socket, timeout, AF_INET, SOCK_DGRAM, SO_BROADCAST, SOL_SOCKET
from time import sleep, time
from random import random
import os
import sys
import logging

# Init logging
if os.environ.get('LOG_LEVEL', None) is not None:
    loglevel = getattr(logging, os.environ.get('LOG_LEVEL').upper(), None)
    if not isinstance(loglevel, int):
            raise ValueError('Invalid log level: {}'.format(os.environ.get('LOG_LEVEL')))
else:
    loglevel = logging.INFO

logging.basicConfig(level=loglevel)

UDP_PORT = int(os.getenv('UDP_PORT', 5005))
BROADCAST_ADDR = os.getenv('BROADCAST_ADDR', '<broadcast>')
STEP = float(os.getenv('STEP', 2))
RESTART_DELAY = float(os.getenv('RESTART_DELAY', 15))
CHARACTER = os.getenv('CHARACTER')

logging.info("UDP port: %s", UDP_PORT)

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', UDP_PORT))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def broadcast(msg):
    s.sendto(msg.encode('utf-8'), (BROADCAST_ADDR, UDP_PORT))
    logging.info(msg)

while True:
    sleep(RESTART_DELAY - (time() % RESTART_DELAY))
    with open('script.txt', 'r') as script:
        monologe = False
        start = time()
        current = start
        for direction in script:
            if direction.strip():
                if ':' in direction:
                    character, line = (chunk.strip() for chunk in direction.split(':', 1))
                    if character.lower() == CHARACTER.lower():
                        monologe = True
                        broadcast(line)

                    else:
                        monologe = False
                elif monologe:
                    line = direction.strip()
                    broadcast(line)


            current += STEP
            if current > time():
                sleep(current - time())

    sleep(time() % RESTART_DELAY)
