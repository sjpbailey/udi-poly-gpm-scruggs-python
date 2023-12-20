import serial
import socket
import sys


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0' ,9600, timeout=10)
    ser.flush
    
    DestainationIP = '192.168.1.164'
    SocketPort = 10000
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (DestainationIP, SocketPort)
    
    while True:
        line = ser.readline().decode('utf8').rstrip()
        print(line)
        #print(type(line))
        #for i in line:
            #print(i)
         #   outputgpm=i
          #  print(outputgpm)
        
        
        sock.sendto(line.encode('utf-8'),server_address)
        