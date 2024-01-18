import serial
import socket
import sys
buffersize=1024

if __name__ == '__main__':
    ## Read Arduino Data
    ser = serial.Serial('/dev/ttyACM0' ,9600, timeout=10)
    ser.flush
    
    ## IP Address to where you want to send the Data
    DestainationIP = '192.168.1.122'
    SocketPort = 10000 
    SocketPort = 10001
    
    ## Socket to Client where data is sent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ((DestainationIP, SocketPort))
    
    print('Server Up')
    
    
    ## Future Requests from Client
    """message1.address=sock.recvfrom(buffersize)
    message1=message.decode('utf-8')
    print(message1)
    print('Client',address[0])"""
    
    ## Messages to send to Client GPM, GPM Total
    while True:
        ## Read GPM from Arduino
        flowGPM = None
        flowGPM = ser.readline().decode('utf-8').rstrip()
        ## Send GPM to Server
        sock.sendto(flowGPM.encode('utf-8'),server_address)
        print(flowGPM)
        pass
    
