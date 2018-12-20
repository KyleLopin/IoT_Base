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
# local files
import sensor_node_data  # for type hinting

# USB-UART Constants
DESCRIPTOR_NAME_WIN = "USB Serial Port"
DESCRIPTOR_NAME_MAC = "FT230X Basic UART"
BAUD_RATE = 115200
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS

DETECTION_MESSAGE = b"Echo this when done"
PRE_DATA_STR = b"Data:b'"
LEN_PRE_DATA_STR = len(PRE_DATA_STR)

LEN_DATA_PACKET_BYTES = 55
LEN_DATA_PACKET_CHARS = 2 * LEN_DATA_PACKET_BYTES


class PyComComm(threading.Thread):
    def __init__(self, data_struct: sensor_node_data.SensorHubData,
                 data_length, data_in_queue: queue.Queue=None, data_out_queue:
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
        threading.Thread.__init__(self)
        self.data = data_struct
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
        self.packet_length = data_length * 2  # the data is coming in hexified so each byte of data is 2 bytes long
        # i.e. 1 is sent as 01 and 255 is sent as ff
        self.device = port
        if not port:
            self.auto_find_com_port()

        self.serial_thread = SerialHandler(self.device, self.from_device, self.to_device, self.wait_for_packet, data_length)
        # self.start_streaming()

    def run(self):
        print('starting to stream')
        self.reading = True
        self.serial_thread.start()
        while self.reading:
            self.wait_for_packet.wait()
            if self.print_message:
                new_data = self.from_device.get()
                print("got package: ", new_data)
                if len(new_data) == 55:
                    new_data = struct.unpack('=BHfffffffffffff', new_data)
                    self.data.add_data(new_data)

                else:
                    print("data not right length")
                # else another section needs to get the queue
        logging.debug("Ending streaming")

    def stop(self):
        self.serial_thread.stop_running()
        self.reading = False
        self.wait_for_packet.set()  # set last event so the run will proceed for the last time
        self.serial_thread.running = False

    def auto_find_com_port(self):
        available_ports = serial.tools.list_ports
        print(available_ports)
        for port in available_ports.comports():  # type: serial.Serial
            print("port:", port, DESCRIPTOR_NAME_WIN in port.description)
            print('check: ', DESCRIPTOR_NAME_WIN, port.description)
            print(port.device)
            print(port.name)
            print(port.description)
            if DESCRIPTOR_NAME_WIN in port.description or DESCRIPTOR_NAME_MAC in port.description:
                try:
                    print("Port found: ", port)
                    self.device = serial.Serial(port.device, baudrate=BAUD_RATE, stopbits=STOP_BITS,
                                                parity=PARITY, bytesize=BYTE_SIZE, timeout=1)
                    print("returning from autofind")
                    return  # a device could connect without an error so return
                except Exception as error:  # didn't work so try other ports
                    print("Port access error: ", error)

    def initialize_device(self):
        done_initializing = False
        read_message = b""
        time.sleep(1)
        print("initializing device")
        self.device.write("print('{0}')".format(DETECTION_MESSAGE))
        while not done_initializing:
            time.sleep(0.5)
            read_message += self.device.readall()
            print("read so far: ")
            print(read_message)
            if DESCRIPTOR_NAME_WIN in read_message:
                print("Done initializing")


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
        self.separator = None
        self.running = False
        self.data_length = packet_length  # how many data bytes to read
        # length of data packet with header and footer (+2 is for the \r\n at the end of packet)
        self.data_packet_length = packet_length + len(PRE_DATA_STR) + 2
        self.packet = b""
        self.remaining_packet = b""

    def run(self):
        self.running = True
        if not self.comm_port:  # no device so just return
            return
        self.comm_port.write(b'read_data()\r')
        print('sending start')
        while self.running:
            time.sleep(0.1)  # ease the load on the computer
            if not self.output.empty():
                self.send_command()
            if self.comm_port.in_waiting:
                packet = self.comm_port.readline()
                # if self.remaining_packet:  # extra data was picked up on the end of previous data so add it in now
                #     packet = PRE_DATA_STR + self.remaining_packet + packet  # parse_inputs needs to see the PRE_DATA_STR
                #     self.remaining_packet = b""
                # print('packet1: ', packet)
                # parse the data packet
                self.parse_input(packet)

    def parse_input(self, packet: str):
        print('packet2: ', packet)
        if packet.startswith(PRE_DATA_STR):
            print('got data')
            if self.remaining_packet:
                data = self.remaining_packet + packet[LEN_PRE_DATA_STR:-3]
                self.remaining_packet = None
            else:
                data = packet[LEN_PRE_DATA_STR:-3]  # slice the bytes hexiflied string by removing the Data:b' at the start
            # and the '\r\n 3 bytes at the end
            print(data)
            # TODO: put the packet and set the flag
            self.parse_data_packet(data)
        else:
            print('non-data packet')

    def parse_data_packet(self, data_packet):
        # check if one or more data sets were sent
        print('len: ', len(data_packet))
        if len(data_packet) == LEN_DATA_PACKET_CHARS:
            print('putting packet a: ', data_packet)
            self.input.put(convert_to_bytes(data_packet))
            self.packet_ready.set()
        elif len(data_packet) > LEN_DATA_PACKET_CHARS:
            while len(data_packet) > LEN_DATA_PACKET_CHARS:
                print('putting data: ', data_packet[:LEN_DATA_PACKET_CHARS])
                self.input.put(convert_to_bytes(data_packet[:LEN_DATA_PACKET_CHARS]))
                data_packet = data_packet[LEN_DATA_PACKET_CHARS:]
                print('len remaining data: ', len(data_packet), data_packet)
            # self.remaining_packet = data_packet
            self.packet_ready.set()

    def parse_input_old(self):
        print("len input: ", len(self.packet))
        if len(self.packet) < self.data_packet_length:
            print("too short, return")
            return  # wait for more bytes to parse
        # check that the packet starts with the pre-data string
        pre_string_index = self.packet.find(PRE_DATA_STR)
        print("pre string index: ", pre_string_index)
        if pre_string_index != 0:
            # the packet does start with the pre-data string, so chop the front of the string till it does
            self.packet = self.packet[pre_string_index:]
            self.parse_input()  # recheck the input length
        # there is a packet of the format b'Data:010001.....\r\n'
        # chop the Data: part off
        packet = self.packet[LEN_PRE_DATA_STR+2:]  # add 2 to get rid of the the b" at the start

        print('db1: ', packet)
        print(len(packet))

        # remove the '\r\n 3 bytes at end
        # i.e. = packet:  b"Data:b'010d1a8054a9470055a9478055a9470056a9478056a9470057a9478057a9470058a9478058a9470059a9478059a947005aa947805aa947'\r\n"
        # len input:  120
        # pre string index:  0
        # db1:  b"010d1a8054a9470055a9478055a9470056a9478056a9470057a9478057a9470058a9478058a9470059a9478059a947005aa947805aa947'\r\n"
        # 113
        # b'Data:'
        # data not right length

        while len(self.packet) >= self.data_length:
            self.input.put(self.packet[:self.data_length])
            self.packet = self.packet[self.data_length:]
            self.packet_ready.set()

    def stop_running(self):
        print("Stoping")
        self.comm_port.write(b'stop_reading_data()\r')
        self.running = False

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
    if type(_string) is str:
        return binascii.unhexlify(_string.replace(' ', '').replace(':', ''))
    elif type(_string) is bytes:
        return binascii.unhexlify(_string.replace(b' ', b'').replace(b':', b''))
    else:
        raise Exception("Use string or byte string")


if __name__ == '__main__':
    # PyComComm(55)
    print(convert_to_bytes("01:04"))
