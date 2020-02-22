import asyncio, telnetlib3
import socket
import sys

TCP_IP = '0.0.0.0'
TCP_PORT = 4001
bob_ip = '165.91.9.93'
bob_port = 6023

#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind((TCP_IP, TCP_PORT))
#server.listen(1)

#print("Listening on {}:{}".format(TCP_IP, TCP_PORT))
#sys.stdout.flush()

@asyncio.coroutine
def shell2(reader, writer):
    pass


@asyncio.coroutine
def shell(reader, writer):

    while True:
        inp = yield from reader.read(1024)
        print("Recvd: ", inp)
        y = input("Pass through? ")
        if y.lower() == 'y':
            writer2.write(inp)
            inp = yield from reader2.read(1024)
            print("Recvd2: ", inp)
        writer.write(inp)
        
        

loop = asyncio.get_event_loop()
coro2 = telnetlib3.open_connection(bob_ip, bob_port, shell=shell2)
reader2, writer2 = loop.run_until_complete(coro2)
loop.run_until_complete(writer2.protocol.waiter_closed)        


#loop = asyncio.get_event_loop()
coro = telnetlib3.create_server(port=4000, shell=shell)
server = loop.run_until_complete(coro)
loop.run_until_complete(server.wait_closed())


