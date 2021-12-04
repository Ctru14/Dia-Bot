import sys
import os
import tkinter as tk
from tkinter import *
import time
import threading
import multiprocessing
import uuid
from math import *
from random import *
import enum
from copy import deepcopy

# Dia-Bot classes
import DataCollection
from Positioning import Point3d

# Types of alerts - range, processing metric, data type

# Starts from 0 to index into AlertsTop lists
class AlertDataType(enum.IntEnum):
    SoundLevel = 0
    Vibration = 1
    Temperature = 2
    Position = 3

# Starts from 1 to index into ProcessingQueue tuple (which has the data type as the first member) 
class AlertMetric(enum.IntEnum):
    Average = 1
    Maximum = 2
    Minimum = 3
    Frequency = 4
    Magnitude = 5

class AlertRange(enum.IntEnum):
    Above = 0
    Between = 1
    Below = 2


class Alert:

    def __init__(self, alertDataType, alertTime, alertRange, alertMetric, tripValue, indices, trackerName = ""):
        self.id = str(uuid.uuid4())
        self.alertDataType = alertDataType
        self.time = alertTime
        self.alertRange = alertRange
        self.alertMetric = alertMetric
        self.tripValue = tripValue
        self.indices = indices
        self.trackerName = trackerName


alertDataTypes = (AlertDataType.SoundLevel.name, AlertDataType.Vibration.name, AlertDataType.Temperature.name)
fullDataTypes = (AlertDataType.SoundLevel.name, AlertDataType.Vibration.name, AlertDataType.Temperature.name, AlertDataType.Position.name)
alertMetrics = (AlertMetric.Average.name, AlertMetric.Maximum.name, AlertMetric.Minimum.name, AlertMetric.Frequency.name, AlertMetric.Magnitude.name)
alertRanges = (AlertRange.Above.name, AlertRange.Between.name, AlertRange.Below.name)
dataTypeUnits = ("dB", "m/s2", "°C", "m")

