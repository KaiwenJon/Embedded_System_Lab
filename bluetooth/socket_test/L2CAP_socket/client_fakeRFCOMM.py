"""
A simple Python script to send messages to a sever over Bluetooth using
Python sockets (with Python 3.3 or above).
"""

import socket
import time

serverMACAddress = '00:11:22:33:44:55'
psm = 0x0019
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
sock.connect((serverMACAddress,psm))
print("Connected!")
time.sleep(0.1)
sock.send("\x03\x3f\x01\x1c") # SABM channel=0
time.sleep(0.1)
sock.send("\x03\xef\x15\x83\x11\x02\xf0\x07\x00\xf0\x03\x00\x07\x70") # UIH (PN)
time.sleep(0.1)
sock.send("\x0b\x3f\x01\x59") # SABM channel=1
time.sleep(0.1) 
sock.send("\x03\xef\x09\xe3\x05\x0b\x8d\x70") # UIH (MSC)
while 1:
    data = raw_input()
    if not data:
        break
    if data == "f":
        data = "\x03\xef\x2b\x54\x60\x36\x9a"
    sock.send(str(data))
    data = sock.recv(1024)
    print("Data received: ", str(data))
print("Disconnected.")
sock.close()