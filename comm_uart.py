# Copyright (c) 2018-2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Communication protocols to read data through the USB-UART, currently just print what is read in
"""

# standard libraries
import binascii
import logging
import queue
import serial
import serial.tools.list_ports
import struct
import threading
import time

# USB-UART Constants
DESCRIPTOR_NAME = "FT230X Basic UART"
BAUD_RATE = 115200
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS


class PyComComm(object):
    def __init__(self, data_length, data_in_queue: queue.Queue=None, data_out_queue:
                 queue.Queue=None, port: serial.Serial=None):
        """
        Construct an object that abstracts the communication protocol.  Custom calls should be put in here
        :param data_in_queue: queue.Queue to put data from the device in,
        if None they will just be printed to the console
        :param data_out_queue: queue.Queue to read to put to the device.  If get() pulls a string, the string
        is treated as hex symbols and converted before being passed through USB(with spaces and : removed first).
        If bytes are pulled
        :param data_length: how many bytes of data contain a packet, if None use a separator sequence
        :TODO add protocol to use data packet separators
        :TODO add in protocol to read length like in CySmart
        """
        if data_out_queue:
            self.to_device = data_out_queue
        else:
            self.to_device = queue.Queue()
        if data_in_queue:
            self.from_device = data_in_queue
            self.print_message = False
        else:
            self.from_device = queue.Queue()
            self.print_message = True
        self.reading = False
        self.wait_for_packet = threading.Event()
        self.packet_length = data_length
        self.device = port
        if not port:
            self.auto_find_com_port()

        serial_thread = SerialHandler(self.device, self.from_device, self.to_device, self.wait_for_packet, data_length)
        serial_thread.start()
        self.reading = True
        self.start_streaming()

    def start_streaming(self):
        while self.reading:
            self.wait_for_packet.wait()
            if self.print_message:
                print("got package:")
                new_data = self.from_device.get()
                print(new_data)
                print(struct.unpack('=BHfffffffffffff', new_data))
                # else another section needs to get the queue
        logging.debug("Ending streaming")

    def stop_streaming(self):
        self.reading = False

    def auto_find_com_port(self):
        available_ports = serial.tools.list_ports
        print(available_ports)
        for port in available_ports.comports():  # type: serial.Serial
            print("port:", port)
            print(port.device)
            print(port.name)
            print(port.description)
            if DESCRIPTOR_NAME in port.description:
                print("Port found: ", port)
                self.device = serial.Serial(port.device, baudrate=BAUD_RATE, stopbits=STOP_BITS,
                                            parity=PARITY, bytesize=BYTE_SIZE, timeout=1)
                time.sleep(0.5)
                print(self.device.read_all())

class SerialHandler(threading.Thread):
    """
    Class to handle IO of USB-UART on seperate thread.
    Checks queue to output data to the device and
    collects input bytes and assembles them into packets
    """
    def __init__(self, port: serial.Serial, in_queue: queue.Queue, out_queue: queue.Queue,
                 data_ready: threading.Event, packet_length: int):
        threading.Thread.__init__(self)
        self.comm_port = port
        self.input = in_queue
        self.output = out_queue
        self.packet_ready = data_ready
        self.data_length = None
        self.separator = None
        self.running = False
        self.data_length = packet_length
        self.packet = b""

    def run(self):
        self.running = True
        self.comm_port.write(b'hub.start()\r')
        print('sending start')
        while self.running:
            # print(self.comm_port.in_waiting)
            time.sleep(5)
            print('run')
            self.comm_port.write(b'hub.read_data()\r')
            if not self.output.empty():
                self.send_command()
            elif self.comm_port.in_waiting:
                self.packet = self.comm_port.read_all()
                print('packet: ', self.packet)
                print('split packet: ')
                print(self.packet.split(b'>>> '))
                # parse the data packet
                self.parse_input()

    def parse_input(self):
        # chop last 3 bytes that is the b'>>> ' put on by REPL and the echo ended with a \r\n
        packets = self.packet[:-4].split(b'\r\n')[1:]
        self.packet = b"".join(packets)
        print(self.packet)
        print(len(self.packet))
        while len(self.packet) >= self.data_length:
            self.input.put(self.packet[:self.data_length])
            self.packet = self.packet[self.data_length:]
            self.packet_ready.set()

    def send_command(self):
        command_to_send = self.to_device_queue.get()
        # check if its a string and has to be processed
        if type(command_to_send) is str:
            command_to_send = convert_to_bytes(command_to_send)
        elif type(command_to_send) is not bytes:
            raise AttributeError("Must input a string or byte")



def convert_to_bytes(_string: str) -> bytes:
    """
    Take an input string of hex numbers (0-F) and convert bytes string
    Note: For some reason strip() was not working when I wrote this so I used replace
    :param _string: string of hex values (0-F)
    :return: bytes string
    """
    # print('input string: ', _string)
    # print("hold: ", _string.replace(b' ', b'').replace(b':', b''))
    # print('new string: ', binascii.unhexlify(_string.replace(b' ', b'').replace(b':', b'')))
    print('llll')
    print(_string, type(_string))
    return binascii.unhexlify(_string.replace(' ', '').replace(':', ''))


if __name__ == '__main__':
    PyComComm(55)
