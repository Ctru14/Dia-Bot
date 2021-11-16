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
    
    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(name, units, samplingRate, globalStartTime, dataQueue)
        self.visualQueue = visualQueue
        self.processingQueue = processingQueue
        #self.dataMutex = threading.Lock()
        #self.dataMutex = multiprocessing.Lock()
        #if isPlotted:
        #    self.fig = Figure(figsize=(3,2.5), dpi=80)
        #    self.fig.patch.set_facecolor("#DBDBDB")
        #    self.plot1 = self.fig.add_subplot(111)
        #    self.plot1.plot(self.t, self.data)
        #    self.plot1.set_ylabel(self.units)
               
        
    # Create and add the Tkinter pane for data visualization - may be overwritten for those without graphs
    def tkAddDataPane(name, tkTop, *args):
        units = args[0]
        # Top label
        tk.Label(tkTop, text=name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add random graph
        fig = Figure(figsize=(3,2.5), dpi=80)
        fig.patch.set_facecolor("#DBDBDB")
        plot1 = fig.add_subplot(111)
        plot1.set_ylabel(units)
        canvas = FigureCanvasTkAgg(fig, master=tkTop)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)
        return (fig, plot1, canvas)

    def createVisual(self, plot1):
        # Find start and end indices for graphing
        start = 0
        end = len(self.t)
        if end == 0:
            print(f"Error in updateVisual ({self.name}) - data length is zero!")
            return
        # Graph the last 5 seconds
        start = int(max(0, end-2*self.samplingRate))
        plot1.cla() # Find way to update graphs without it taking too long!!
        # Update plot
        #self.dataMutex.acquire()
        print(f"Update {self.name} graph: indices ({start}..{end})  Latest: ({self.t[-1]}, {self.data[-1]})")
        plot1.plot(self.t[start:end], self.data[start:end])
        #self.dataMutex.release()
        #self.dataMutex.release()
    
    # Called by UI thread - after proper changes, this will receive and post a new plot from the visual queue
    def updateVisual(self, dataViewVars):
        print(f"Update {self.name} visual")
        fig = dataViewVars[0]
        plot1 = dataViewVars[1]
        canvas = dataViewVars[2]
        self.getAndAddData()
        self.createVisual(plot1)
        # Update canvas on UI
        #self.globalUImutex.acquire()
        canvas.draw()
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

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue)



class VibrationProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue)



class PositionProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue)



class TemperatureProcessing(DataProcessing):

    def __init__(self, name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(name, units, samplingRate, globalStartTime, isPlotted, dataQueue, visualQueue, processingQueue)


    # Overwrite data visuals method: no graph needed
    def tkAddDataPane(name, tkTop, tempDisplayText, tempViewButtonText, switchTempViewCommand):
        # Top label
        tk.Label(tkTop, text=name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add temperature text and display button
        tempLabel = tk.Label(tkTop, textvariable=tempDisplayText, font="none 14")
        tempLabel.grid(row=3, column=1, columnspan=5)
        switchTempViewButton = tk.Button(tkTop, textvariable=tempViewButtonText, command=switchTempViewCommand)
        switchTempViewButton.grid(row=4, column=1, columnspan=5)
        return (tempLabel, switchTempViewButton)

    # Called by UI thread to update temperature printout
    def updateVisual(tempView):
        TemperatureProcessing.readNewData(tempView)
        print(f"Update TEMPERATURE visual: {tempView.getDisplayText()}")
        tempView.tempDisplayText.set(tempView.getDisplayText())

    def readNewData(tempView):
        while not tempView.visualQueue.empty():
            t, dataC = tempView.visualQueue.get()
            tempView.currentTempCelsius = dataC
            tempView.currentTempFarenheit = dataC * 9 / 5 + 32
            print(f"New temperature data! {t}, C={tempView.currentTempCelsius}, F={tempView.currentTempFarenheit}")