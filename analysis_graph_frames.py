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

FIGURE_SIZE = (8, 4)


class SavedDataGraph(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.figure_bed = plt.figure(figsize=FIGURE_SIZE)
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

    def plot_data(self, data_lines):
        print("============PLOTTING====")
        print(data_lines)
        index = 0
        for key, data in data_lines:
            index += 1
            if index == 2:
                # print(key, data)
                # print('=================')
                if key == "Temperature":
                    new_line, = self.axis.plot(data)

                    self.lines.append(new_line)
                else:
                    new_line, = self.axis.plot(data.difference, label="diff")
                    # print('diff: ', data.difference)
                    self.lines.append(new_line)
                    new_line, = self.axis.plot(data.lights_on, label="on")
                    # print('on: ', data.difference)
                    self.lines.append(new_line)
                    new_line, = self.axis.plot(data.lights_off, label="off")
                    # print('of: ', data.difference)
                    self.lines.append(new_line)
        # print("lines")
        # print(self.lines)
        # print(self.lines[0].get_data())
        self.axis.legend()
        self.axis.relim()
        self.axis.autoscale_view()
        # self.axis.set_xlim([0, 1000])
        # self.axis.set_ylim([0, 1000])
        self.canvas.draw()


    class DisplayOptions(tk.Frame):
        def __init__(self, data_lines):
            for key, data in data_lines:
                pass
