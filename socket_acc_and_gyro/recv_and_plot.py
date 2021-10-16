import socket 
import json
import numpy as np
import matplotlib.pyplot as plt


HOST = "192.168.239.64"
PORT = 8081
print("Starting server at: ", (HOST, PORT))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            print("Received from socket server:", data)
            if (data.count('{') != 1):
                data = data.split('}')[0] + '}'
            obj = json.loads(data)
            
            observe_data = 'x' # Modify yourself: x, y, z, gx, gy, gz

            x = obj['s']
            y = obj[observe_data]
            plt.scatter(x, y, c='blue')
            plt.title(observe_data + " variations over time")
            plt.xlabel("sample num")
            plt.ylabel(observe_data)
            plt.pause(0.0001)
