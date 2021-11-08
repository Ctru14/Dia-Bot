import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import multiprocessing
import math
from random import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class DataCollection:
    
    def __init__(self, name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime):
        self.name = name
        self.units = units
        self.tkTop = tkTop
        self.data = []
        self.samplingRate = samplingRate
        self.samplingTime = 1/samplingRate
        self.dataMutex = threading.Lock()
        #self.dataMutex = multiprocessing.Lock()
        self.globalUImutex = globalUImutex
        self.globalStartTime = globalStartTime
        self.t = []
        self.data = []
        if isPlotted:
            self.fig = Figure(figsize=(3,2.5), dpi=80)
            self.fig.patch.set_facecolor("#DBDBDB")
            self.plot1 = self.fig.add_subplot(111)
            self.plot1.plot(self.t, self.data)
            self.plot1.set_ylabel(self.units)
        
    # Create and add the Tkinter pane for data visualization - may be overwritten for those without graphs
    def tkAddDataPane(self):
        # Top label
        tk.Label(self.tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add random graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tkTop)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)
        
        
    def addData(self, t, data):
        self.dataMutex.acquire()
        self.t.append(t)  # self.t[-1]+self.samplingTime)
        self.data.append(data)
        self.dataMutex.release()

    def readAndAddData(self):
        t = (time.time_ns()-self.globalStartTime)/1_000_000_000
        data = self.readData()
        self.addData(t, data)
        
        
    def updateVisual(self):
        print(f"Update {self.name} visual")

        # Find start and end indices for graphing
        start = 0
        end = len(self.t)
        # Graph the last 5 seconds
        start = int(max(0, end-2*self.samplingRate))
        self.plot1.cla() # Find way to update graphs without it taking too long!!
        print(f"Update {self.name} graph: indices ({start}..{end})  Latest: ({self.t[-1]}, {self.data[-1]})")
        # Update plot
        #self.dataMutex.acquire()
        self.plot1.plot(self.t[start:end], self.data[start:end])
        #self.dataMutex.release()
        # Update canvas on UI
        #self.globalUImutex.acquire()
        self.canvas.draw()
        print(f"Graph done: {self.name} (total time = {(time.time_ns()-self.globalStartTime)/1_000_000_000} s)\n")
        #self.globalUImutex.release()
        

    # ----- Data Processing functions -----
    def peakMagnitude(self, timeLo, timeHi):
        print(f"Calculating peak oscillation magnitude between {timeLo}s and {timeHi}s")

    def averageMagnitude(self, timeLo, timeHi):
        print(f"Calculating average oscillation magnitude between {timeLo}s and {timeHi}s")

    def peakValue(self, timeLo, timeHi):
        print(f"Finding peak magnitude of the data between {timeLo}s and {timeHi}s")

    def frequency(self, timeLo, timeHi):
        print(f"Finding frequency between {timeLo}s and {timeHi}s")



class SoundLevel(DataCollection):

    def __init__(self, name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime):
        return super().__init__(name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading sound level! - " + str(num))
        return num



class Vibration(DataCollection):

    def __init__(self, name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime):
        return super().__init__(name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading vibration! - " + str(num))
        return num
    
    

class Position(DataCollection):

    def __init__(self, name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime):
        return super().__init__(name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading position! - " + str(num))
        return num



class Temperature(DataCollection):

    def __init__(self, name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime):
        self.currentTempCelsius = 0
        self.currentTempFarenheit = 32
        self.viewFarenheit = False
        self.tempDisplayText = StringVar()
        self.tempDisplayText.set(self.getDisplayText())
        self.tempViewButtonText = StringVar()
        self.tempViewButtonText.set("View Farenheit")
        return super().__init__(name, units, tkTop, globalUImutex, isPlotted, samplingRate, globalStartTime)

    def readData(self):
        num = randint(-10, 10)
        self.currentTempCelsius = num
        self.currentTempFarenheit = num * 9 / 5 + 32
        #print("Reading temperature! - " + str(num))
        return num

    def getDisplayText(self):
        if self.viewFarenheit:
            return f"{self.currentTempFarenheit} °F"
        else:
            return f"{self.currentTempCelsius} °C"

    # Overwrite data visuals method: no graph needed
    def tkAddDataPane(self):
        # Top label
        tk.Label(self.tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add temperature text and display button
        self.tempLabel = tk.Label(self.tkTop, textvariable=self.tempDisplayText, font="none 14")
        self.tempLabel.grid(row=3, column=1, columnspan=5)
        self.switchTempViewButton = tk.Button(self.tkTop, textvariable=self.tempViewButtonText, command=self.switchTempView)
        self.switchTempViewButton.grid(row=4, column=1, columnspan=5)

    def switchTempView(self):
        print(f"Switching view! Temp = {self.tempDisplayText.get()}, Button = {self.tempViewButtonText.get()}")
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

    def updateVisual(self):
        self.tempDisplayText.set(self.getDisplayText())
        #self.tempViewButtonText.set("View Farenheit")
