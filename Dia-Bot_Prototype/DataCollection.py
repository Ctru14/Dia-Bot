import sys
import time
from datetime import datetime
import threading
import multiprocessing
import math
from random import *

from Alerts import AlertDataType

class DataFields:

    def __init__(self, name, units, samplingRate, startTime, alertDataType):
        self.name = name
        self.units = units
        self.samplingRate = samplingRate
        self.samplingTime = 1/samplingRate
        self.startTime = startTime
        self.alertDataType = alertDataType


# Class is used in both the GPIO collection process and the processing process for queue collection
class DataCollection(DataFields):
    
    def __init__(self, name, units, samplingRate, startTime, dataQueue, alertDataType):
        super().__init__(name, units, samplingRate, startTime, alertDataType)
        #self.dataMutex = threading.Lock()
        #self.dataMutex = multiprocessing.Lock()
        self.startTime = startTime
        self.t = []
        self.data = []
        self.dataQueue = dataQueue
        
    # Used in processing process - appends new data point to the data array
    def addData(self, t, data):
        #self.dataMutex.acquire()
        self.t.append(t)  # self.t[-1]+self.samplingTime)
        self.data.append(data)
        #self.dataMutex.release()

    # Retrieves all new data from the queue and appends it to the array - called by processing process
    def getAndAddData(self, *args):
        #print(f"Attempting to retrieve from {self.name} queue {self.dataQueue}")
        while not self.dataQueue.empty():
            t, data = self.dataQueue.get()
            #print(f"Getting ({t}, {data}) from {self.name} data queue: {self.dataQueue}")
            self.addData(t, data)

    # Reads data from given function - called by data collection process
    def readAndSendData(self, *args):
        #t = time.time_ns()/1_000_000_000
        t = datetime.now()
        data = self.readData()
        self.dataQueue.put((t, data))
        #print(f"Putting {self.name} data ({data}) in visual queue: {self.visualQueue}")
        #self.visualQueue.put((t, data)) # TODO: decide if this is necessary
        #print(f"Adding ({t}, {data}) to {self.name} data queue: {self.dataQueue}")
        


class SoundLevelCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        return super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.SoundLevel)

    def readData(self):
        num = uniform(-10, 10)
        #print("Reading sound level! - " + str(num))
        return num



class VibrationCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Vibration)

    # addData override in DataProcessing class!
        
    def readData(self):
        vib = (uniform(-1, 1), uniform(-1, 1), uniform(-1, 1))
        #print("Reading vibration! - " + str(vib))
        return vib
    

class PositionCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        return super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Position)

    def readData(self):
        pos = (uniform(-10, 10), uniform(-10, 10), uniform(-10, 10))
        #print("Reading position! - " + str(pos))
        return pos



class TemperatureCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue, visualQueue): # TODO: REMOVE VISUAL QUEUE
        super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Temperature)
        self.visualQueue = visualQueue # TODO: REMOVE ONCE EXTRA PROCESS IS RUNNING

    def readData(self):
        num = uniform(-10, 10)
        #print("Reading temperature! - " + str(num))
        return num

    # Reads data from given function 
    def readAndSendData(self, *args):
        #t = time.time_ns()/1_000_000_000
        t = datetime.now()
        data = self.readData()
        self.dataQueue.put((t, data))
        self.visualQueue.put((t, data))

        