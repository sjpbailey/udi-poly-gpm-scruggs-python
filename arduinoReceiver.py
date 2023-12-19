import socket
import sys
from struct import unpack

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
host, port = '192.168.1.18', 10000
server_address = (host, port)

print(f'Starting UDP server on {host} port {port}')
sock.bind(server_address)

while True:
    # Wait for message
    message, address = sock.recvfrom(4096)
    message = message.decode('utf-8')
    print(message)

    
    
    
    
    #print(f'Received {len(message)} bytes:')
    #x, y, z = unpack('3f', message)
    #print(f'X: {x}, Y: {y}, Z: {z}')