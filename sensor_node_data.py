# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import time

RAW_DATA_BYTES_READ = 54
DATA_BYTES_READ_PER_SESSION = 50000  # reading once a second, will be 43200 in 12 hours, so this will cover 13.8 hours

COEFFS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

class SensorHubData(object):
    def __init__(self):
        self.raw_color_data = np.zeros((DATA_BYTES_READ_PER_SESSION),
                                       dtype=[('sequence', np.uint16),
                                              ('time', 'datetime64[s]'),
                                              ('temp', np.float32),
                                              ('spectro_data', np.float32, (1, 12))])
        print('size:', self.raw_color_data.nbytes)
        self.color_index = np.zeros(DATA_BYTES_READ_PER_SESSION, dtype=np.float32)

        self.temp_data = np.zeros(DATA_BYTES_READ_PER_SESSION, dtype=np.float32)
        print(self.temp_data)
        self.sequence_data = np.zeros(DATA_BYTES_READ_PER_SESSION, dtype=np.int16)
        self.last_sequence = -10  # guarantee the sequence is out of order first time to get a time stamp
        self.time_stamps = []  # list of tuples with (index, time_stamp) for when the sequence numbers are off
        self.current_index = 0

    def add_data(self, data):
        print('add: ', data)
        # self.time_stamps[self.current_index] = datetime.datetime.now()
        self.raw_color_data[self.current_index]['time'] = datetime.datetime.now()
        self.raw_color_data[self.current_index]['sequence'] = data[1]
        self.last_sequence = data[1]
        self.raw_color_data[self.current_index]['temp'] = data[2]
        self.temp_data[self.current_index] = data[2]
        self.raw_color_data[self.current_index]['spectro_data'] = data[3:]
        self.process_data()
        self.current_index += 1
        print(self.raw_color_data[self.current_index-1])
        time.sleep(1)

    def process_data(self):
        color_index = 0.0
        for i, data_pt in enumerate(self.raw_color_data[self.current_index]['spectro_data'][0]):
            color_index += data_pt * COEFFS[i]
        self.color_index[self.current_index] = color_index

    def save_data(self):
        self.raw_color_data[:self.current_index].tofile('test.fsg_nu')

    def plot(self):
        time = self.raw_color_data[:self.current_index]['time']
        xfmt = mdates.DateFormatter('%H:%M:%S')

        y = self.color_index[:self.current_index]
        ax=plt.subplot(111)
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
