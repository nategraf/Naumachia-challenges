import socket
from time import sleep
import os
import sys
import math

UDP_IP = 'bob'
UDP_PORT = 5005

flag = os.environ['CTF_FLAG']

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("flag:", flag)
sys.stdout.flush()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    first_half = flag[:math.floor(len(flag)/2)]
    last_half = flag[math.floor(len(flag)/2):]

    try:
        message = ("Hey Bob, I think I have half the flag here. "
                   f"Is this right? flag{{{first_half}")
        print(f"Sending message to {(UDP_IP, UDP_PORT)!r}: {message!r}")

        sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)
        pass
    sleep(3)
