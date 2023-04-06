from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
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

        # Read the KS90 actual temp
        result = client.read_holding_registers(35112, 2, self.address_ks)

        # Convert result to float
        byte_data = struct.pack("!HH", result.registers[0], result.registers[1])
        float_val_ks = struct.unpack('>f', byte_data)[0]

        # Read the RE72 actual temp
        result = client.read_holding_registers(7000, 2, self.address_re)

        # register 4084 int32 / 10
        # register 7008 32??

        # Convert result to float
        byte_data = struct.pack("!HH", result.registers[0], result.registers[1])
        float_val_re = struct.unpack('>f', byte_data)[0]

        # Close the connection
        client.close()

        # read KS output status
        result = client.read_holding_registers(4380, 1, self.address_ks)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        out_ks = float(decoder.decode_16bit_uint())
        print(out_ks)

        # read KS setpoint
        result = client.read_holding_registers(3180, 1, self.address_ks)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        sp_ks = float(decoder.decode_16bit_int())
        print(sp_ks)

        # read RE setpoint
        result = client.read_holding_registers(4084, 1, self.address_re)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        sp_re = float(decoder.decode_16bit_int()) / 10

        # read RE output status
        result = client.read_holding_registers(4009, 1, self.address_re)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        out_re = float(decoder.decode_16bit_uint()) / 10
        if out_re > 50.0:
            out_re = 1
        else:
            out_re = 0

        time.sleep(0.4)

        return [round(float_val_ks, 1), round(float_val_re, 1), sp_ks, sp_re, out_ks, out_re]

    def write_re_sp(self, sp):
        sp = sp * 10
        client = ModbusClient(method="rtu", port=self.port, stopbits=1, bytesize=8, parity='E', baudrate=9600)
        client.connect()

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        builder.add_16bit_int(int(sp))

        client.write_registers(4084, values=builder.to_registers(), slave=self.address_re)
        client.close()
        time.sleep(0.4)

    def write_ks_sp(self, sp):
        client = ModbusClient(method="rtu", port=self.port, stopbits=1, bytesize=8, parity='E', baudrate=9600)
        client.connect()

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        builder.add_16bit_int(int(sp))

        client.write_registers(3180, values=builder.to_registers(), slave=self.address_ks)
        client.close()

        time.sleep(0.4)