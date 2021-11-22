import sys
import tkinter as tk
from tkinter import *
import time
import threading
import multiprocessing
from math import *
from random import *
import enum

# Dia-Bot classes
import DataCollection

# Types of alerts - range, processing metric, data type

# Starts from 0 to index into AlertsTop lists
class AlertDataType(enum.IntEnum):
    SoundLevel = 0
    Vibration = 1
    Position = 2
    Temperature = 3

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

    def __init__(self, alertDataType, alertTime, alertRange, alertMetric, tripValue):
        self.alertDataType = alertDataType
        self.alertTime = alertTime
        self.alertRange = alertRange
        self.alertMetric = alertMetric
        self.tripValue = tripValue


alertDataTypes = (AlertDataType.SoundLevel.name, AlertDataType.Vibration.name, AlertDataType.Position.name, AlertDataType.Temperature.name)
alertMetrics = (AlertMetric.Average.name, AlertMetric.Maximum.name, AlertMetric.Minimum.name, AlertMetric.Frequency.name, AlertMetric.Magnitude.name)
alertRanges = (AlertRange.Above.name, AlertRange.Between.name, AlertRange.Below.name)
dataTypeUnits = ("dB", "m/s2", "m", "°C")

class AlertTracker:
   
    def __init__(self, alertsTop, alertControlsFrame, name, alertDataType, alertRange, alertMetric, width=400, height=100):
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
        self.alerts = []

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
        self.input1 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString1)
        self.input2 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString2)
        self.unitsLabel = tk.Label(self.frame, text=self.thresholdUnits, anchor="w", justify=RIGHT, font="none 11")
        self.clearButton = tk.Button(self.frame, text="CLR", command=self.clearAlerts)
        self.deleteButton = tk.Button(self.frame, text="DEL", command=self.deleteTracker)

    # Builds and returns the alert frame in self.frame 
    def getAlertFrame(self):
        #print(f"Creating and returning alert row for {self.name})
        self.nameEnableButton.grid(row=1, column=1, columnspan=3)
        self.dataTypeLabel.grid(row=1, column=4, columnspan=2)
        self.metricLabel.grid(row=1, column=7, columnspan=2)
        self.notificationLabel.grid(row=1, column=9, columnspan=3)

        # Alert ranges
        self.rangeMenu.grid(row=2, column=2, columnspan=2)
        
        # Input entry fields: Only show the second entry for 'Between' mode
        self.input1.grid(row=2, column=4, columnspan=2)
        if (self.alertRange == AlertRange.Between):
            self.input2.grid(row=2, column=6, columnspan=2)
            
        # Units
        self.unitsLabel.grid(row=2, column=9, columnspan=2)

        # Clear and Delete buttons
        self.clearButton.grid(row=2, column=11)
        self.deleteButton.grid(row=2, column=12)

        # Alert notification
        return self.frame
    
    def deleteTracker(self):
        print(f"Delete tracker: {self.name}")
        self.alertsTop.removeTracker(self)
        self.frame.grid_forget()

    # Callback function for changing the alert type
    def alertRangeChanged(self, typeName):
        self.alertRangeName.set(typeName)
        self.alertRange = AlertRange[typeName]
        if typeName == AlertRange.Above.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change above limit!")
            self.input2.grid_forget()
        elif typeName == AlertRange.Below.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change below limit!")
            self.input2.grid_forget()
        elif typeName == AlertRange.Between.name:
            print(f"Alert type changed to {self.alertRange} ({typeName}): change between limits and add the entry box")
            self.input2.grid(row=2, column=6, columnspan=2)
            
    
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
        self.alerts.clear()
        self.notificationLabel.grid_forget()
        self.notificationLabel = tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black")
        self.notificationLabel.grid(row=1, column=11, columnspan=2)

    def setErrorLabel(self):
        #timeString = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(alert.alertTime)) # Add %Z to show time zone
        self.notificationLabel.grid_forget()
        self.notificationLabel = tk.Label(self.frame, text=f"Error({len(self.alerts)})", anchor=CENTER, font="none 11 bold", fg="red")
        self.notificationLabel.grid(row=1, column=11, columnspan=2)

    def checkForAlerts(self, t, value):
        if self.alertEnabled.get():
            # Checks tracker thresholds to compare this value
            if self.alertRange == AlertRange.Above:
                if value > self.aboveValue:
                    self.alerts.append(Alert(self.alertDataType, t, self.alertRange, self.alertMetric, value))
                    print(f"Alert #{len(self.alerts)} found in {self.name} tracker at time {t}! {self.alertMetric.name}={value} {self.alertRange.name} {self.aboveValue}")
                    self.setErrorLabel()
            if self.alertRange == AlertRange.Below:
                if value < self.belowValue:
                    self.alerts.append(Alert(self.alertDataType, t, self.alertRange, self.alertMetric, value))
                    print(f"Alert #{len(self.alerts)} found in {self.name} tracker at time {t}! {self.alertMetric.name}={value} {self.alertRange.name} {self.belowValue}")
                    self.setErrorLabel()
            if self.alertRange == AlertRange.Between:
                if value < self.betweenHiValue and value > self.betweenLoValue:
                    self.alerts.append(Alert(self.alertDataType, t, self.alertRange, self.alertMetric, value))
                    print(f"Alert #{len(self.alerts)} found in {self.name} tracker at time {t}! {self.alertMetric.name}={value} {self.alertRange.name} {self.betweenLoValue} and {self.betweenHiValue}")
                    self.setErrorLabel()

