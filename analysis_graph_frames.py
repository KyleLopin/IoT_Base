# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Frames with embedded graphs to display the
"""

# standard libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
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


__author__ = "Kyle Vitatus Lopin"

FIGURE_SIZE = (5, 4)
MAX_UV = 380
MAX_IR = 940


class SavedDataGraph(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.figure_bed = plt.figure()
        self.figure_bed.add_axes([0.1, 0.1, 0.6, 0.6])
        self.axis = plt.subplot(111)


        self.canvas = FigureCanvasTkAgg(self.figure_bed, master=self)
        self.canvas._tkcanvas.config(highlightthickness=0)
        toolbox_frame = tk.Frame(self)
        toolbox_frame.pack(side=tk.BOTTOM)
        self.toolbar = NavToolbar(self.canvas, toolbox_frame)
        self.axis.format_coord = lambda x, y: ""
        self.toolbar.pack(side=tk.BOTTOM)

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='left', fill=tk.BOTH, expand=1)

        self.lines = []

    def add_data(self, data: sensor_node_data.SavedSensorData):
        # TODO: THIS IS DEPRECATED
        print("making graph")
        for data_line in data:
            print(data_line)
            self.axis.plot(data_line)

    def plot_index_lines(self, data):  #TODO: work for multiple nodes
        new_line, = self.axis.plot(data)
        self.axis.relim()
        self.axis.autoscale_view()
        # self.axis.set_xlim([0, 1000])
        # self.axis.set_ylim([0, 1000])
        self.canvas.draw()
        # self.DisplayOptions(self, data_lines).pack(side='left')

    def plot_data(self, data_lines):
        print("============PLOTTING====")
        print(data_lines)
        if not self.lines:
            make_new_lines = True
        index = 0
        for key, data in data_lines:
            print('k, d', key, data)
            index += 1
            # print(key, data)
            # print('=================')
            if key == "Temperature":
                if make_new_lines:
                    new_line, = self.axis.plot(data)

                    self.lines.append(new_line)
                else:
                    self.lines[index].set_ydata(data)
            else:
                if make_new_lines:
                    print('nm: ', int(key.split()[0]))
                    r, g, b = wavelength_to_rgb(key.split()[0], max_value=1.0)

                    new_line, = self.axis.plot(data.difference, label=key, color=(r, g, b))
                    # print('diff: ', data.difference)
                    self.lines.append(new_line)
                    # new_line, = self.axis.plot(data.lights_on, label="on")
                    # print('on: ', data.difference)
                    # self.lines.append(new_line)
                    # new_line, = self.axis.plot(data.lights_off, label="off")
                    # print('of: ', data.difference)
                    # self.lines.append(new_line)
                else:
                    self.lines[index].set_ydata(data)
        print("lines")
        print(self.lines)
        print(self.lines[0].get_data())
        print('bbox: ', self.axis.bbox)
        # self.axis.bbox(x1=5)
        # self.axis.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
        #                  mode="expand")
        # plt.tight_layout()
        self.axis.relim()
        self.axis.autoscale_view()
        # self.axis.set_xlim([0, 1000])
        # self.axis.set_ylim([0, 1000])
        self.canvas.draw()
        self.DisplayOptions(self, data_lines).pack(side='left')

    class DisplayOptions(tk.Frame):
        def __init__(self, parent, data_lines):
            tk.Frame.__init__(self, master=parent)
            print(data_lines)
            for key, data in data_lines:
                if key == "Temperature":
                    continue
                print('making legend: ', key, data)
                r, g, b = wavelength_to_rgb(key.split()[0], max_value=255)
                color_string = hex(int(r))+hex(int(g))[-2:]+hex(int(b))[-2:]
                print('r, g, b: ', r, g, b, color_string, hex(int(r)), hex(int(g)), hex(int(b)))
                tk.Button(self, text=key).pack(side="top", padx=5, pady=2)

def wavelength_to_rgb(wavelength, max_value=255, gamma=0.8):
    """  modified from https://www.noah.org/wiki/Wavelength_to_RGB_in_Python
    This converts a given wavelength of light to an
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    """
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
    print('rgb:', red, green, blue)
    return red, green, blue
