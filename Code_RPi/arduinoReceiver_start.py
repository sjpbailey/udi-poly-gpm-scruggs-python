import socket
import sys
import json
from struct import unpack

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
host, port = '192.168.1.18', 10000
server_address = (host, port)

print(f'Starting UDP server on {host} port {port}')
sock.bind(server_address)

while True:
    message, address = sock.recvfrom(4096)
    message = message.decode('utf-8')
    dataArray=message.split(' , ')
    print('GPM:', dataArray[0], 'GPM Total:', dataArray[1])

"""while True:
    # Wait for message
    message, address = sock.recvfrom(4096)
    message = message.decode('utf-8')
    print(message)
    
    
    
    if message == 0:
        print("Done")    
        break"""
    
    #line1 = message
    #print(line
    #line2 = message
    
    #print(line2)"""
    
    
    #print(f'Received {len(message)} bytes:')
    #x, y, z = unpack('3f', message)
    #print(f'X: {x}, Y: {y}, Z: {z}')


"""
#message, address = sock.recvfrom(4096)
#message = message.decode('utf-8')

flowGPM = None
line1 = message
print(line1)

line2 = message
print(line2)"""