# Top-level class to contain AlertTrackers
# Receives processing info from queue and sends it to each relevant tracker
class AlertsTop:

    def __init__(self, alertControlsFrame, alertTrackersFrame, processingQueue):
        self.alertControlsFrame = alertControlsFrame
        self.alertTrackersFrame = alertTrackersFrame
        self.processingQueue = processingQueue
        # Sort trackers in lists based on their data type
        self.soundLevelTrackers = []
        self.vibrationTrackers = []
        self.positionTrackers = []
        self.temperatureTrackers = []
        self.trackers = [self.soundLevelTrackers, self.vibrationTrackers, self.positionTrackers, self.temperatureTrackers]
        # TK variables for the Add New Alert frame
        self.nameEntryVar = StringVar()
        self.nameEntryVar.set("Name")
        self.newDataTypeVar = StringVar()
        self.newMetricVar = StringVar()
        self.nextTrackerRow = 1

    def addTracker(self, tracker):
        # Add tracker to a list based on the data type
        self.trackers[tracker.alertDataType].append(tracker)
        #print(f"Added {tracker.alertDataType.name} Tracker: {tracker.name}. There are now {len(self.trackers[tracker.alertDataType])}")
        # TODO: Update GUI with new tracker
        tracker.getAlertFrame().grid(row=self.nextTrackerRow, column=1, columnspan=10)
        self.nextTrackerRow += 1

    # Delete tracker from UI and Top
    def removeTracker(self, tracker):
        trackersList = self.trackers[tracker.alertDataType]
        found = False
        for i in range(len(trackersList)):
            if trackersList[i] == tracker:
                found = True
                #print(f"Tracker found at index {i}! Removing (len {len(trackersList)})...")
                trackersList.pop(i)
                #print(f"...new len {len(trackersList)}")
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

    def buildAndAddTracker(self):
        newTracker = AlertTracker(self, self.alertTrackersFrame, self.nameEntryVar.get(), self.newDataType, AlertRange.Above, AlertMetric.Average)
        self.addTracker(newTracker) # Add to existing list
        # Clear new tracker frame of the previous name name
        self.nameEntryVar.set("Name")
        return newTracker

    def updateAlerts(self):
        for trackerList in self.trackers:
            for tracker in trackerList:
                tracker.confirmUpdates()

    # Check processing queue for new metrics and distribute to proper trackers
    def readProcessedData(self):
        # TODO: MOVE DATA SOURCE TO PROCESSING PROCESS
        # Testing UI: Randomly add alerts to the queue
        #if randint(0, 10) == 2:
        #    newAlert = Alert(self.alertDataType, time.time(), self.alertRange, self.alertMetric, 10)
        #    self.processingQueue.put(newAlert)

        # Check processing queue for new data
        while not self.processingQueue.empty(): #  TODO: READ AND PARSE PROCESSING DATA TO FORM ALERT
            processed = self.processingQueue.get()
            dataType = processed[0]
            alertTime = processed[6]
            for tracker in self.trackers[int(dataType)]:
                value = processed[int(tracker.alertMetric)]
                tracker.checkForAlerts(alertTime, value)
