"""
A simple Python script to send messages to a sever over Bluetooth using
Python sockets (with Python 3.3 or above).
"""

import socket
import struct
import time
import threading
from constants import *
from pprint import pformat

l2cap_sock = None
connection_handle = None
wait_for_handle = True
def connect_L2CAP():
    global connection_handle
    global l2cap_sock
    global wait_for_handle
    serverMACAddress = 'C8:09:A8:C8:FE:05'
    port = 0x000f
    while 1:
        # To avoid socket automatically disconnect
        time.sleep(5)
        try:
            wait_for_handle = True
            l2cap_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
            l2cap_sock.connect((serverMACAddress,port))  
            print("==============L2CAP Socket Connected!==================")
        except Exception as e:
            print(e)

            

l2cap_thread = threading.Thread(target=connect_L2CAP, name='L2CAPSocketConnection')
l2cap_thread.setDaemon(True)
l2cap_thread.start()

filter = struct.pack(HCIPY_HCI_FILTER_STRUCT,
                             (1 << HCI_EVENT_PKT) | (1 << HCI_ACLDATA_PKT),     # Type Mask
                             (1 << EVT_DISCONN_COMPLETE)
                             | (1 << EVT_CMD_COMPLETE) | (1 << EVT_CONN_COMPLETE)
                             | (1 << EVT_CMD_STATUS),                           # eventMask1
                             1 << (EVT_LE_META_EVENT - 32),                     # eventMask2
                             0                                                  # opcode
                             )

device_id = 0
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
sock.bind((device_id,))
sock.setsockopt(socket.SOL_HCI, socket.HCI_FILTER, filter)
print("Bind HCI Success!")


def wait_connection(sock):
    global wait_for_handle
    print("------Listening to Response at HCI--------------")
    data = bytearray(sock.recv(1024))
    packet_indicator = data[0]
    print("packet_indicator = {}".format(packet_indicator))

    # 1 = Command Packets
    # 2 = Data Packets for ACL
    # 3 = Data Packets for SCO
    # 4 = Event Packets

    if HCI_EVENT_PKT == packet_indicator:
        evt = data[1]
        print("HCI_EVENT_PKT, evt={}".format(hex(evt)))

        if EVT_CMD_STATUS == evt:
            print("EVT_CMD_STATUS")
            s = struct.Struct('=B BB BBH')
            fields = s.unpack(data)
            evt_cmd_status = dict( packet_indicator  = fields[0],
                                    hdr_evt     = fields[1],
                                    hdr_plen    = fields[2],
                                    cmd_status  = fields[3],
                                    cmd_ncmd    = fields[4],
                                    cmd_opcode  = fields[5],
                                    )
            print("EVT_CMD_STATUS = {}".format(pformat(evt_cmd_status)))

        elif EVT_DISCONN_COMPLETE == evt:
            print("EVT_DISCONN_COMPLETE")

            s = struct.Struct('=B BB   BHB')
            fields = s.unpack(data)
            evt_disconn_complete = dict(
                #packet_indicator=fields[0],
                #hdr_evt=fields[1],
                #hdr_plen=fields[2],
                status=fields[3],
                handle=fields[4],
                reason=fields[5],
            )

            print("evt_disconn_complete = {}".format(pformat(evt_disconn_complete)))
            exit(0)
        elif evt == EVT_CONN_COMPLETE:
            print("ACL CONN COMPLETE")
            s = struct.Struct('=BBBBH 3H BB')
            fields = s.unpack(data)
            evt_conn_complete = dict(
                handle = fields[4]
            )
            print("conn_complete = {}".format(pformat(evt_conn_complete)))
            connection_handle = fields[4]
            print("Got Connection Handle!")
            wait_for_handle = False
            return connection_handle

    elif HCI_ACLDATA_PKT == packet_indicator:
        print("HCI_ACLDATA_PKT")
        connection_handle = data[1] & 0x0fff
        payload = data[9:-1]

        print('ACL data');
        print('connection_handle: {}'.format(connection_handle))
        print("Got Connection Handle!")
        wait_for_handle = False
        return connection_handle

try:
    while 1:
        if wait_for_handle:
            connection_handle = wait_connection(sock)
        else:
            # Connection Handle Found!
            # l2cap_payload = raw_input("Please enter HCI payload (in hex stream): ")
            time.sleep(0.5)
            l2cap_payload = "a1234"
            if len(l2cap_payload)%2 == 1:
                l2cap_payload += "0"
            l2cap_payload = l2cap_payload.decode('hex')
            l2cap_header = chr(len(l2cap_payload)) + "\x00" + "\x01\x00" # Signal channel
            HCI_header = "\x02"+chr(connection_handle)+"\x00"+chr(len(l2cap_header+l2cap_payload))+"\x00"
            data = HCI_header + l2cap_header + l2cap_payload
            sock.send(data)

except Exception as e:
    print("\nDisconnected.")
    print(e)
    print(connection_handle)
    l2cap_sock.close()
    sock.close()