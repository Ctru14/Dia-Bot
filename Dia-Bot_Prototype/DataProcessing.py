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

from DataCollection import DataCollection
import Threads

class DataProcessing(DataCollection):
    
    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue):
        super().__init__(name, units, samplingRate, globalStartTime, dataQueue)
        #self.dataCollection = dataCollection
        #self.dataMutex = threading.Lock()
        #self.dataMutex = multiprocessing.Lock()
        #self.globalUImutex = globalUImutex
        #self.dataQueue = dataQueue
        #self.t = []
        #self.data = []
        if isPlotted:
            self.fig = Figure(figsize=(3,2.5), dpi=80)
            self.fig.patch.set_facecolor("#DBDBDB")
            self.plot1 = self.fig.add_subplot(111)
            self.plot1.plot(self.t, self.data)
            self.plot1.set_ylabel(self.units)
               
        
    # Create and add the Tkinter pane for data visualization - may be overwritten for those without graphs
    def tkAddDataPane(self, tkTop):
        # Top label
        tk.Label(tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add random graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=tkTop)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)

    def createVisual(self):
        # Find start and end indices for graphing
        start = 0
        end = len(self.t)
        if end == 0:
            print(f"Error in updateVisual ({self.name}) - data length is zero!")
            return
        # Graph the last 5 seconds
        start = int(max(0, end-2*self.samplingRate))
        self.plot1.cla() # Find way to update graphs without it taking too long!!
        # Update plot
        #self.dataMutex.acquire()
        print(f"Update {self.name} graph: indices ({start}..{end})  Latest: ({self.t[-1]}, {self.data[-1]})")
        self.plot1.plot(self.t[start:end], self.data[start:end])
        #self.dataMutex.release()
        #self.dataMutex.release()
    
    def updateVisual(self):
        print(f"Update {self.name} visual")
        self.getAndAddData()
        self.createVisual()
        # Update canvas on UI
        #self.globalUImutex.acquire()
        self.canvas.draw()
        print(f"Graph done: {self.name} (total time = {(time.time_ns()-self.globalStartTime)/1_000_000_000} s)\n")
        #self.globalUImutex.release()
        
    #def readNewData(self):
    #    while not self.dataQueue.empty():
    #        t, data = self.dataQueue.get()
    #        self.t.append(t)
    #        self.data.append(data)
    #        #print(f"New data! {t}, {data}")
               

    # ----- Data Processing functions -----
    def peakMagnitude(self, timeLo, timeHi):
        print(f"Calculating peak oscillation magnitude between {timeLo}s and {timeHi}s")

    def averageMagnitude(self, timeLo, timeHi):
        print(f"Calculating average oscillation magnitude between {timeLo}s and {timeHi}s")

    def peakValue(self, timeLo, timeHi):
        print(f"Finding peak magnitude of the data between {timeLo}s and {timeHi}s")

    def frequency(self, timeLo, timeHi):
        print(f"Finding frequency between {timeLo}s and {timeHi}s")




class SoundLevelProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue)



class VibrationProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue)



class PositionProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue)



class TemperatureProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue):
        super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue)
        self.viewFarenheit = False
        self.currentTempCelsius = 0
        self.currentTempFarenheit = 0
        self.tempDisplayText = StringVar()
        self.tempDisplayText.set(self.getDisplayText())
        self.tempViewButtonText = StringVar()
        self.tempViewButtonText.set("View Farenheit")


    def getDisplayText(self):
        if self.viewFarenheit:
            return f"{self.currentTempFarenheit} °F"
        else:
            return f"{self.currentTempCelsius} °C"

    # Overwrite data visuals method: no graph needed
    def tkAddDataPane(self, tkTop):
        # Top label
        tk.Label(tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add temperature text and display button
        self.tempLabel = tk.Label(tkTop, textvariable=self.tempDisplayText, font="none 14")
        self.tempLabel.grid(row=3, column=1, columnspan=5)
        self.switchTempViewButton = tk.Button(tkTop, textvariable=self.tempViewButtonText, command=self.switchTempView)
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
        self.readNewData()
        print(f"Update temperature visual: {self.getDisplayText()}")
        self.tempDisplayText.set(self.getDisplayText())
        #self.tempViewButtonText.set("View Farenheit")

    def readNewData(self):
        while not self.dataQueue.empty():
            t, dataC, dataF = self.dataQueue.get()
            self.t.append(t)
            self.data.append(dataC)
            self.currentTempCelsius = dataC
            self.currentTempFarenheit = dataF
            print(f"New temperature data! {t}, C={dataC}, F={dataF}")