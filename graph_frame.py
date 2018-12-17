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


class DataGraphFrame(tk.Frame):
    def __init__(self, master, parent_notebook, data, type):
        ttk.Frame.__init__(self, parent_notebook)
        self.graph = GraphFrame(self, data, type)  # make graph
        self.graph.pack(side='left', expand=True, fill=tk.BOTH)
        self.pack()


class GraphFrame(tk.Frame):
    def __init__(self, master_frame, data, type):
        tk.Frame.__init__(self, master=master_frame)
        self.plotted_lines = []  # type: list # to hold lines to update with new data
        self.data = data
        self.figure_bed = plt.figure(figsize=(8, 5))
        self.axis = plt.subplot(111)
        self.figure_bed.autofmt_xdate()
        self.axis.format_coord = lambda x, y: ""  # remove the coordinates in the toolbox

        # set the limits of the frame
        start_time = datetime.now()

        self.axis.set_xlim([start_time, start_time+timedelta(minutes=30)])
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



if __name__ == '__main__':
    root = tk.Tk()
    app = DataGraphFrame(root, None, None)
    app.mainloop()
