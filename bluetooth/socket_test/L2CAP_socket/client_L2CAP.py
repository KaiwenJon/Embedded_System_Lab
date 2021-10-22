"""
A simple Python script to send messages to a sever over Bluetooth using
Python sockets (with Python 3.3 or above).
"""

import socket
import time

serverMACAddress = 'C8:09:A8:C8:FE:05'
port = 0x000f
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
sock.connect((serverMACAddress,port))
print("Connected!")
while 1:
    data = raw_input()
    if not data:
        break
    sock.send(str(data))
    data = sock.recv(1024)
    print("Data received: ", str(data))
print("Disconnected.")
sock.close()

