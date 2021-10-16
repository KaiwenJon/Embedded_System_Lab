import socket 
import numpy as np
import matplotlib.pyplot as plt

HOST = "192.168.239.64"
PORT = 8081
print("start server")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            print("Received from socket server:", data)