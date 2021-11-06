from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import Peripheral, UUID, Descriptor


class MyDelegate (DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif (isNewData):
            print("Received new data from", dev.addr)
    def handleNotification(self, cHandle, data):
        print("Received notification: %s" %data)


# scanner = Scanner().withDelegate(MyDelegate())
# devices = scanner.scan(10.0)
# n = 0
# for dev in devices:
#     print("%d: Device %s (%s), RSSI=%d dB" %
#           (n, dev.addr, dev.addrType, dev.rssi))
#     n += 1
#     for (adtype, desc, value) in dev.getScanData():
#         print(" %s = %s" % (desc, value))
# number = int(input('Enter your device number: '))
# print('Device', number)
# print(list(devices)[number].addr)
print("Connecting...")
dev = Peripheral("e2:da:5e:a1:3b:af",'random')
print("Services...")
for svc in dev.services:
    print(str(svc))
try:
    buttonService = dev.getServiceByUUID(UUID(0xA000))
    for btn_ch in buttonService.getCharacteristics():
        print(str(btn_ch))
    btn_ch = dev.getCharacteristics(uuid = UUID(0xA001))[0]
    btn_des = btn_ch.getDescriptors(forUUID=0x2902)[0]
    idService = dev.getServiceByUUID(UUID(0x9000))
    for id_ch in idService.getCharacteristics():
        print(str(id_ch))
    id_ch = dev.getCharacteristics(uuid = UUID(0x9001))[0]
    id_des = id_ch.getDescriptors(forUUID=0x2902)[0]
    ledService = dev.getServiceByUUID(UUID(0x7000))
    for led_ch in ledService.getCharacteristics():
        print(str(led_ch))
    led_ch = dev.getCharacteristics(uuid = UUID(0x7001))[0]
    print("Button CHAR Value:",btn_ch.read())
    print("Button CCCD:",btn_des.read())
    print("Student ID CCCD:",id_des.read())
    print("LED1 CHAR Value:",led_ch.read())
    setup_data=b'\x01\x00'
    led_data=b'\x01'
    btn_des.write(setup_data, True)
    id_des.write(setup_data, True)
    led_ch.write(led_data, True)
    print("Notifiying Enabled")
    print("LED1 On")
    print("Button CCCD:",btn_des.read())
    print("Student ID CCCD:",id_des.read())
    print("LED1 CHAR Value:",led_ch.read())
    while(1):
        print("Button:", btn_ch.read(), "Student ID:", id_ch.read())
    
finally:
    dev.disconnect()
