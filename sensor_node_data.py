# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import struct

RAW_DATA_BYTES_READ = 54
TIME_BETWEEN_READS = 2000  # milliseconds between sensor reading
DATA_BYTES_READ_PER_SESSION = 50000  # reading once a second, will be 43200 in 12 hours, so this will cover 13.8 hours

COEFFS = [0, 0, 0, 0, 0, 0, 0.2161, 0, 0, 0, 0, 0, 9.19]
# COEFFS = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
# COEFFS = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
USE_COEFF_DICT = False
COEFF_DICT = dict()
COEFF_DICT['const'] = -2.1540
COEFF_DICT[450] = 14.92
COEFF_DICT[600] = 4.56
COEFF_DICT[650] = -14.79
COEFF_DICT[730] = 0.06
COEFF_DICT[450] = (-15.9, 2)
COEFF_DICT[650] = (17.11, 2)
COEFF_DICT[730] = (-1.61, 2)

WAVELENGTHS = [450, 500, 550, 570, 600, 650, 610, 680, 730, 760, 810, 860]


class SensorHubData(object):
    def __init__(self, sensor_numbers):
        self.sensors = []  # make list of sensor
        self.color_graph = None  # placeholder, main will make graph after this
        self.temp_graph = None
        for i in range(sensor_numbers):
            print('making sensor: ', i)
            self.sensors.append(SensorData(i))

    def add_graphs(self, color_graph, temp_graph):
        self.color_graph = color_graph
        self.temp_graph = temp_graph

    def add_data(self, data, bin_data):
        print('add out: ', data)
        if self.data_has_error(data):
            print('error in data packet')
            return
        # the first entry of the data is the sensor number (1 indexed, not 0 so add 1) so add data to that sensor
        self.sensors[data[0]].add_data(data, bin_data)
        # self.sensors[data[0]].add_data(data, bin_data)

    @staticmethod
    def data_has_error(data):
        if data[0] > 2:
            return True
        return False


