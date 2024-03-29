from AdamConnector import AdamConnector
from KS90Connector import KS90Connector
import time

if __name__ == '__main__':
    ks = KS90Connector(port='/dev/cu.usbserial-A10NAKJG')
    print(ks.read_temp())

    adam = AdamConnector(port='/dev/cu.usbserial-A10NAKJG')
    # adam.set_output(0, 0.69)
    # adam.set_output(1, 2)
    # adam.set_output(2, 3)
    # adam.set_output(3, 10)
    # time.sleep(1)
    print(adam.get_temps())
    # print(adam.get_inputs())
    # adam.set_relay(0, True)
    # adam.set_relay(1, False)
    # adam.set_relay(2, True)
    # adam.set_relay(3, True)
    # adam.set_relay(4, False)
    # adam.set_relay(5, True)
    print(adam.get_relays())
    ks = KS90Connector(port='/dev/cu.usbserial-A10NAKJG')
    print(ks.read_temp())
