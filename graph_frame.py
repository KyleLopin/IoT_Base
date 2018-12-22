# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
from datetime import datetime
from datetime import timedelta
import tkinter as tk
from tkinter import ttk
# installed libraries
import matplotlib
import matplotlib.dates as mdates
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavToolbar
# local files
import sensor_node_data  # for type hinting

FIGURE_SIZE = (8, 4)


class DataGraphFrame(tk.Frame):
    def __init__(self, master, parent_notebook, data: sensor_node_data.SensorHubData, type):
        ttk.Frame.__init__(self, parent_notebook)
        self.graph = GraphFrame(self, data, type)  # make graph
        self.graph.pack(side='left', expand=True, fill=tk.BOTH)
        self.pack()

    def update(self):
        self.graph.update()


class GraphFrame(tk.Frame):
    def __init__(self, master_frame, data: sensor_node_data.SensorHubData, type):
        tk.Frame.__init__(self, master=master_frame)
        self.config(bg='white')
        self.plotted_lines = []  # type: list # to hold lines to update with new data
        self.data = data
        self.figure_bed = plt.figure(figsize=FIGURE_SIZE)
        self.axis = plt.subplot(111)
        x_format = mdates.DateFormatter("%H:%M")
        # self.figure_bed.autofmt_xdate()
        self.axis.xaxis.set_major_formatter(x_format)
        self.axis.format_coord = lambda x, y: ""  # remove the coordinates in the toolbox

        # set the limits of the frame
        start_time = datetime.now()

        self.axis.set_xlim([start_time - timedelta(minutes=5), start_time+timedelta(minutes=15)])
        if type == 'Temperature':
            self.axis.set_ylim([15, 100])

        self.axis.set_xlabel("Time", fontsize=12)
        self.axis.set_ylabel(type, fontsize=12)

        self.canvas = FigureCanvasTkAgg(self.figure_bed, master=self)
        self.canvas._tkcanvas.config(highlightthickness=0)
        toolbox_frame = tk.Frame(self)
        toolbox_frame.pack(side=tk.BOTTOM)
        self.toolbar = NavToolbar(self.canvas, toolbox_frame)
        self.toolbar.pack(side=tk.BOTTOM)

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='left', fill=tk.BOTH, expand=1)
        self.line1 = None
        self.line2 = None

    def update_proto(self):
        pass

    def update(self):
        print("update")
        if self.data.sensors[0].current_index == 0:
            return  # no data
        data_end0 = self.data.sensors[0].current_index - 1
        data_end1 = self.data.sensors[1].current_index - 1
        print('indexes: ', data_end0, data_end1)
        t_series1 = self.data.sensors[0].raw_color_data['time'][:data_end0]
        t_series2 = self.data.sensors[1].raw_color_data['time'][:data_end1]
        # t_series3 = self.data.sensors[2].raw_color_data['time']
        color_series1 = self.data.sensors[0].color_index[:data_end0]
        color_series2 = self.data.sensors[1].color_index[:data_end1]
        # color_series3 = self.data.sensors[2].color_index

        print('time1: ', t_series1)
        print('data1: ', color_series1)
        if self.line1:
            self.line1.set_ydata(color_series1)
            self.line1.set_xdata(t_series1)
        else:
            self.line1,  = self.axis.plot(t_series1, color_series1)

        if self.line2:
            self.line2.set_ydata(color_series1)
            self.line2.set_xdata(t_series1)
        else:
            self.line2,  = self.axis.plot(t_series1, color_series1)
        print(self.line1)
        self.axis.relim()
        self.axis.autoscale_view(True, True, True)
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = DataGraphFrame(root, None, None)
    app.mainloop()
