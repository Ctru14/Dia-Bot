import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import picamera
import time
import math
from random import *
import RPi.GPIO as GPIO
import pigpio
import DCMotor
import DualHBridge

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# GPIO Startup
gpioMode = GPIO.BOARD
GPIO.setwarnings(False)
GPIO.setmode(gpioMode)
pi = pigpio.pi()


class DataCollection:
    
    def __init__(self, name, units, tkTop, readDataFunction):
        self.name = name
        self.units = units
        self.tkTop = tkTop
        self.readDataFunction = readDataFunction
        self.data = []
        # Create Random Graph
        self.t = list(range(10))
        self.data = [randint(-5, 8) for i in range(10)]
        self.fig = Figure(figsize=(3,2.5), dpi=80)
        self.fig.patch.set_facecolor("#DBDBDB")
        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(self.t, self.data)
        self.plot1.set_ylabel(self.units)
        
        
    def tkAddDataPane(self):
        # Top label
        tk.Label(self.tkTop, text=self.name, font="none 12 bold").grid(row=1, column=1, columnspan=5)
        # Add random graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tkTop)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)
        
        
    def readData(self):
        self.t.append(self.t[-1]+1)
        self.data.append(self.readDataFunction())
        
        
    def updateGraph(self):
        startTime = time.time_ns()
        start = 0
        end = self.t[-1]
        if end > 20:
            start = end-20
        print("Update graph: indices (" + str(start) + ".." + str(end) + ")")
        # self.plot1.cla() # Find way to update graphs without it taking too long!!
        self.plot1.plot(self.t[start:end], self.data[start:end])
        self.canvas.draw()
        totalTimeNs = time.time_ns() - startTime
        print("Update graph: " + str(int(totalTimeNs/1_000_000)) + " ms")
        
    