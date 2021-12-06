import sys
import os
import csv
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
from DataCollection import VibrationCollection
from Alerts import AlertDataType
from Alerts import AlertMetric
from Positioning import Point3d
import Positioning
import Threads



class DataProcessing(DataCollection):
    
    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(name, units, samplingRate, startTime, dataQueue, alertDataType)
        self.alertDataType = alertDataType
        self.visualQueue = visualQueue
        self.processingQueue = processingQueue
        self.dataMutex = threading.Lock()
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

    def addDataToVisualQueue(self, idxHi):
        while self.lastIdx <= idxHi:
            self.visualQueue.put((self.t[self.lastIdx], self.data[self.lastIdx]))
            self.lastIdx += 1

   
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
            self.processingQueue.put((self.alertDataType, avg, maximum, minimum, freq, mag, t, (idxLo, idxHi)))
            self.addDataToVisualQueue(idxHi)
        return idxHi

class SoundLevelProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)



class VibrationProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue, positionQueue):
        super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)
        self.positionQueue = positionQueue
        self.dataRaw = [] # Point3d
        self.lastPosIdx = 0
        self.curVel = Point3d(0, 0, 0, 0)
        self.curPos = Point3d(0, 0, 0, 0)

    # DataCollection method! Overridden  instead due to inheritance complications
    # Used in processing process - appends new data point to the data array
    def addData(self, t, data):
        #self.dataMutex.acquire()
        self.t.append(t)  # self.t[-1]+self.samplingTime)
        newPoint = Point3d(t.timestamp(), data[0], data[1], data[2])
        self.dataRaw.append(newPoint)
        self.data.append(newPoint.mag())
        #self.dataMutex.release()

    # Calculate all processing values and put them into the queue
    # Processing done on magnitude!
    def mainProcessing(self, *args):
        idxHi = super().mainProcessing()
        # Integrate the new vibration acceleration data
        if idxHi > 0:
            self.calculatePosition(idxHi)

    def calculatePosition(self, idxHi):
        # Track position up to the last index
        if self.lastPosIdx == 0 and len(self.dataRaw) > 0:
            self.curVel.t = self.dataRaw[0].t
            self.curPos.t = self.dataRaw[0].t
        #print(f"Track position from idx {self.lastPosIdx} up to idx {idxHi}:")
        while self.lastPosIdx < idxHi:
            acc = self.dataRaw[self.lastPosIdx]
            #print(f"  idx {self.lastPosIdx}: Pos={self.curPos}, Vel={self.curVel}, Acc={acc}")
            Positioning.writeNextIntegralPoint(self.curVel, acc.t, acc.x, acc.y, acc.z)
            Positioning.writeNextIntegralPoint(self.curPos, self.curVel.t, self.curVel.x, self.curVel.y, self.curVel.z)
            self.lastPosIdx += 1
        # Write new position to the queue
        #print(f"New position update: {self.curPos}")
        self.positionQueue.put((self.curPos.t, (self.curPos.x, self.curPos.y, self.curPos.z)))
        


class PositionProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        return super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)

    def mainProcessing(self, *args):
        # Calculate all processing values and put them into the queue
        idxHi = len(self.t)-1
        if idxHi > 0:
            t = self.t[idxHi]
            idxLo = max(0, int(idxHi - (10 * self.samplingRate)))
            #avg = self.average(idxLo, idxHi)
            #maximum = self.maximum(idxLo, idxHi)
            #minimum = self.minimum(idxLo, idxHi)
            #freq = self.frequency(idxLo, idxHi)
            #mag = self.magnitude(idxLo, idxHi)
            #self.processingQueue.put((self.alertDataType, avg, maximum, minimum, freq, mag, t, (idxLo, idxHi)))
            self.addDataToVisualQueue(idxHi)


class TemperatureProcessing(DataProcessing):

    def __init__(self, alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue):
        super().__init__(alertDataType, name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)


    #def visualProcessing(self, *args):
    #    # Temperature is simple: read latest temperature and send it to visual queue
    #    if len(self.t) > 0:
    #        print(f"Adding temperature data to visual queue: {(self.t[-1], self.data[-1])}")
    #        self.visualQueue.put((self.t[-1], self.data[-1]))