class AlertTracker:
   
    def __init__(self, alertsTop, alertControlsFrame, name, alertDataType, alertRange, alertMetric, alertIOqueue, deleteIcon, clearIcon, width=400, height=100):
        # Initialize data variables
        self.name = name
        self.alertsTop = alertsTop
        self.alertEnabled = BooleanVar()
        self.alertDataType = alertDataType
        self.thresholdUnits = dataTypeUnits[int(alertDataType)]
        self.alertRange = alertRange
        self.alertMetric = alertMetric
        self.alertRangeName = StringVar()
        self.alertRangeName.set(self.alertRange.name)
        self.alertIOqueue = alertIOqueue
        self.alerts = []
        self.deleteIcon = deleteIcon
        self.clearIcon = clearIcon
        self.errorActive = False
        self.alertsMutex = threading.Lock()
        self.alertsDataPath = self.alertsTop.alertsDataPaths[int(self.alertDataType)]
        self.dateTimeFormat = "{:%Y%m%d-%H%M%S}"

        # Threshold levels
        self.belowValue = nan
        self.aboveValue = nan
        self.betweenLoValue = nan
        self.betweenHiValue = nan

        # Strings to hold the alert thresholds
        self.thresholdString1 = StringVar()
        self.thresholdString2 = StringVar()

        # Create TKinter frame
        self.frame = tk.Frame(alertControlsFrame, width=width, height=height)
        self.nameEnableButton = tk.Checkbutton(self.frame, text=self.name, variable=self.alertEnabled, anchor="w", justify=LEFT, font="none 11")
        self.dataTypeLabel = tk.Label(self.frame, text=self.alertDataType.name, anchor="w", justify=LEFT, font="none 11")
        self.metricLabel = tk.Label(self.frame, text=self.alertMetric.name, anchor="w", justify=LEFT, font="none 11")
        self.notificationLabel = tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black")
        self.rangeMenu = tk.OptionMenu(self.frame, self.alertRangeName, *alertRanges, command=self.alertRangeChanged)
        self.input1 = tk.Entry(self.frame, justify=CENTER, width=6, font="none 11", textvariable=self.thresholdString1)
        self.input2 = tk.Entry(self.frame, justify=CENTER, width=6, font="none 11", textvariable=self.thresholdString2)
        self.unitsLabel = tk.Label(self.frame, text=self.thresholdUnits, anchor="w", justify=RIGHT, font="none 11")
        self.clearButton = tk.Button(self.frame, image=self.clearIcon, command=self.clearAlerts)
        self.deleteButton = tk.Button(self.frame, image=self.deleteIcon, command=self.deleteTracker)

    # Builds and returns the alert frame in self.frame 
    def getAlertFrame(self):
        #print(f"Creating and returning alert row for {self.name})
        self.nameEnableButton.place(x=0, y=0, anchor=tk.NW)
        self.dataTypeLabel.place(x=135, y=0, anchor=tk.NW)
        self.metricLabel.place(x=260, y=0, anchor=tk.NW)
        self.notificationLabel.place(x=400, y=0, anchor=tk.NE)

        # Alert ranges
        self.rangeMenu.place(x=0, y=30, anchor=tk.NW)
        
        # Input entry fields: Only show the second entry for 'Between' mode
        self.input1.place(x=110, y=30, anchor=tk.NW)
        if (self.alertRange == AlertRange.Between):
            self.input2.place(x=185, y=30, anchor=tk.NW)
            
        # Units
        self.unitsLabel.place(x=260, y=30, anchor=tk.NW)

        # Clear and Delete buttons
        self.clearButton.place(x=365, y=30, anchor=tk.NE)
        self.deleteButton.place(x=400, y=30, anchor=tk.NE)

        # Alert notification
        return self.frame
    
    def deleteTracker(self):
        print(f"Delete tracker: {self.name}")
        self.frame.destroy()
        self.alertsTop.removeTracker(self)

    # Callback function for changing the alert type
    def alertRangeChanged(self, typeName):
        self.alertRangeName.set(typeName)
        self.alertRange = AlertRange[typeName]
        if typeName == AlertRange.Above.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change above limit!")
            self.input2.place_forget()
        elif typeName == AlertRange.Below.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change below limit!")
            self.input2.place_forget()
        elif typeName == AlertRange.Between.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change between limits and add the entry box")
            self.input2.place(x=185, y=30, anchor=tk.NW)
            
    
    def confirmUpdates(self):
        try:
           threshold1 = float(self.thresholdString1.get())
           if self.alertRange == AlertRange.Above:
               self.aboveValue = threshold1
           elif self.alertRange == AlertRange.Below:
               self.belowValue = threshold1
        except:
            print(f"Error: cannot convert string {self.thresholdString1.get()} to a number")
        if self.alertRange == AlertRange.Between:
            try:
               threshold2 = float(self.thresholdString2.get())
               thresholdLo = min(threshold1, threshold2)
               thresholdHi = max(threshold1, threshold2)
               self.thresholdString1.set(str(thresholdLo))
               self.thresholdString2.set(str(thresholdHi))
               self.betweenLoValue = thresholdLo
               self.betweenHiValue = thresholdHi
            except:
                print(f"Error: cannot convert string {self.thresholdString2.get()} to a number")

    def clearAlerts(self):
        self.errorActive = False
        self.alertsMutex.acquire()
        self.alerts.clear()
        self.alertsMutex.release()
        self.notificationLabel.place_forget()
        self.notificationLabel = tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black")
        self.notificationLabel.place(x=400, y=0, anchor=tk.NE)

    def setErrorLabel(self):
        #timeString = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(alert.time)) # Add %Z to show time zone
        self.notificationLabel.place_forget()
        self.notificationLabel = tk.Label(self.frame, text=f"Error({len(self.alerts)})", anchor=CENTER, font="none 11 bold", fg="red")
        self.notificationLabel.place(x=400, y=0, anchor=tk.NE)

    def checkAlertCondition(self, value):
        if self.alertRange == AlertRange.Above:
            if value > self.aboveValue:
                self.tripValue = self.aboveValue
                return True
        elif self.alertRange == AlertRange.Below:
            if value < self.belowValue:
                self.tripValue = self.belowValue
                return True
        elif self.alertRange == AlertRange.Between:
            if value < self.betweenHiValue and value > self.betweenLoValue:
                self.tripValue = (self.betweenLoValue, self.betweenHiValue)
                return True
        return False

    def checkForAlerts(self, t, value, indices, position):
        if self.alertEnabled.get():
            errorFound = False
            # Checks tracker thresholds to compare this value
            if self.checkAlertCondition(value):
                errorFound = True
                #isNewAlert = False
                if not self.errorActive:
                    self.errorActive = True
                    isNewAlert = True
                    newAlert = Alert(self.alertDataType, t, self.alertRange, self.alertMetric, value, indices, self.name)
                    self.alertsMutex.acquire()
                    self.alerts.append(newAlert)
                    self.alertsMutex.release()
                    print(f"Alert #{len(self.alerts)} found in {self.name} tracker at time {t}! {self.alertMetric.name}={value} {self.alertRange.name} {self.tripValue}")
                    self.setErrorLabel()
                else:
                    isNewAlert = False
                    print(f"Error {self.alerts[-1].id} currently active in {self.name}! Append data to file...")
                    self.alertsMutex.acquire()
                    newAlert = deepcopy(self.alerts[-1])
                    self.alertsMutex.release()
                    newAlert.indices = indices
                # Alert found: Make new directory if it doesn't already exist
                # Construct directory name:  YYYYMMDD-hhmmss_Metric_Range_ID/
                trackerName = self.name.replace(" ", "")
                #timeString = time.strftime(self.timeFormat, time.gmtime(alert.time)) # time.gmtime(alert.time).strftime(self.timeFormat)
                timeString = self.dateTimeFormat.format(newAlert.time)#.strftime(self.timeFormat, time.gmtime(alert.time)) # time.gmtime(alert.time).strftime(self.timeFormat)
                alertDirName = f"{trackerName}_{timeString}_{self.alertMetric.name}_{self.alertRange.name}"
                alertDirPath = os.path.join(self.alertsDataPath, alertDirName)
                if not os.path.exists(alertDirPath):
                    # Create new alert directory
                    os.mkdir(alertDirPath)
                self.alertIOqueue.put((newAlert, position, alertDirPath, isNewAlert))
                self.alertsTop.takeImageFunction(os.path.join(alertDirPath, f"img-{self.dateTimeFormat.format(t)}.jpg"))
            # Check if active error needs to be reset
            if self.errorActive and not errorFound:
                print(f"Previously active error in {self.name} was not tripped - resetting active")
                self.errorActive = False


