from pymodbus.client import ModbusSerialClient as ModbusClient
import struct
import time


def get_temp():
    return KS90Connector().read_temp()


class KS90Connector:
    def __init__(self, port='COM3', address=1):
        self.address = address
        self.port = port

    def read_temp(self):
        # Connection to the modbus client
        client = ModbusClient(method="rtu", port=self.port, stopbits=1, bytesize=8, parity='E', baudrate=9600)
        client.connect()

        # Read the register
        result = client.read_holding_registers(35112, 2, 1)

        # Convert result to float
        byte_data = struct.pack("!HH", result.registers[0], result.registers[1])
        float_val = struct.unpack('>f', byte_data)[0]

        # Close the connection
        client.close()

        time.sleep(0.4)

        return float_val
