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
        self.alertType = alertType
        self.alertTypeName = StringVar()
        self.alertTypeName.set(self.alertType.name)

        # Threshold levels
        self.belowValue = nan
        self.aboveValue = nan
        self.betweenLowValue = nan
        self.betweenAboveValue = nan

        # Create TKinter frame
        self.frame = tk.Frame(alertControlsFrame, width=400, height=50)

    # Builds and returns the alert frame in self.frame 
    def getAlertFrame(self):
        #print(f"Creating and returning alert row for {self.name})
        tk.Checkbutton(self.frame, text=self.name, anchor="w", justify=LEFT, font="none 11").grid(row=1, column=1, columnspan=3)
        tk.OptionMenu(self.frame, self.alertTypeName, *Alert.alertTypes, command=self.alertTypeChanged).grid(row=1, column=4, columnspan=2)
        tk.Entry(self.frame, justify=CENTER, width=5, font="none 11").grid(row=1, column=6, columnspan=2)
        tk.Label(self.frame, text=self.thresholdUnits, anchor="w", justify=LEFT, font="none 11").grid(row=1, column=8, columnspan=2)
        if randint(0,1) == 1:
            tk.Label(self.frame, text="Error", anchor=CENTER, font="none 11 bold", fg="red").grid(row=1, column=10, columnspan=2)
        else:
            tk.Label(self.frame, text="None", anchor=CENTER, font="none 11", fg="black").grid(row=1, column=10, columnspan=2)
        return self.frame
    
    # Callback function for changing the alert type
    def alertTypeChanged(self, typeName):
        self.alertTypeName.set(typeName)
        print(f"Option changed! {typeName}")
    
   
    