import sys
import time
from datetime import datetime
import threading
import multiprocessing
import math
from random import *

from PiInterface import Accelerometer
from PiInterface import ADC

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
        self.startTime = startTime
        self.t = []
        self.data = []
        self.dataQueue = dataQueue
        
    # Used in processing process - appends new data point to the data array
    def addData(self, t, data):
        #self.dataMutex.acquire()
        self.t.append(t)
        self.data.append(data)
        #self.dataMutex.release()

    # Retrieves all new data from the queue and appends it to the array - called by processing process
    def getAndAddData(self, *args):
        while not self.dataQueue.empty():
            t, data = self.dataQueue.get()
            self.addData(t, data)

    # Reads data from given function - called by data collection process
    def readAndSendData(self, *args):
        t = datetime.now()
        data = self.readData()
        self.dataQueue.put((t, data))
        


# DEPRECATED - SOUND LEVEL USES ADC COLLECTION CLASS
class SoundLevelCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.SoundLevel)
        #self.adc = ADC()

    def readData(self):
        num = uniform(-10, 10)
        return num
    
    #def readData(self):
        #return self.adc.readSoundData()
        



class VibrationCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Vibration)
        self.accelerometer = Accelerometer()

    # addData override in DataProcessing class!

    def readData(self):
        return self.accelerometer.readAccData()
        
    

# DEPRECATED - POSITION IS NO LONGER HANDLED LIKE THE OTHER DATA TYPES! (updated by vibration)
#  Leaving this here in case a new position method is found in the future
class PositionCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue):
        return super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Position)

    def readData(self):
        pos = (uniform(-10, 10), uniform(-10, 10), uniform(-10, 10))
        #print("Reading position! - " + str(pos))
        return pos



class TemperatureCollection(DataCollection):

    def __init__(self, name, units, samplingRate, startTime, dataQueue): 
        super().__init__(name, units, samplingRate, startTime, dataQueue, AlertDataType.Temperature)
        #self.adc = ADC()
    
    def readData(self):
        return self.adc.readTemperatureData()

    # Reads data from given function (DEPRECATED - INSTEAD USES ACD COLLECTION)
    def readAndSendData(self, *args):
        t = datetime.now()
        data = self.readData()
        self.dataQueue.put((t, data))
        #self.visualQueue.put((t, data))

    
class ADCCollection():

    def __init__(self, name, soundLevelSamplingRate, soundLevelDataQueue, temperatureDataQueue):
        self.samplingRate = soundLevelSamplingRate
        self.soundLevelDataQueue = soundLevelDataQueue
        self.temperatureDataQueue = temperatureDataQueue
        self.tempLoopNum = 0
        self.tempLoopMax = self.samplingRate * 4 # Approximately 4s/Temp
        self.adc = ADC()
        
        
    def readAndSendData(self, *args):
        t = datetime.now()
        soundData = self.adc.readSoundData()
        self.soundLevelDataQueue.put((t, soundData))
        if self.tempLoopNum == 0:
            tempData = self.adc.readTemperatureData()
            self.temperatureDataQueue.put((t, tempData))
        self.tempLoopNum += 1
        if self.tempLoopNum == self.tempLoopMax:
            self.tempLoopNum = 0