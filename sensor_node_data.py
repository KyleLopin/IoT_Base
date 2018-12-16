# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import datetime
import numpy as np

RAW_DATA_BYTES_READ = 54
DATA_BYTES_READ_PER_SESSION = 50000  # reading once a second, will be 43200 in 12 hours, so this will cover 13.8 hours


class SensorHubData(object):
    def __init__(self):
        self.raw_color_data = np.zeros((DATA_BYTES_READ_PER_SESSION),
                                       dtype=[('sequence', np.uint16),
                                              ('time', 'datetime64[s]'),
                                              ('temp', np.float32),
                                              ('AS7262_data', np.float32, (1, 6)),
                                              ('AS7263_data', np.float32, (1, 6))])
        print('size:', self.raw_color_data.nbytes)
        self.color_index = np.array([], dtype=np.float32)
        self.temp_data = np.array([], dtype=np.float32)
        self.sequence_data = np.array([], dtype=np.int16)
        self.last_sequence = -10  # guarantee the sequence is out of order first time to get a time stamp
        self.time_stamps = []  # list of tuples with (index, time_stamp) for when the sequence numbers are off
        self.current_index = 0

    def add_data(self, data):
        print('add: ', data)
        self.raw_color_data[self.current_index]['time'] = datetime.datetime.now()
        self.raw_color_data[self.current_index]['sequence'] = data[1]
        self.raw_color_data[self.current_index]['temp'] = data[2]
        self.raw_color_data[self.current_index]['AS7262_data'] = data[3:9]
        self.raw_color_data[self.current_index]['AS7263_data'] = data[9:]
        self.current_index += 1
        print(self.raw_color_data[self.current_index-1])

    def save_data(self):
        print(self.raw_color_data[:self.current_index])


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
