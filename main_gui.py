# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Graphical User Interface to read data from the Sensor Hub through the USB.  The sensor hub will receive data
from the different sensor nodes through the wifi and transmit it to the computer for this program.
"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
# local files
import comm_uart as comm
import graph_frame
import sensor_node_data

DATA_LENGTH = 55
NUMBER_OF_SENSOR = 3


class PerfectEarthGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # make data class for the data
        self.data = sensor_node_data.SensorHubData(NUMBER_OF_SENSOR)

        # make ttk tabs
        self.notebook = ttk.Notebook(self)
        self.color_frame = graph_frame.DataGraphFrame(self, self.notebook, self.data, 'Color Scale')
        self.notebook.add(self.color_frame, text="Color Summary")

        self.temp_frame = graph_frame.DataGraphFrame(self, self.notebook, self.data, 'Temperature')
        self.notebook.add(self.temp_frame, text="Temperature")
        # all tabs in so pack the notebook on the main frame
        self.notebook.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # add graphs to the data class so it can call the update data directly
        self.data.add_graphs(self.color_frame, self.temp_frame)

        # connect the device through the communication module
        self.device = comm.PyComComm(self.data, DATA_LENGTH)
        # print('device: ', self.device.device)
        if not self.device.device:  # TODO: abstract this better
            messagebox.showerror("Missing Sensor Hub", message="Please connect the sensor hub to a USB port")

        # make run button
        self.running = False  # type: bool
        self.bottom_frame = tk.Frame(self, relief=tk.GROOVE, bd=4, bg='wheat4')
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.run_button = tk.Button(self.bottom_frame, text="Run",
                                    command=self.run_button_handler,
                                    width=20, bd=5, relief=tk.RAISED)
        self.run_button.pack(side=tk.BOTTOM, pady=5)
        self.graph_updater = self.after(3000, self.update_graphs)

    def run_button_handler(self):
        if self.running:
            # system in running to send stop message and update button
            print("TODO: send stop message")
            if not self.device.device:  # TODO: abstract this better
                messagebox.showerror("Missing Sensor Hub", message="Please connect the sensor hub to a USB port")
            else:
                self.device.stop()
            self.run_button.config(text="Run", relief=tk.RAISED)
            self.running = False

        else:
            if not self.device.device:  # TODO: abstract this better
                messagebox.showerror("Missing Sensor Hub", message="Please connect the sensor hub to a USB port")
            else:
                # self.device = comm.PyComComm(self.data, DATA_LENGTH)
                # self.device.close()
                self.device.start()
            self.run_button.config(text="Stop", relief=tk.SUNKEN)
            self.running = True

    def update_graphs(self):
        self.graph_updater = self.after(3000, self.update_graphs)
        print('==============UPDATE GRAPH ================')
        self.color_frame.update()

    def on_closing(self):
        print("closing")
        self.after_cancel(self.graph_updater)
        self.device.close()
        self.destroy()


if __name__ == '__main__':


    app = PerfectEarthGUI()
    app.title("Perfect Earth Analytics")
    app.geometry("900x650")
    app.mainloop()