# Top-level class to contain AlertTrackers
# Receives processing info from queue and sends it to each relevant tracker
class AlertsTop:

    def __init__(self, alertControlsFrame, alertTrackersFrame, processingQueue, alertIOqueues, deleteIcon, clearIcon, takeImageFunction):
        self.alertControlsFrame = alertControlsFrame
        self.alertTrackersFrame = alertTrackersFrame
        self.processingQueue = processingQueue
        self.alertIOqueues = alertIOqueues
        self.deleteIcon = deleteIcon
        self.clearIcon = clearIcon
        self.position = (0.0, 0.0, 0.0) # Sent with Alerts in IO queue
        self.takeImageFunction = takeImageFunction
        # Sort trackers in lists based on their data type
        self.soundLevelTrackers = []
        self.vibrationTrackers = []
        #self.positionTrackers = []
        self.temperatureTrackers = []
        self.trackers = [self.soundLevelTrackers, self.vibrationTrackers, self.temperatureTrackers]
        #self.trackers = [self.soundLevelTrackers, self.vibrationTrackers, self.positionTrackers, self.temperatureTrackers]
        # TK variables for the Add New Alert frame
        self.nameEntryVar = StringVar()
        self.nameEntryVar.set("Tracker Name")
        self.newDataTypeVar = StringVar()
        self.newMetricVar = StringVar()
        # Create new directory for alerts, if it does not exist yet
        self.rootPath = os.path.dirname(__file__)
        self.alertsPath = os.path.join(self.rootPath, "Alerts")
        if not os.path.exists(self.alertsPath):
            print(f"Alerts path does not exist - creating: {self.alertsPath}")
            os.mkdir(self.alertsPath)
        self.alertsDataPaths = []
        for name in alertDataTypes:
            alertsDataPath = os.path.join(self.alertsPath, name)
            self.alertsDataPaths.append(alertsDataPath)
            if not os.path.exists(alertsDataPath):
                print(f"{name} alerts data path does not exist - creating: {alertsDataPath}")
                os.mkdir(alertsDataPath)

        
    def addTracker(self, tracker):
        # Add tracker to a list based on the data type
        self.trackers[tracker.alertDataType].append(tracker)
        tracker.getAlertFrame().pack()

    # Delete tracker from UI and Top
    def removeTracker(self, tracker):
        trackersList = self.trackers[tracker.alertDataType]
        found = False
        for i in range(len(trackersList)):
            if trackersList[i] == tracker:
                found = True
                trackersList.pop(i)
                break
        if not found:
            print(f"Error in alertsTop.removeTracker: ({tracker.name}) not found!")

    def buildNewTrackerFrame(self, alertControlsFrame, width=400, height=100):
        # Create TKinter frame
        self.newTrackerFrame = tk.Frame(alertControlsFrame, width=width, height=height)
        self.newTrackerLabel = tk.Label(self.newTrackerFrame, text="Add New Alert:", anchor=CENTER, font="none 11", fg="black")
        self.newTrackerLabel.grid(row=1, column=1, columnspan=4)
        self.nameEntry = tk.Entry(self.newTrackerFrame, justify=CENTER, width=15, font="none 11", textvariable=self.nameEntryVar)
        self.nameEntry.grid(row=1, column=5, columnspan=4)
        self.dataTypeMenu = tk.OptionMenu(self.newTrackerFrame, self.newDataTypeVar, *alertDataTypes, command=self.alertDataTypeChanged)
        self.dataTypeMenu.grid(row=2, column=3, columnspan=3)
        self.metricMenu = tk.OptionMenu(self.newTrackerFrame, self.newMetricVar, *alertMetrics, command=self.alertMetricChanged)
        self.metricMenu.grid(row=2, column=6, columnspan=3)
        self.addButton = tk.Button(self.newTrackerFrame, text="+", command=self.buildAndAddTracker)
        self.addButton.grid(row=1, column=10, rowspan=2, columnspan=2)
        return self.newTrackerFrame
        
    # Callback function for selecting a new alert data type
    def alertDataTypeChanged(self, typeName):
        self.newDataTypeVar.set(typeName)
        self.newDataType = AlertDataType[typeName]
        
    # Callback function for selecting a new alert metric
    def alertMetricChanged(self, metricName):
        self.newMetricVar.set(metricName)
        self.newMetric = AlertMetric[metricName]

    # Callback button for "+" new tracker - take UI input to build and add a new tracker
    def buildAndAddTracker(self):
        if len(self.newDataTypeVar.get()) > 1 and len(self.newMetricVar.get()) > 1:
            newTracker = AlertTracker(self, self.alertTrackersFrame, self.nameEntryVar.get(), self.newDataType, AlertRange.Above, self.newMetric, self.alertIOqueues[int(self.newDataType)], self.deleteIcon, self.clearIcon)
            self.addTracker(newTracker) # Add to existing list
            # Clear new tracker frame of the previous name name
            self.nameEntryVar.set("Tracker Name")
            return newTracker
        else:
            print("Error in buildAndAddTracker: data type or metric not selected!")

    # Accept UI changes to existing alert trackers to change tracker behavior
    def updateAlerts(self):
        for trackerList in self.trackers:
            for tracker in trackerList:
                tracker.confirmUpdates()

    # Check processing queue for new metrics and distribute to proper trackers
    def distributeProcessedData(self, position):
        # Check processing queue for new data
        self.position = position
        while not self.processingQueue.empty():
            processed = self.processingQueue.get()
            dataType = processed[0]
            alertTime = processed[6]
            indices = processed[7]
            for tracker in self.trackers[int(dataType)]:
                value = processed[int(tracker.alertMetric)]
                tracker.checkForAlerts(alertTime, value, indices, position)
