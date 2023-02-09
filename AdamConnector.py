import serial
import time
import re


def get_temps():
    return AdamConnector().get_temps()


def get_inputs():
    return AdamConnector().get_inputs()


def get_relays():
    return AdamConnector().get_relays()


def set_relay(ch, state):
    AdamConnector().set_relay(ch, state)


def set_output(ch, value):
    AdamConnector().set_output(ch, value)


class AdamConnector:

    def __init__(self, port='COM3', address=2, temp_slot=0, relay_slot=1, input_slot=2,
                 output_slot=3):
        self.address = address
        self.temp_slot = temp_slot
        self.relay_slot = relay_slot
        self.input_slot = input_slot
        self.output_slot = output_slot
        self.port = port

    def get_temps(self):
        return self._get_analogs(self.temp_slot)

    def get_inputs(self):
        return self._get_analogs(self.input_slot)

    def _get_analogs(self, slot):
        try:
            with serial.Serial(port=self.port) as ser:
                ser.write(
                    ("#" + "{:02d}".format(self.address) + "S" + "{:01d}".format(slot) + "\r\n").encode())
                time.sleep(0.1)
                out = ''
                while ser.inWaiting() > 0:
                    out += ser.read(1).decode()
                if out.startswith(">"):  # check if the received data starts with ">"
                    return self._extract_numbers(out)
                else:
                    print("Received data is not in the expected format.")
        except serial.SerialException as e:
            print("Error opening or communicating with the serial port:", e)

    def _extract_numbers(self, s):
        s = s[1:]
        elements = re.split("[+-]", s[1:])
        numbers = [float(elem) if elem != '' else 0 for elem in elements]
        signs = [*''.join([i for i in s if i == '+' or i == '-'])]
        for i, sign in enumerate(signs):
            if sign == '-':
                numbers[i] = numbers[i] * -1
        return numbers

    def get_relays(self):
        try:
            with serial.Serial(port=self.port) as ser:
                ser.write(
                    ("$" + "{:02d}".format(self.address) + "S" + "{:01d}".format(self.relay_slot) + "6\r\n").encode())
                time.sleep(0.1)
                response = ''
                while ser.inWaiting() > 0:
                    response += ser.read(1).decode()
                if response:
                    return self._convert_hex_to_bool_list(response)
                else:
                    raise ValueError("No response received from the serial port")
        except (serial.SerialException, ValueError) as e:
            print(f"Error communicating with the serial port: {e}")

    def _convert_hex_to_bool_list(self, hex_str):
        if not hex_str.startswith("!"):
            raise ValueError("Received data is not in the expected format.")

        cleaned_str = re.sub(r'[^a-zA-Z0-9]+', '', hex_str)[2:][:2]
        bool_list = []
        for char in cleaned_str:
            temp_list = []
            hex_value = int(char, 16)
            for i in range(4):
                temp_list.append(True if hex_value & (1 << i) else False)
            temp_list.reverse()
            bool_list.extend(temp_list)
        return bool_list[2:]

    def set_relay(self, ch, state):
        try:
            with serial.Serial(port=self.port) as ser:
                val = '0'
                if state is True:
                    val = '1'
                ser.write(
                    ("#" + "{:02d}".format(self.address) + "S" + "{:01d}".format(self.relay_slot) + "1" + str(
                        ch) + '0' + val + "\r\n").encode())
                time.sleep(0.01)
        except serial.SerialException as e:
            print("Error opening or communicating with the serial port:", e)

    def set_output(self, ch, value):
        try:
            with serial.Serial(port=self.port) as ser:
                ser.write(
                    ("#" + "{:02d}".format(self.address) + "S" + "{:01d}".format(self.output_slot) + "C" + str(
                        ch) + "{:06.3f}".format(value) + "\r\n").encode())
                time.sleep(0.01)
        except serial.SerialException as e:
            print("Error opening or communicating with the serial port:", e)
