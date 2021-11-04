import sys
import tkinter as tk
from tkinter import *
import time
import threading
from math import *
from random import *
import enum

# Dia-Bot classes
import DataCollection


class Alert:
    # --- Static class variables ---
    class AlertType(enum.Enum):
        Above = 1
        Between = 2
        Below = 3

    alertTypes = (AlertType.Above.name, AlertType.Between.name, AlertType.Below.name)

    def __init__(self, alertControlsFrame, name, thresholdUnits, alertType, width=400, height=50):
        # Initialize data variables
        self.name = name
        self.thresholdUnits = thresholdUnits
        self.alertEnabled = BooleanVar()
        self.alertType = alertType
        self.alertTypeName = StringVar()
        self.alertTypeName.set(self.alertType.name)

        # Threshold levels
        self.belowValue = nan
        self.aboveValue = nan
        self.betweenLoValue = nan
        self.betweenHiValue = nan

        # Strings to hold the alert thresholds
        self.thresholdString1 = StringVar()
        self.thresholdString2 = StringVar()

        # Create TKinter frame
        self.frame = tk.Frame(alertControlsFrame, width=400, height=50)

    # Builds and returns the alert frame in self.frame 
    def getAlertFrame(self):
        #print(f"Creating and returning alert row for {self.name})
        self.enableButton = tk.Checkbutton(self.frame, text=self.name, variable=self.alertEnabled, anchor="w", justify=LEFT, font="none 11")
        self.enableButton.grid(row=1, column=1, columnspan=3)
        
        # Alert type s
        self.typeMenu = tk.OptionMenu(self.frame, self.alertTypeName, *Alert.alertTypes, command=self.alertTypeChanged)
        self.typeMenu.grid(row=1, column=4, columnspan=2)
        
        # Input entry fields: Only show the second entry for 'Between' mode
        self.input1 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString1)
        self.input1.grid(row=1, column=6, columnspan=2)
        self.input2 = tk.Entry(self.frame, justify=CENTER, width=5, font="none 11", textvariable=self.thresholdString2)
        if (self.alertType == Alert.AlertType.Between):
            self.input2.grid(row=1, column=8, columnspan=2)
            
        # Units
        tk.Label(self.frame, text=self.thresholdUnits, anchor="w", justify=LEFT, font="none 11").grid(row=1, column=9, columnspan=2)
        
        # Alert notification
        if randint(0,1) == 1:
            tk.Label(self.frame, text="Error", anchor=CENTER, font="none 11 bold", fg="red").grid(row=1, column=11, columnspan=2)
        else:
            tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black").grid(row=1, column=11, columnspan=2)
        return self.frame
    
    # Callback function for changing the alert type
    def alertTypeChanged(self, typeName):
        self.alertTypeName.set(typeName)
        self.alertType = self.AlertType[typeName]
        if typeName == self.AlertType.Above.name:
            print(f"Alert type changed to {self.alertType} ({typeName}): change above limit!")
            self.input2.grid_forget()
        elif typeName == self.AlertType.Below.name:
            print(f"Alert type changed to {self.alertType} ({typeName}): change below limit!")
            self.input2.grid_forget()
        elif typeName == self.AlertType.Between.name:
            print(f"Alert type changed to {self.alertType} ({typeName}): change between limits and add the entry box")
            self.input2.grid(row=1, column=8, columnspan=2)
            
    
    def confirmUpdates(self):
        try:
           threshold1 = float(self.thresholdString1.get())
           if self.alertType == self.AlertType.Above:
               self.aboveValue = threshold1
           elif self.alertType == self.AlertType.Below:
               self.belowValue = threshold1
        except:
            print(f"Error: cannot convert string {self.thresholdString1.get()} to a number")
        if self.alertType == self.AlertType.Between:
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
   