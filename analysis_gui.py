# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Graphical User Interface to open binary data of sensor input and display it to the user and save it into an easier
to read format
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import logging
import struct
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
# local files
import analysis_graph_frames as graph_frame
import sensor_node_data

DATA_FORMAT_STRING = '>BH13f'
print(struct.calcsize(DATA_FORMAT_STRING))
DATA_PACKET_LEN = struct.calcsize(DATA_FORMAT_STRING)


class PerfectEarthAnalytics(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        self.notebook = ttk.Notebook(self)
        self.raw_color_frames = []
        # self.raw_color_frame = graph_frame.SavedDataGraph(self)
        # self.notebook.add(self.raw_color_frame, text="All Spectra")
        self.summary_frame = graph_frame.SavedDataGraph(self)
        self.notebook.add(self.summary_frame, text="Color Index")

        self.sensor_nodes = {}

        status_frame = tk.Frame(self, height=50, bg='grey')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        control_frame = tk.Frame(self, width=400, bg='grey')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.init_control_frame(control_frame)
        # add at the end so the other frames can expand
        self.notebook.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


    def init_control_frame(self, _frame):
        self.open_button = tk.Button(_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.BOTTOM, padx=10, pady=20)

    def open_file(self):
        filename = open_filename(self, 'open')
        if not filename:
            return  # no file selected so just return
        with open(filename, mode='rb') as _file:
            try:
                data = _file.read()
                _file.close()
            except Exception as error:

                messagebox.showerror(title="Error", message=error)
                self.lift()
                _file.close()
        print(data)
        print('len data: ', len(data), len(data)/56, len(data)-(len(data)//56*56))
        self.parse_data(data)
        print("DONE PARSING -----------", self.sensor_nodes.keys())


        for node in self.sensor_nodes.keys():
            print("Node: ", node)
            # self.raw_color_frame.config(text="Sensor Node {0}".format(node))
            color_frame = graph_frame.SavedDataGraph(self)
            color_frame.plot_data(self.sensor_nodes[node])
            color_frame.pack(fill=tk.BOTH, expand=1)
            self.notebook.add(color_frame, text="Sensor Node {0}".format(node))

            self.summary_frame.plot_index_lines(self.sensor_nodes[node].color_index)
            # self.notebook.tab(self.raw_color_frame, text="Sensor Node {0}".format(node))
        # self.raw_color_frame.plot_data(self.sensor_nodes)

    def parse_data(self, data):
        index = 0
        len_data = len(data)
        while index < len_data - DATA_PACKET_LEN:
            print(data[index:index+DATA_PACKET_LEN])
            sensor_node = struct.unpack("B", data[index:index+1])[0]
            print("sensor node: ", sensor_node)

            if sensor_node not in self.sensor_nodes:
                print("No node ", sensor_node, self.sensor_nodes)
                self.sensor_nodes[sensor_node] = sensor_node_data.SavedSensorData(sensor_node)

            self.sensor_nodes[sensor_node].add_data(data[index+1:index+DATA_PACKET_LEN])

            index += DATA_PACKET_LEN

            # print(struct.unpack(DATA_FORMAT_STRING, data[index:index+DATA_PACKET_LEN]))
            # _struct = list(struct.unpack("<BH", data[index:index+3]))
            # _struct.extend(list(struct.unpack('>13f', data[index+3:index+DATA_PACKET_LEN])))
            # print('struct', _struct)

        # for node in self.sensor_nodes.keys():
        #     print('node:    ', node)
        #     self.sensor_nodes[node] = sensor_node_data.SavedDataStruct(self.sensor_nodes[node])


def open_filename(parent, _type: str) -> str:
    """
    Make a method to return an open file or a file name depending on the type asked for
    :param parent:  master tk.TK or toplevel that called the file dialog
    :param _type:  'open' or 'saveas' to specify what type of file is to be opened
    :return: filename user selected
    """
    """ Make the options for the save file dialog box for the user """
    file_opt = options = {}
    options['defaultextension'] = ".npy"
    # options['filetypes'] = [('All files', '*.*'), ("Comma separate values", "*.csv")]
    options['filetypes'] = [("Numpy ", "*.npy")]
    logging.debug("saving data: 1")
    if _type == 'saveas':
        """ Ask the user what name to save the file as """
        logging.debug("saving data: 2")
        _filename = filedialog.asksaveasfilename(parent=parent, confirmoverwrite=False, **file_opt)
        return _filename

    elif _type == 'open':
        _filename = filedialog.askopenfilename(**file_opt)
        return _filename


print(23430/56, 23430-56*418)

if __name__ == '__main__':
    app = PerfectEarthAnalytics()
    app.title("Perfect Earth Analytics")
    app.geometry("950x650")
    app.mainloop()