class SensorData(object):
    def __init__(self, sensor_number):
        self.raw_color_data = np.zeros(DATA_BYTES_READ_PER_SESSION,
                                       dtype=[('sequence', np.uint16),
                                              ('time', 'datetime64[s]'),
                                              ('temp', np.float32),
                                              ('spectro_data', np.float32, (1, 12))])
        print('size:', self.raw_color_data.nbytes)
        # the color index is lights on reading minus the lights off reading so there are only half the data points
        self.color_index = np.zeros(DATA_BYTES_READ_PER_SESSION//2, dtype=np.float32)
        self.time_series = np.zeros(DATA_BYTES_READ_PER_SESSION//2, dtype='datetime64[s]')  # same as color index
        self.temp_data = np.zeros(DATA_BYTES_READ_PER_SESSION, dtype=np.float32)
        print(self.temp_data)
        self.sequence_data = np.zeros(DATA_BYTES_READ_PER_SESSION, dtype=np.int16)
        self.last_sequence = -10  # guarantee the sequence is out of order first time to get a time stamp

        self.current_index = 0
        self.filename = "sensor_{0}_{1}.npy".format(sensor_number, datetime.datetime.now().strftime("%m-%d-%H"))
        # self.filename = "test.npy"
        print('filename :', self.filename)
        self.last_saved_index = 0
        self.plot_index = 0
        self.last_off_color_index = None

    def add_data(self, data, bin_data):
        print('add in: ', data)
        # print(bin_data)
        if data[1] == self.last_sequence:
            # print('duplicate data')
            return
        elif data[1] == self.last_sequence + 1:
            # print('pre time')
            seq_time = self.raw_color_data[self.current_index-1]['time'] + np.timedelta64(TIME_BETWEEN_READS, 'ms')
            print('sed time: ', seq_time, self.current_index)
            self.raw_color_data[self.current_index]['time'] = seq_time
        else:
            print('starting time: ')
            self.raw_color_data[self.current_index]['time'] = datetime.datetime.now()
            print('starting time: ', self.raw_color_data[self.current_index]['time'])

        self.raw_color_data[self.current_index]['sequence'] = data[1]
        self.last_sequence = data[1]
        self.raw_color_data[self.current_index]['temp'] = data[2]
        self.temp_data[self.current_index] = data[2]
        self.raw_color_data[self.current_index]['spectro_data'] = data[3:]

        self.process_data(data)

        self.current_index += 1
        # self.current_index += 1
        # print(self.raw_color_data[self.current_index-1])
        self.last_sequence = data[1]


        with open(self.filename, 'ab') as _f:
            _f.write(bin_data)
        _f.close()

    def data_has_error(self, data):
        if data[0] > 4:
            return True
        return False

    def process_data(self, data):

        # if the data is even number, the LED should be on
        if (data[1] % 2 == 0) and self.last_off_color_index is not None:
            # self.color_index[self.plot_index] = self.calculate_raw_color_index() - self.last_off_color_index
            self.color_index[self.plot_index] = self.calculate_raw_color_index()
            self.time_series[self.plot_index] = self.raw_color_data[self.current_index]['time']
            self.plot_index += 1
        else:
            self.last_off_color_index = self.calculate_raw_color_index()

    def calculate_raw_color_index(self):
        if USE_COEFF_DICT:
            self.color_index = COEFF_DICT['const']
            for key, value in COEFF_DICT:
                print('===========')
                print(key, value)

        else:
            color_index = COEFFS[-1]
            for i, data_pt in enumerate(self.raw_color_data[self.current_index]['spectro_data'][0]):
                color_index += data_pt * COEFFS[i]
            # print('returning color index: ', color_index, self.raw_color_data[self.current_index]['spectro_data'])
            return color_index

    def save_data(self):
        self.raw_color_data[:self.current_index].tofile('test.fsg_nu')

    def plot(self):
        time = self.raw_color_data[:self.current_index]['time']
        xfmt = mdates.DateFormatter('%H:%M:%S')

        y = self.color_index[:self.current_index]
        ax = plt.subplot(111)
        ax.plot(time, y)
        ax.xaxis.set_major_formatter(xfmt)
        # ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        plt.show()


class SavedSensorData():
    def __init__(self, sensor_number):
        self.sensor_number = sensor_number
        self.data = {}
        self.data["Temperature"] = []
        for wavelength in WAVELENGTHS:
            self.data["{0} nm".format(wavelength)] = SavedDataStruct()
        self.time = []
        self.current_time = 0
        self.last_lights_off = 0
        self.color_index = []
        # self.tag = 0
        self.last_sequence = None
        self.last_packet = None

    def __iter__(self):
        for key in self.data:
            # print("yielding: ", key)
            # print('data: ', self.data[key])
            yield key, self.data[key]

    def add_data(self, data_packet):
        # print("adding start")
        print(len(self.data["450 nm"].lights_on))
        if not self.valid_packet(struct.unpack(">13f", data_packet[2:])):
            print('invalid packet')
            return

        if not self.last_packet:
            # print('sa')
            self.last_packet = data_packet
            self.last_sequence = struct.unpack("<H", data_packet[:2])[0]
            return

        sequence = struct.unpack("<H", data_packet[:2])[0]
        # print('sb', sequence, self.last_sequence)
        if (sequence - 1) == self.last_sequence:  # sequence is in order
            # print('adding ok')
            if (sequence % 2) == 1:  # this is a lights off sequence
                # print('adding 1')
                self.last_lights_off = struct.unpack(">13f", data_packet[2:])
                # the last packet saved had the lights on
                self.last_lights_on = struct.unpack(">13f", self.last_packet[2:])
            else:  # this is a lights on sequence
                # print('adding 2')
                self.last_lights_on = struct.unpack(">13f", data_packet[2:])
                # the last packet saved had the lights off
                self.last_lights_off = struct.unpack(">13f", self.last_packet[2:])
            # check if both a lights on and lights on data set is ready
            self.parse_packets(self.last_lights_on, self.last_lights_off)
        else:  # sequence is out of order so reset the last sequence and data packet
            self.last_sequence = sequence
            self.last_packet = data_packet

    def parse_packets(self, lights_on_packet, lights_off_packet):
        diff_data = []
        for i, data_pt in enumerate(lights_on_packet):
            diff_data.append(data_pt- lights_off_packet[i])
        for i, data_line in enumerate(self.data):
            if data_line == "Temperature":
                self.data[data_line].append(lights_on_packet[i])
                continue  # skip adding the temperature data for now
            # the data_line, i.e. "450 nm" data is the ith data in the data packet
            self.data[data_line].lights_on.append(lights_on_packet[i])
            self.data[data_line].lights_off.append(lights_off_packet[i])
            self.data[data_line].difference.append(lights_on_packet[i]-lights_off_packet[i])
            self.calc_color_index(diff_data)

    def calc_color_index(self, data):
        if USE_COEFF_DICT:
            color_index = COEFF_DICT['const']
            for key, value in COEFF_DICT.items():
                if key == 'const':
                    continue
                wave_index = WAVELENGTHS.index(key) + 1  # add one to compensate for temperature in struct
                print(data)
                print(key, value, wave_index, type(value))
                if type(value) is tuple:
                    print()
                    color_index += value[0]*data[wave_index]**value[1]
                else:
                    color_index += value * data[wave_index]
        else:
            color_index = COEFFS[-1]
            print(data)
            for i, data_pt in enumerate(data[1:]):
                print(i, data_pt)
                color_index += data_pt * COEFFS[i]  # do not need -1 because enumerate starts
                # at 0 for the second (index 1) data point so temperature data point is ignored

        print('color index: ', color_index)
        self.color_index.append(color_index)


    def add_data_old(self, data_packet):
        print('add data: ', data_packet)
        sequence = struct.unpack("<H", data_packet[:2])
        print("sequence: ", sequence, (sequence[0] % 2))
        data = struct.unpack(">13f", data_packet[2:])
        if not self.last_sequence:

            self.last_sequence = sequence[0]
        elif (self.last_sequence + 1 != sequence[0]):
            self.last_sequence = sequence[0]
            print("returning ")
            return  # sequence out of sequnce

        for i, data_line in enumerate(self.data):
            if data_line == "Temperature":
                self.data[data_line].append(data[i])
                continue  # skip adding the temperature data for now
            # print('data line: ', data_line, self.tag)
            # print(self.data[data_line])
            if hasattr(self.data[data_line], "difference"):
                # print("diff:", self.data[data_line].difference)
                # print('on:', self.data[data_line].lights_on)
                # print('off:', self.data[data_line].lights_off)
                pass

            if (sequence[0] % 2) == 1:
                print(data_line)
                print("add lights off", sequence, data)

                self.data[data_line].lights_off.append(data[i])
                self.last_lights_off = data[i]
                self.time.append(self.current_time)
                self.current_time += 1
            else:
                print("add lights on", sequence, data)

                self.data[data_line].lights_on.append(data[i])
                self.data[data_line].difference.append(data[i] -
                                                       self.last_lights_off)
                # print("adding deiff: ", self.data[data_line].difference)

        if data_line != "Temperature":
            print(self.data[data_line], data_line)
            print('llkj:', len(self.data[data_line].lights_on),
                           len(self.data[data_line].lights_off),
                           len(self.data[data_line].difference))
        # print('data:', self.data)
        # self.tag = (self.tag + 1) % 2
        self.last_sequence = sequence[0]

    def plot(self):
        pass

    @staticmethod
    def valid_packet(packet):
        print('valid packet: ', packet)
        for data_pt in packet:
            if data_pt != 0.0:
                return True
        return False

    # def fit_data(self):
    #     if USE_COEFF_DICT:
    #         y = COEFF_DICT['const']
    #         for wavelength in WAVELENGTHS:


class SavedDataStruct:
    def __init__(self):
        self.lights_off = []
        self.lights_on = []
        self.difference = []


if __name__ == "__main__":
    data = SensorHubData()
    data1 = (1, 0, 1.0, 10.0, 20.0, 30.0, 40.0, 50.0,
             60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0)
    data2 = (1, 1, 2.0, 11.0, 21.1, 31.0, 41.0, 51.0,
             61.0, 71.0, 81.0, 91.0, 101.0, 111.0, 121.0)
    data3 = (1, 2, 3.0, 12.0, 22.0, 32.0, 42.0, 52.0,
             62.0, 72.0, 82.0, 92.0, 102.0, 112.0, 122.0)
    data.add_data(data1)
    data.add_data(data2)
    data.add_data(data3)
    data.save_data()

    data.plot()
