# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

RAW_DATA_BYTES_READ = 54
TIME_BETWEEN_READS = 2000  # milliseconds between sensor reading
DATA_BYTES_READ_PER_SESSION = 50000  # reading once a second, will be 43200 in 12 hours, so this will cover 13.8 hours

# COEFFS = [0, 0, 0, 0, 0, 0, -0.2161, 0, 0, 0, 0, 0, 9.19]
COEFFS = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]


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
        print('add in: ', data, type(bin_data))
        # print(bin_data)
        if data[1] == self.last_sequence:
            # print('duplicate data')
            return
        elif data[1] == self.last_sequence + 1:
            # print('pre time')
            seq_time = self.raw_color_data[self.current_index-1]['time'] + np.timedelta64(TIME_BETWEEN_READS, 'ms')
            # print('sed time: ', seq_time)
            self.raw_color_data[self.current_index]['time'] = seq_time
        else:
            self.raw_color_data[self.current_index]['time'] = datetime.datetime.now()

        self.raw_color_data[self.current_index]['sequence'] = data[1]
        self.last_sequence = data[1]
        self.raw_color_data[self.current_index]['temp'] = data[2]
        self.temp_data[self.current_index] = data[2]
        self.raw_color_data[self.current_index]['spectro_data'] = data[3:]

        self.process_data(data)

        self.current_index += 1
        # print(self.raw_color_data[self.current_index-1])
        self.last_sequence = data[1]


        with open(self.filename, 'ab') as _f:
            _f.write(bin_data)
        _f.close()
        # if self.current_index % 5 == 0:
            # print('====SAVING DATA ========', self.filename)
            # print(self.raw_color_data[self.last_saved_index:self.current_index][:])
            # every minute save data to temp file
            # self.raw_color_data[:self.current_index-1].tofile(self.temp_filename)
            # self.raw_color_data[:self.current_index-1].savetxt(self.temp_filename)
            # np.savetxt(self.filename, self.raw_color_data, fmt='%u, %M, %.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f')
            # return

            # np.save(self.filename, self.raw_color_data[self.last_saved_index:self.current_index])
            # self.last_saved_index = self.current_index - 1

            # with open(self.filename, 'ab') as _f:
            #     np.save(_f, self.raw_color_data[self.last_saved_index:self.current_index][:])
            #     self.last_saved_index = self.current_index-1
            # _f.close()

    def data_has_error(self, data):
        if data[0] > 4:
            return True
        return False

    def process_data(self, data):
        if (data[1] % 2 == 0) and self.last_off_color_index is not None:
            self.color_index[self.plot_index] = self.calculate_raw_color_index() - self.last_off_color_index
            self.time_series[self.plot_index] = self.raw_color_data[self.current_index]['time']
            self.plot_index += 1
        else:
            self.last_off_color_index = self.calculate_raw_color_index()

    def calculate_raw_color_index(self):
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
