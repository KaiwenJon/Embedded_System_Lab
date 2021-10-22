"""
A simple Python script to send messages to a sever over Bluetooth using
Python sockets (with Python 3.3 or above).
"""

import socket
import time

serverMACAddress = '2C:67:73:DF:EF:D3' # 2C:67:73:DF:EF:D3 kooper
psm = 0x0017
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
sock.connect((serverMACAddress,psm))
print("Connected!")
if psm == 0x0019:
    # AVDTP
    pre_send_data = [
        '0001',
        '100204',
        '200208',
        '3003040401000706000021150226',
        '400604'
    ]
elif psm == 0x0001:
    # SDP
    pre_send_data = [
        '060000000f3503190100ffff35050a0000ffff00',
        '060001000f3503191200ffff35050a0000ffff00'
    ]
elif psm == 0x0017:
    # volume up AVCTP
    pre_send_data = [
        '92110e0f4800001958310000020d99',
        'a2110e0f4800001958310000020d99'
    ]
music = '8001049f000ccc0000000001079cbd26ef40710000005100000098dd1f42f22e8c376519fcccadea690d32fc5785e28e2895cb15f4f684f5269046ccc96a6fc5392465e364d82813aaa44ed355d016dd4144ba5d11a6a6e188d5a2e557b048f56b61822b67509cbd265fc05100000061000000a73ed36eda6455cced36a77f124ccb6ecbdf441014f026b0f827cb25b6184d7b889be73651ae822379b97d92a8e3b4d42b6d48a8548e64d1d550c7911ad0ce56c59d073aad4d48f2c12cc7499cbd2661006100000061000000a4893983a2651fef71d7d05dc7f4dd868f3abda11ab8f56a71ca6e9aa8a2b9c8af208156d5cb7415fb2099a871710d95f729dc31563b45b9986506af81a525db2f9203f8868a3b4d8de85f829cbd2608c062000000610000000fd96b0040d89fb18634b748dab7db46e7339d8cc6ebd6aa97e42c756b426499daadd6161859a4b886348dfc6198bd781f6982a9a74dba5e9a99cb888d65a30ee2b1e408af6df58c65758cf49cbd269180610000006100000028b58dc7a1059a302345049ec470185e0ae7da7e1489484ae02e25edaeaa76809839235b0994dd43f19966f1a947fa399d8922fbdeb9dcc58b5e9893358dbd175d4977c4639bd3e2be95a4449cbd2619406100000061000000b3e60e2b0e4b9f4272f64f8b137455b9fbf2b440194e01593f2717b2479a8024102715c9574e9b49ce08f61a51445bb537e74f2b18b93dd3e765d574c83542a764fd63f857a6f0482e7e1c309cbd262bc06000000060000000834653a356c45556ba5bf6a56f1162b85670256a095ad9150c0566b1527495984947784699851c255a6954fb856f4c57a185c59571a456ab15eef159f657c1a565b05e765596b97405563105'
def presend():
    print("pre-send", psm)
    for data in pre_send_data:
        time.sleep(0.2)
        hexdata = data.decode('hex')
        sock.send(hexdata)

while 1:
    data = raw_input()

    if data == 'pre':
        presend()
    if data == "sbc":
        data = music
    if not data or len(data)%2 == 1:
        print("Please even-length hex stream.")
        continue

    hexdata = data.decode('hex')
    sock.send(hexdata)
print("Disconnected.")
sock.close()