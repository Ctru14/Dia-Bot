import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import multiprocessing
import math
import numpy as np
from random import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from DataCollection import DataCollection
from Alerts import AlertDataType
from Alerts import AlertMetric
import Threads

class DataProcessing(DataCollection):
    
    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(name, units, samplingRate, startTime, dataQueue, alertDataType)
        self.alertDataType = alertDataType
        self.visualQueue = visualQueue
        self.processingQueue = processingQueue
        #self.dataMutex = threading.Lock()
        #self.dataMutex = multiprocessing.Lock()
        self.lastIdx = 0
               

    # ----- Data Processing functions -----
    def average(self, idxLo, idxHi):
        avg = np.mean(self.data[idxLo:idxHi])
        #print(f"Calculating average between {idxLo} and {idxHi}: {avg}")
        return avg

    def maximum(self, idxLo, idxHi):
        max = np.max(self.data[idxLo:idxHi])
        #print(f"Calculating maximum between {idxLo} and {idxHi}: {max}")
        return max

    def minimum(self, idxLo, idxHi):
        min = np.min(self.data[idxLo:idxHi])
        #print(f"Finding minimum between {idxLo} and {idxHi}: {min}")
        return min

    def frequency(self, idxLo, idxHi):
        fft = np.fft.fft(self.data[idxLo:idxHi])
        #print(f"Finding frequency between {idxLo} and {idxHi}: {fft}")
        return fft

    def magnitude(self, idxLo, idxHi):
        fft = np.fft.fft(self.data[idxLo:idxHi])
        #print(f"Finding magnitude between {idxLo} and {idxHi}: {fft}")
        return fft[0]

   
    def mainProcessing(self, *args):
        # Calculate all processing values and put them into the queue
        idxHi = len(self.t)-1
        if idxHi > 0:
            t = self.t[idxHi]
            idxLo = max(0, int(idxHi - (10 * self.samplingRate)))
            avg = self.average(idxLo, idxHi)
            maximum = self.maximum(idxLo, idxHi)
            minimum = self.minimum(idxLo, idxHi)
            freq = self.frequency(idxLo, idxHi)
            mag = self.magnitude(idxLo, idxHi)
            #print(f"Sending {self.name}[{idxLo}:{idxHi}] update to processing queue: (Avg={avg}, Max={maximum}, Min={minimum}, Freq={freq}, Mag={mag})")
            self.processingQueue.put((self.alertDataType, avg, maximum, minimum, freq, mag, t, (idxLo, idxHi)))
            while self.lastIdx <= idxHi:
                self.visualQueue.put((self.t[self.lastIdx], self.data[self.lastIdx]))
                self.lastIdx += 1

    # Visual Processing
   
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

    #def visualProcessing(self, *args):
    #    # TESTING CODE: Make plot to put in visual queue
    #    idxHi = len(self.t)
    #    #if idxHi > 0:
    #    #    t = self.t[idxHi-1]
    #    #    idxLo = max(0, int(idxHi - (10 * self.samplingRate)))
    #    #    fig = Figure(figsize = (3,3), dpi = 100)
    #    #    a = fig.add_subplot(111)
    #    #    a.plot(self.t[idxLo:idxHi], self.data[idxLo:idxHi])
    #    #    a.set_title("Test Title")
    #    #    print(f"Adding {self.name} figure to visual queue (indices {idxLo}..{idxHi})...")
    #    #    #fig.show()
    #    #    self.visualQueue.put(fig)
    




class SoundLevelProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)



class VibrationProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)



class PositionProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)



class TemperatureProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)

    def readNewData(tempView):
        while not tempView.visualQueue.empty():
            t, dataC = tempView.visualQueue.get()
            tempView.currentTempCelsius = dataC
            tempView.currentTempFarenheit = dataC * 9 / 5 + 32
            #print(f"New temperature data! {t}, C={tempView.currentTempCelsius}, F={tempView.currentTempFarenheit}")

    #def visualProcessing(self, *args):
    #    # Temperature is simple: read latest temperature and send it to visual queue
    #    if len(self.t) > 0:
    #        print(f"Adding temperature data to visual queue: {(self.t[-1], self.data[-1])}")
    #        self.visualQueue.put((self.t[-1], self.data[-1]))
