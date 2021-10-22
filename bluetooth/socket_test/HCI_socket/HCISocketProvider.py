
import socket
import struct
import time
import threading
from constants import *
from pprint import pformat

# If we only open HCI socket, the connection cannot hold for more than 2 seconds. Therefore, we concurrently open a l2cap socket to ensure the conncetion, then bind the HCI socket to send customized l2cap packets.
# When sending customized l2cap packets on HCI socket, we need to specify the ACL connection handle, which is determined at the stage of hci's 'create connection'. So we first listen to the HCI event to get the connection handle before starting sending l2cap data.
# In addition, the connection still seem to disconnect easily once we send malformed packet, so we reset l2cap connection every 5 seconds to ensure the data being sent.

class HCISocketProvider(object):
    def __init__(self, serverMACAddress='C8:09:A8:C8:FE:05', serverPort=0x000f):
        self.DEBUG = False
        self.hci_device_id = 0 # use hciconfig to check device id
        self.l2cap_connect_interval = 5 # seconds
        self.l2cap_sock = None
        self.hci_sock = None
        self.connection_handle = None
        self.serverMACAddress = serverMACAddress
        self.serverPort = serverPort
        self.wait_for_handle = True
    def run_l2cap_connection(self):
        def connect_to_L2CAP_thread():
            while 1:
            # To avoid socket automatically disconnect
                time.sleep(self.l2cap_connect_interval)
                self.wait_for_handle = True
                self.l2cap_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
                self.l2cap_sock.connect((self.serverMACAddress,self.serverPort))  
                print("\n==============L2CAP Socket Connected!==================")

        l2cap_thread = threading.Thread(target=connect_to_L2CAP_thread, name='L2CAPSocketConnection')
        l2cap_thread.setDaemon(True)
        l2cap_thread.start()

    def hci_binding(self):
        filter = struct.pack(HCIPY_HCI_FILTER_STRUCT,
                             (1 << HCI_EVENT_PKT) | (1 << HCI_ACLDATA_PKT),     # Type Mask
                             (1 << EVT_DISCONN_COMPLETE)
                             | (1 << EVT_CMD_COMPLETE) | (1 << EVT_CONN_COMPLETE)
                             | (1 << EVT_CMD_STATUS),                           # eventMask1
                             1 << (EVT_LE_META_EVENT - 32),                     # eventMask2
                             0                                                  # opcode
                             )
        self.hci_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        self.hci_sock.bind((self.hci_device_id,))
        self.hci_sock.setsockopt(socket.SOL_HCI, socket.HCI_FILTER, filter)
        print("Bind HCI Success!")

    def wait_for_connection_handle(self):
        if self.DEBUG: print("------Listening to Response at HCI--------------")
        data = bytearray(self.hci_sock.recv(1024))
        packet_indicator = data[0]
        if self.DEBUG: print("packet_indicator = {}".format(packet_indicator))

        # 1 = Command Packets
        # 2 = Data Packets for ACL
        # 3 = Data Packets for SCO
        # 4 = Event Packets

        if HCI_EVENT_PKT == packet_indicator:
            evt = data[1]
            if self.DEBUG: print("HCI_EVENT_PKT, evt={}".format(hex(evt)))

            if EVT_CMD_STATUS == evt:
                if self.DEBUG: print("EVT_CMD_STATUS")
                s = struct.Struct('=B BB BBH')
                fields = s.unpack(data)
                evt_cmd_status = dict( packet_indicator  = fields[0],
                                        hdr_evt     = fields[1],
                                        hdr_plen    = fields[2],
                                        cmd_status  = fields[3],
                                        cmd_ncmd    = fields[4],
                                        cmd_opcode  = fields[5],
                                        )
                if self.DEBUG: print("EVT_CMD_STATUS = {}".format(pformat(evt_cmd_status)))

            elif EVT_DISCONN_COMPLETE == evt:
                if self.DEBUG: print("EVT_DISCONN_COMPLETE")

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
                if self.DEBUG: print("ACL CONN COMPLETE")
                s = struct.Struct('=BBBBH 3H BB')
                fields = s.unpack(data)
                evt_conn_complete = dict(
                    handle = fields[4]
                )
                if self.DEBUG: print("conn_complete = {}".format(pformat(evt_conn_complete)))
                self.connection_handle = fields[4]
                print('connection_handle: {}'.format(self.connection_handle))
                print("Got Initial Connection Handle!")
                self.wait_for_handle = False

        elif HCI_ACLDATA_PKT == packet_indicator:
            if self.DEBUG: print("HCI_ACLDATA_PKT")
            self.connection_handle = data[1] & 0x0fff
            payload = data[9:-1]
            # DCID = data[13]
            # s = struct.Struct('=B 4H BB HHH HH')
            # if len(data) == 21:
            #     fields = s.unpack(data)
            #     for d in fields:
            #         print(d)
            # if self.DEBUG: print('ACL data');
            print('connection_handle: {}'.format(self.connection_handle))
            # print('DCID: {}'.format(hex(DCID)))
            if self.DEBUG: print("Got Connection Handle!")
            self.wait_for_handle = False

    def wait_handle_and_send_data(self, data):
        if self.wait_for_handle:
            self.wait_for_connection_handle() # blocking
        else:
            l2cap_payload = data
            l2cap_header = chr(len(l2cap_payload)) + "\x00" + "\x01\x00" # Signal channel
            HCI_header = "\x02"+chr(self.connection_handle)+"\x00"+chr(len(l2cap_header+l2cap_payload))+"\x00"
            send_data = HCI_header + l2cap_header + l2cap_payload
            print("Sending data on HCI:", send_data)
            self.hci_sock.send(send_data)


if __name__ == '__main__':
    serverMACAddress = 'C8:09:A8:C8:FE:05'
    serverPort = 0x000f
    hci = HCISocketProvider(serverMACAddress, serverPort)
    hci.run_l2cap_connection()
    hci.hci_binding()
    while 1:
        time.sleep(0.5)
        data = "\x01\x02\xa3"
        hci.wait_handle_and_send_data(data)