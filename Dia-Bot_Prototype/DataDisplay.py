import sys
import os
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import multiprocessing
import math
import enum
from random import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import matplotlib.animation as animation
from collections import deque

import matplotlib.dates as mdates

import DataProcessing


import matplotlib.ticker as ticker



# Credit for this solution for millisecond time display goes to StackOverflow user "hemmelig"
# https://stackoverflow.com/questions/11107748/showing-milliseconds-in-matplotlib
class PrecisionDateFormatter(ticker.Formatter):
    """
    Extend the `matplotlib.ticker.Formatter` class to allow for millisecond
    precision when formatting a tick (in days since the epoch) with a
    `~datetime.datetime.strftime` format string.

    """

    def __init__(self, fmt, precision=2, tz=None):
        """
        Parameters
        ----------
        fmt : str
            `~datetime.datetime.strftime` format string.
        """
        from matplotlib.dates import num2date
        if tz is None:
            from matplotlib.dates import _get_rc_timezone
            tz = _get_rc_timezone()
        self.num2date = num2date
        self.fmt = fmt
        self.tz = tz
        self.precision = precision

    def __call__(self, x, pos=0):
        #if x == 0:
        #    raise ValueError("DateFormatter found a value of x=0, which is "
        #                     "an illegal date; this usually occurs because "
        #                     "you have not informed the axis that it is "
        #                     "plotting dates, e.g., with ax.xaxis_date()")
        #
        dt = self.num2date(x, self.tz)
        ms = dt.strftime("%f")[:self.precision]

        return dt.strftime(self.fmt).format(ms=ms)

    def set_tzinfo(self, tz):
        self.tz = tz



# Owned by main TK process to display the data
class DataDisplay:

    def __init__(self, fields, tkTop, visualQueue):
        self.name = fields.name
        self.units = fields.units
        self.tkTop = tkTop
        self.visualQueue = visualQueue
        # Finf max length of data to display: 3 seconds worth or 250, whichever is smaller
        self.displayDataLen = int((fields.samplingRate * 3)/10)*10
        self.displayDataLen = min(self.displayDataLen, 250)
        self.t = deque([], maxlen=self.displayDataLen)
        self.data = deque([], maxlen=self.displayDataLen)

    # Create and add the Tkinter pane for data visualization - may be overwritten for those without graphs
    def tkAddDataPane(self, *args):
        # Top label
        tk.Label(self.tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add random graph
        self.fig = Figure(figsize=(3,2.5), dpi=80)
        self.fig.patch.set_facecolor("#DBDBDB")
        self.plot1 = self.fig.add_subplot(111)
        self.plot1.set_ylabel(self.units)
        self.line, = self.plot1.plot([], [], lw=2)
        self.plot1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(2))
        self.plot1.xaxis.set_major_formatter(PrecisionDateFormatter("%H:%M:%S.{ms}"))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tkTop)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)
        self.ani = animation.FuncAnimation(
            self.fig,
            self.appendNewData,
            interval=2000, # Time (ms) between graph updates
            repeat=True)
        self.ani._start()


    # Called by UI thread - after proper changes, this will receive and post a new plot from the visual queue
    def updateVisual(self, dataViewVars):
        print(f"UPDATE VISUAL: {self.name} - Note, this does nothing!")

    def appendNewData(self, *args):
        #print(f"Trying to append new {self.name} data...")
        #t0 = time.time()
        while not self.visualQueue.empty():
            t, data = self.visualQueue.get()
            self.t.append(t)
            self.data.append(data)
        if len(self.t) > 0:
            #print(f"APPENDING new data to the {self.name} animation! ({self.t[0]}..{self.t[len(self.t)-1]})")
            self.line.set_data(self.t, self.data)
            self.plot1.set_ylim(min(self.data), max(self.data))
            self.plot1.set_xlim(self.t[0], self.t[-1])
            #t1 = time.time()
            #print(f"Appended new data to {self.name} graph! Took {1000*(t1-t0)}ms")
        return self.line,

 # Create class for Temperature text/button display
class TemperatureDisplay(DataDisplay):

    def __init__(self, fields, tkTop, visualQueue):
        super().__init__(fields, tkTop, visualQueue)
        self.viewFarenheit = False
        self.currentTempCelsius = 0
        self.currentTempFarenheit = 0
        self.tempDisplayText = StringVar()
        self.tempDisplayText.set(self.getDisplayText())
        self.tempViewButtonText = StringVar()
        self.tempViewButtonText.set("View Farenheit")

    def getDisplayText(self):
        if self.viewFarenheit:
            tempF = "{:.2f}".format(self.currentTempFarenheit)
            return f"{tempF} °F"
        else:
            tempC = "{:.2f}".format(self.currentTempCelsius)
            return f"{tempC} °C"
        
    def switchTempView(self):
        print(f"Switching temp view! Temp = {self.tempDisplayText.get()}, Button = {self.tempViewButtonText.get()}")
        if self.viewFarenheit:
            # Currently Farenheit --> Switch to Celsius
            self.viewFarenheit = False
            self.tempDisplayText.set(self.getDisplayText())
            self.tempViewButtonText.set("View Farenheit")
        else:
            # Currently Celsius --> Switch to Farenheit
            self.viewFarenheit = True
            self.tempDisplayText.set(self.getDisplayText())
            self.tempViewButtonText.set("View Celsius")


    # Called by UI thread to update temperature printout
    def updateVisual(self):
        DataProcessing.TemperatureProcessing.readNewData(self)
        #print(f"Update TEMPERATURE visual: {self.getDisplayText()}")
        self.tempDisplayText.set(self.getDisplayText())


    # Overwrite data visuals method: no graph needed
    def tkAddDataPane(self):
        # Top label
        self.topLabel = tk.Label(self.tkTop, text=self.name, font="none 12 bold")
        self.topLabel.grid(row=1, column=1, columnspan=5)
        # Add temperature text and display button
        self.tempLabel = tk.Label(self.tkTop, textvariable=self.tempDisplayText, font="none 14")
        self.tempLabel.grid(row=3, column=1, columnspan=5)
        self.switchTempViewButton = tk.Button(self.tkTop, textvariable=self.tempViewButtonText, command=self.switchTempView)
        self.switchTempViewButton.grid(row=4, column=1, columnspan=5)
