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
import numpy as np
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

        self.axis.set_xlim([start_time - timedelta(minutes=15), start_time + timedelta(minutes=5)])
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
        self.lines = [None, None, None]

    def update(self):
        # print('lines: ', self.lines)
        # print('num_data points = ', self.data.sensors[0].plot_index)
        for i, line in enumerate(self.lines):
            data_end = self.data.sensors[i].plot_index
            time_series = self.data.sensors[i].time_series[:data_end]
            color_series = self.data.sensors[i].color_index[:data_end]
            # print("color series: ", i, color_series)
            if self.lines[i]:
                # print('setind data: ', time_series)
                line.set_ydata(color_series)
                line.set_xdata(time_series)
                # print('set data: ', color_series)
                # print(time_series)
            else:
                new_line, = self.axis.plot(time_series, color_series)
                self.lines[i] = new_line  # TODO: does line = new_line work
        self.axis.relim()
        self.axis.autoscale_view(True, True, True)
        now = datetime.now()

        self.axis.set_xlim([now - timedelta(minutes=15), now + timedelta(minutes=5)])
        # self.axis.set_ylim([np.amin(color_series), now + timedelta(minutes=5)])
        if color_series.any():
            print('y min:', np.amin(color_series))
            print('y max:', np.amax(color_series))
        self.canvas.draw()

    def update_old(self):
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


def wavelength_to_rgb(wavelength, max_value=255, gamma=0.8):
    """  modified from https://www.noah.org/wiki/Wavelength_to_RGB_in_Python
    This converts a given wavelength of light to an
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    """
    MAX_UV = 380
    MAX_IR = 940
    wavelength = float(wavelength)
    if MAX_UV <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - MAX_UV) / (440 - MAX_UV)
        red = ((-(wavelength - 440) / (440 - MAX_UV)) * attenuation) ** gamma
        green = 0.0
        blue = (1.0 * attenuation) ** gamma
    elif wavelength <= 490:  # if less than 440 the previous if statement will be called
        red = 0.0
        green = ((wavelength - 440) / (490 - 440)) ** gamma
        blue = 1.0
    elif wavelength <= 510:
        red = 0.0
        green = 1.0
        blue = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength <= 580:
        red = ((wavelength - 510) / (580 - 510)) ** gamma
        green = 1.0
        blue = 0.0
    elif wavelength <= 645:
        red = 1.0
        green = (-(wavelength - 645) / (645 - 580)) ** gamma
        blue = 0.0
    elif wavelength <= MAX_IR:
        attenuation = 0.3 + 0.7 * (MAX_IR - wavelength) / (MAX_IR - 645)
        red = (1.0 * attenuation) ** gamma
        green = 0.0
        blue = 0.0
    else:
        red = 0.0
        green = 0.0
        blue = 0.0
    red *= max_value
    green *= max_value
    blue *= max_value
    return (red, green, blue)

if __name__ == '__main__':
    root = tk.Tk()
    app = DataGraphFrame(root, None, None)
    app.mainloop()
