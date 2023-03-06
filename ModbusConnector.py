from pymodbus.client import ModbusSerialClient as ModbusClient
import struct
import time


def get_temps():
    return ModbusConnector().read_temps()


class ModbusConnector:
    def __init__(self, port='COM3', address_ks=1, address_re=3):
        self.address_ks = address_ks
        self.address_re = address_re
        self.port = port

    def read_temps(self):
        # Connection to the modbus client
        client = ModbusClient(method="rtu", port=self.port, stopbits=1, bytesize=8, parity='E', baudrate=9600)
        client.connect()

        # Read the KS90
        result = client.read_holding_registers(35112, 2, self.address_ks)

        # Convert result to float
        byte_data = struct.pack("!HH", result.registers[0], result.registers[1])
        float_val_ks = struct.unpack('>f', byte_data)[0]

        # Read the RE72
        result = client.read_holding_registers(7000, 2, self.address_re)

        # Convert result to float
        byte_data = struct.pack("!HH", result.registers[0], result.registers[1])
        float_val_re = struct.unpack('>f', byte_data)[0]

        # Close the connection
        client.close()

        time.sleep(0.4)

        return [round(float_val_ks, 1), round(float_val_re, 1)]
