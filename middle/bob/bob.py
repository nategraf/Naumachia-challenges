import socket
import os
import sys
import math

UDP_IP = 'bob'
UDP_PORT = 5005

flag = os.environ['CTF_FLAG']

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening on {}:{}".format(UDP_IP, UDP_PORT))
print("flag:", flag)
sys.stdout.flush()

while True:
        first_half = flag[:math.floor(len(flag)/2)]
        last_half = flag[math.floor(len(flag)/2):]

        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print(f"Received message from {addr!r}: {data!r}")

        if first_half in str(data):
            response = f"Yup, that's it! Here is the second half: {last_half}}}"
        else:
            response = f"That doesn't seem right..."

        print(f"Sending response to {addr!r}: {response!r}")
        sock.sendto(response.encode('utf-8'), addr)
        sys.stdout.flush()

