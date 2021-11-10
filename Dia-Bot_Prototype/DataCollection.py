import sys
import time
import multiprocessing
import math
from random import *


class DataCollection:
    
    def __init__(self, name, units, samplingRate, globalStartTime, queue):
        self.name = name
        self.units = units
        self.samplingRate = samplingRate
        self.samplingTime = 1/samplingRate
        #self.dataMutex = threading.Lock()
        self.dataMutex = multiprocessing.Lock()
        self.globalStartTime = globalStartTime
        self.t = []
        self.data = []
        self.queue = queue
        
    def addData(self, t, data):
        self.dataMutex.acquire()
        self.t.append(t)  # self.t[-1]+self.samplingTime)
        self.data.append(data)
        self.dataMutex.release()

    def readAndAddData(self, *args):
        t = (time.time_ns()-self.globalStartTime)/1_000_000_000
        data = self.readData()
        self.addData(t, data)

    def readAndSendData(self, *args):
        t = (time.time_ns()-self.globalStartTime)/1_000_000_000
        data = self.readData()
        self.queue.put((t, data))
        


class SoundLevelCollection(DataCollection):

    def __init__(self, name, units, samplingRate, globalStartTime, queue):
        return super().__init__(name, units, samplingRate, globalStartTime, queue)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading sound level! - " + str(num))
        return num



class VibrationCollection(DataCollection):

    def __init__(self, name, units, samplingRate, globalStartTime, queue):
        return super().__init__(name, units, samplingRate, globalStartTime, queue)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading vibration! - " + str(num))
        return num
    
    

class PositionCollection(DataCollection):

    def __init__(self, name, units, samplingRate, globalStartTime, queue):
        return super().__init__(name, units, samplingRate, globalStartTime, queue)

    def readData(self):
        num = randint(-10, 10)
        #print("Reading position! - " + str(num))
        return num



class TemperatureCollection(DataCollection):

    def __init__(self, name, units, samplingRate, globalStartTime, queue):
        self.currentTempCelsius = 0
        self.currentTempFarenheit = 32
        return super().__init__(name, units, samplingRate, globalStartTime, queue)

    def readData(self):
        num = randint(-10, 10)
        self.currentTempCelsius = num
        self.currentTempFarenheit = num * 9 / 5 + 32
        #print("Reading temperature! - " + str(num))
        return num

    def readAndSendData(self, *args):
        t = (time.time_ns()-self.globalStartTime)/1_000_000_000
        temp = self.readData()
        self.currentTempCelsius = temp
        self.currentTempFarenheit = temp * 9 / 5 + 32
        self.queue.put((t, self.currentTempCelsius, self.currentTempFarenheit))
        