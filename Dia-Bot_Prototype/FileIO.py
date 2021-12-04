import sys
import os
import csv
from PIL import ImageTk, Image
import time
import threading
import math
import enum

# Dia-Bot specific imports
import DataCollection
import DataDisplay
import DataProcessing
import Alerts
import Threads
from Alerts import Alert
from Alerts import AlertDataType
from Alerts import AlertMetric
from Alerts import AlertRange
from Alerts import AlertTracker
from Alerts import AlertsTop



class FileIO:

    # New FileIO class runs in the same process context as the rest of the data
    def __init__(self, fields, alertIOqueue, processing):
        self.name = fields.name
        self.units = fields.units
        self.samplingRate = fields.samplingRate
        self.alertDataType = fields.alertDataType
        self.processing = processing
        self.alertIOqueue = alertIOqueue
        # Create new directory for alerts, if it does not exist yet
        self.rootPath = os.path.dirname(__file__)
        self.alertsPath = os.path.join(self.rootPath, "Alerts")
        if not os.path.exists(self.alertsPath):
            print(f"Alerts path does not exist - creating: {self.alertsPath}")
            os.mkdir(self.alertsPath)
        self.alertsDataPath = os.path.join(self.alertsPath, self.name)
        if not os.path.exists(self.alertsDataPath):
            print(f"{self.name} alerts data path does not exist - creating: {self.alertsDataPath}")
            os.mkdir(self.alertsDataPath)
        self.timeFormat = "%y%m%d-%H%M%S"
        self.dateTimeFormat = "{:%Y%m%d-%H%M%S}"


    def writeAlertData(self, alert, position):
        # Construct directory name:  YYYYMMDD-hhmmss_Metric_Range_ID/
        trackerName = alert.trackerName.replace(" ", "")
        #timeString = time.strftime(self.timeFormat, time.gmtime(alert.time)) # time.gmtime(alert.time).strftime(self.timeFormat)
        timeString = self.dateTimeFormat.format(alert.time)#.strftime(self.timeFormat, time.gmtime(alert.time)) # time.gmtime(alert.time).strftime(self.timeFormat)
        alertDirName = f"{trackerName}_{timeString}_{alert.alertMetric}_{alert.alertRange}_{alert.id}"
        alertDirPath = os.path.join(self.alertsDataPath, alertDirName)
        idxLo = alert.indices[0]
        idxHi = alert.indices[1]
        csvDataPath = os.path.join(alertDirPath, f"raw_data.csv")
        csvPositionPath = os.path.join(alertDirPath, f"position.csv")
        # New alert or update?
        if os.path.exists(alertDirPath):
            # Alert already exists - update image and data
            print(f"Alert path exists! Updating raw data in {alertDirPath}")
            with open(csvDataPath, 'a', newline='') as csvDataFile:
                writer = csv.writer(csvDataFile)
                # TODO: Ensure proper indices!!
                for i in range(idxLo, idxHi):
                    writer.writerow([self.processing.t[i], self.processing.data[i]])
            with open(csvPositionPath, 'a', newline='') as csvPositionFile:
                writer = csv.writer(csvPositionFile)
                writer.writerow([self.processing.t[i], position[0], position[1], position[2]])
        else:
            # New alert - create new directory and write data
            print(f"Writitng new {self.name} alert data idxs=({idxLo}..{idxHi}) to {alertDirPath}")
            os.mkdir(alertDirPath)
            # Create and write raw data to CSV
            with open(csvDataPath, 'w', newline='') as csvDataFile:
                writer = csv.writer(csvDataFile)
                writer.writerow(["Time", f"{self.name} Data"])
                for i in range(idxLo, idxHi):
                    writer.writerow([self.processing.t[i], self.processing.data[i]])
            with open(csvPositionPath, 'a', newline='') as csvPositionFile:
                writer = csv.writer(csvPositionFile)
                writer.writerow(["Time", "Position-X", "Position-Y", "Position-Z"])
                writer.writerow([self.processing.t[i], position[0], position[1], position[2]])
            

    def alertIO(self, *args):
        #print(f"Alert IO starting - args = {args}")
        while not self.alertIOqueue.empty():
            alert, position = self.alertIOqueue.get()
            self.writeAlertData(alert, position)
            print(f"Writing {self.alertDataType.name} to file - Alert IO in {self.name}! {alert}")
        