class StudentIDService{
public:
    const static uint16_t STUDENTID_SERVICE_UUID =0x9000;
    const static uint16_t STUDENTID_VALUE_CHARACTERISTIC_UUID =0x9001;
    StudentIDService(BLE &_ble, uint64_t student_id_init):
        ble(_ble), 
        StudentID(STUDENTID_VALUE_CHARACTERISTIC_UUID, &student_id_init, GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY)
    {
        GattCharacteristic *charTable[] = {&StudentID};
        GattService         StudentIDService(StudentIDService::STUDENTID_SERVICE_UUID, charTable, sizeof(charTable) / sizeof(GattCharacteristic *));
        ble.gattServer().addService(StudentIDService);
    }
    void updateStudentID(uint64_t newStuID) {
        ble.gattServer().write(StudentID.getValueHandle(), (uint8_t *)&newStuID, sizeof(uint64_t));
    }


private:
    BLE                                        &ble;
    ReadOnlyGattCharacteristic<uint64_t>               StudentID;
    
};