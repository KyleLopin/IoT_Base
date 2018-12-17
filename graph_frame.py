# Copyright (c) 2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
from tkinter import ttk
# local files


class DataGraphFrame(tk.Frame):
    def __init__(self, master, parent_notebook):
        ttk.Frame.__init__(self, parent_notebook)
        self.graph = self.make_graph_area(master, graph_properties)  # make graph
        self.graph.pack(side='left', expand=True, fill=tk.BOTH)

    def make_graph_area(self, master, graph_props):
        """
        
        """
        # current_lim = 1.2 * 1000. / master.device_params.adc_tia.tia_resistor
        current_lim = master.device_params.adc_tia.current_lims
        low_voltage = self.settings.low_voltage
        high_voltage = self.settings.high_voltage
        graph = tkinter_pyplot.PyplotEmbed(master.frames[0],
                                           # frame to put the toolbar in NOTE: hack, fix this
                                           graph_props.cv_plot,
                                           self,
                                           current_lim, low_voltage, high_voltage)

        return graph
