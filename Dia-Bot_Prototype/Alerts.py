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
class AlertDataType(enum.Enum):
    SoundLevel = 1
    Vibration = 2
    Position = 3
    Temperature = 4

class AlertMetric(enum.Enum):
    Average = 1
    Maximum = 2
    Minimum = 3
    Frequency = 4
    Magnitude = 5

class AlertRange(enum.Enum):
    Above = 1
    Between = 2
    Below = 3


class Alert:

    def __init__(self, alertDataType, alertTime, alertRange, alertMetric, tripValue):
        self.alertDataType = alertDataType
        self.alertTime = alertTime
        self.alertRange = alertRange
        self.alertMetric = alertMetric
        self.tripValue = tripValue


class AlertTracker: # TODO: Make class to contain many AlertTrackers - parses through multiple processing metrics and divides them accordingly
    # --- Static class variables ---
   
    alertRanges = (AlertRange.Above.name, AlertRange.Between.name, AlertRange.Below.name)
    #alertMetrics = (metric.name for metric in AlertMetric)

    def __init__(self, alertControlsFrame, name, thresholdUnits, alertDataType, alertRange, alertMetric, processingQueue, width=400, height=50):
        # Initialize data variables
        self.name = name
        self.thresholdUnits = thresholdUnits
        self.alertEnabled = BooleanVar()
        self.alertDataType = alertDataType
        self.alertRange = alertRange
        self.alertMetric = alertMetric
        #self.tripValue = tripValue
        self.alertRangeName = StringVar()
        self.alertRangeName.set(self.alertRange.name)
        self.alerts = []
        self.processingQueue = processingQueue
        #self.notificationQueue = multiprocessing.Queue()

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
        self.enableButton = tk.Checkbutton(self.frame, text=self.name, variable=self.alertEnabled, anchor="w", justify=LEFT, font="none 11")
        self.typeMenu = tk.OptionMenu(self.frame, self.alertRangeName, *AlertTracker.alertRanges, command=self.alertRangeChanged)
        self.input1 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString1)
        self.input2 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString2)
        self.unitsLabel = tk.Label(self.frame, text=self.thresholdUnits, anchor="w", justify=LEFT, font="none 11")
        self.notificationLabel = tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black")

    # Builds and returns the alert frame in self.frame 
    def getAlertFrame(self):
        #print(f"Creating and returning alert row for {self.name})
        self.enableButton.grid(row=1, column=1, columnspan=3)
        
        # Alert types
        self.typeMenu.grid(row=1, column=4, columnspan=2)
        
        # Input entry fields: Only show the second entry for 'Between' mode
        self.input1.grid(row=1, column=6, columnspan=2)
        if (self.alertRange == AlertRange.Between):
            self.input2.grid(row=1, column=8, columnspan=2)
            
        # Units
        self.unitsLabel.grid(row=1, column=9, columnspan=2)

        # Alert notification
        self.notificationLabel.grid(row=1, column=11, columnspan=2)
        return self.frame
    
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
            self.input2.grid(row=1, column=8, columnspan=2)
            
    
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
   
    # Setting up and testing multiprocessing!
    def checkForAlerts(self):
        # TODO: MOVE DATA SOURCE TO PROCESSING PROCESS
        # Testing UI: Randomly add alerts to the queue
        #if randint(0, 10) == 2:
        #    newAlert = Alert(self.alertDataType, time.time(), self.alertRange, self.alertMetric, 10)
        #    self.processingQueue.put(newAlert)

        # Check notification queue for alerts
        if not self.processingQueue.empty(): #  TODO: READ AND PARSE PROCESSING DATA TO FORM ALERT
            processed = self.processingQueue.get()
            print(f"Receiving processed data! {processed}")
            #alert = self.processingQueue.get()
            #if self.alertEnabled.get():
            #    timeString = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(alert.alertTime)) # Add %Z to show time zone
            #    self.alerts.append(alert)
            #    print(f"Alert #{len(self.alerts)} in {self.name} at {timeString}: {alert.alertRange.name}, {alert.tripValue}{self.thresholdUnits}")
            #    self.notificationLabel.grid_forget()
            #    self.notificationLabel = tk.Label(self.frame, text="Error", anchor=CENTER, font="none 11 bold", fg="red")
            #    self.notificationLabel.grid(row=1, column=11, columnspan=2)
    
