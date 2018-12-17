# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
from tkinter import ttk
# local files
import graph_frame
import sensor_node_data


class PerfectEarthGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        # make data class for the data
        data = sensor_node_data.SensorHubData()

        # make ttk tabs
        self.notebook = ttk.Notebook(self)
        color_frame = graph_frame.DataGraphFrame(self, self.notebook, data, 'Color Scale')
        self.notebook.add(color_frame, text="Color qualities")

        temp_frame = graph_frame.DataGraphFrame(self, self.notebook, data, 'Temperature')
        self.notebook.add(temp_frame, text="Temperature")
        # all tabs in so pack the notebook on the main frame
        self.notebook.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # make run button
        self.running = False  # type: bool
        self.run_button = tk.Button(self, text="Run", command=self.run_button_handler)
        self.run_button.pack(side=tk.BOTTOM)

    def run_button_handler(self):
        if self.running:
            # system in running to send stop message and update button
            print("TODO: send stop message")
            self.run_button.config(text="Run")
            self.running = False
        else:
            print("TODO: send start message")
            self.run_button.config(text="Stop")
            self.running = True


if __name__ == '__main__':
    app = PerfectEarthGUI()
    app.title("Perfect Earth Analytics")
    app.geometry("900x500")
    app.mainloop()
