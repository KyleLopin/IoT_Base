# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
from tkinter import ttk
# local files


class PerfectEarthGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        # make ttk tabs
        self.notebook = ttk.Notebook(self)



        # for i, possible_sensor in enumerate(["AS7262", "AS7263"]):
        #     for sensor in self.device.sensors:
        #         if sensor.sensor_type == possible_sensor:
        #             new_sensor_frame = spectro_frame.ColorSpectorFrame(self, self.notebook, sensor, self.device)
        #             self.notebook.add(new_sensor_frame, text=sensor.sensor_type)
        # self.notebook.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

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
    app.geometry("500x450")
    app.mainloop()
