"""
A simple Python script to receive messages from a client over
Bluetooth using Python sockets (with Python 3.3 or above).
"""

import socket

# hostMACAddress = 'F0:2F:74:6A:F4:4B' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
# 24:79:F3:8E:62:F2 my oppo
# F0:2F:74:6A:F4:4B onwardbt
port = 0x1001 # 3 is an arbitrary choice. However, it must match the port used by the client.
backlog = 1
size = 1024
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((socket.BDADDR_ANY,port))
s.listen(backlog)
try:
    client, address = s.accept()
    while 1:
        data = client.recv(size)
        if data:
            print(data)
            client.send(data)
except:	
    print("Closing socket")	
    client.close()
    s.close()