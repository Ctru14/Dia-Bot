import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import math
import enum
from random import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Dia-Bot specific imports
import DataCollection
import Alerts


piConnected = True
try:
    import PiInterface 
    from PiInterface import PiInterface
except:
    piConnected = False
    print("Error importing PiInterface!")

# Initialize necessary variables
#camera = PiInterface.camera
top = tk.Tk()
top.title('Dia-Bot')
speed = IntVar()
zoom = IntVar()

# Threading control
graphRefreshTime = 5 # Number of seconds between graph refresh
programRunning = True
collectData = False
uiMutex = threading.Lock()
startTime = time.time_ns()


# Closes relevant processes and stops GPIO
def exit():
    top.destroy
    quit()
    
    

# Debugging function - run a function and report how long it takes
def elapsedTime(func, *args):
    startTime = time.time_ns()
    #try:
    #    func(*args)
    #except:
    func()
    elapsedTimeNs = time.time_ns() - startTime
    print("ElapsedTime (" + str(func.__name__) + ") = " + str(elapsedTimeNs / 1_000_000) + " ms")

# Returns a printout of the total time since execution began
def totalElapsedTime():
    global startTime
    return f"(total time = {(time.time_ns()-startTime)/1_000_000_000} s)"

# Opens the camera preview on the screen
#   Note: for VNC users to see the feed, the setting "Enable Direct Capture Mode" must be on
def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(640,500, 1080, 720)
    camera.resolution=(1280,720)
    camera.rotation = 180
    camera.start_preview()


# -------------------------- GUI SETUP CODE --------------------------
top.resizable(width=False, height=False)
top.geometry("1600x900")

# Primary sections
controlFrame = tk.Frame(top, width=400, height=900)#, bg='orange')
dataFrame = tk.Frame(top, width=1120, height=270)#, bg='blue')
videoFrame = tk.Frame(top, width=1120, height=630)#, bg='red')

# Individual Control Frames
movementControls = tk.Frame(controlFrame, width=400, height=280)#, bg='blue')
cameraControls = tk.Frame(controlFrame, width=400, height=280)
alertControls = tk.Frame(controlFrame, width=400, height=280)

# Arrange frames
controlFrame.grid(row=1, column=1, sticky="nesw")
dataFrame.grid(row=1, column=2)
videoFrame.grid(row=2, column=2)


# ------------------ Controls Pane -----------------------
# Controls top text
controlsLabel = tk.Label(controlFrame, text="Controls", font="none 18 bold")#, bg="orange")
controlsLabel.grid(row=1, column=1, columnspan=8)
controlsLabel.config(anchor=CENTER)
controlFrame.grid_rowconfigure(1, minsize=60)

# ----- Movement controls -----
movementControls.grid(row=2, column=1, rowspan=2, columnspan=10)
tk.Label(movementControls, text="Movement", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)

# Speed slider
def speedChanged(event):
    PiInterface.speed=speed.get()
tk.Label(movementControls, text="Speed", anchor=CENTER, font="bold").grid(row=2, column=2)
speedScale = tk.Scale(movementControls, from_=100, to=0, orient=tk.VERTICAL, variable=speed, command=speedChanged, length=150, showvalue=0, sliderlength=20)
speedScale.grid(row=3, column=2, rowspan=4)
speedScale.set(50)

# Directional buttons
tk.Label(movementControls, text="Direction", anchor=CENTER, font="bold").grid(row=2, column=4, columnspan=3)

moveForwardButton = tk.Button(movementControls, text="^", anchor=CENTER, font="16")
moveForwardButton.bind("<ButtonPress>", PiInterface.moveForwardPress)
moveForwardButton.bind("<ButtonRelease>", PiInterface.moveForwardRelease)
#top.bind("<KeyPress-w>", moveForwardPress)
#top.bind("<KeyRelease-w>", moveForwardRelease)
moveForwardButton.grid(row=3, column=5)

moveForwardLeftButton = tk.Button(movementControls, text="FL", anchor=CENTER, font="16")
moveForwardLeftButton.bind("<ButtonPress>", PiInterface.moveForwardLeftPress)
moveForwardLeftButton.bind("<ButtonRelease>", PiInterface.moveForwardLeftRelease)
moveForwardLeftButton.grid(row=3, column=4)

moveForwardRightButton = tk.Button(movementControls, text="FR", anchor=CENTER, font="16")
moveForwardRightButton.bind("<ButtonPress>", PiInterface.moveForwardRightPress)
moveForwardRightButton.bind("<ButtonRelease>", PiInterface.moveForwardRightRelease)
moveForwardRightButton.grid(row=3, column=6)

moveBackwardButton = tk.Button(movementControls, text="v", anchor=CENTER, font="16")
moveBackwardButton.bind("<ButtonPress>", PiInterface.moveBackwardPress)
moveBackwardButton.bind("<ButtonRelease>", PiInterface.moveBackwardRelease)
#top.bind("<KeyPress-s>", moveBackwardPress)
#top.bind("<KeyRelease-s>", moveBackwardRelease)
moveBackwardButton.grid(row=5, column=5)

moveBackwardLeftButton = tk.Button(movementControls, text="BL", anchor=CENTER, font="16")
moveBackwardLeftButton.bind("<ButtonPress>", PiInterface.moveBackwardLeftPress)
moveBackwardLeftButton.bind("<ButtonRelease>", PiInterface.moveBackwardLeftRelease)
moveBackwardLeftButton.grid(row=5, column=4)

moveBackwardRightButton = tk.Button(movementControls, text="BR", anchor=CENTER, font="16")
moveBackwardRightButton.bind("<ButtonPress>", PiInterface.moveBackwardRightPress)
moveBackwardRightButton.bind("<ButtonRelease>", PiInterface.moveBackwardRightRelease)
moveBackwardRightButton.grid(row=5, column=6)

moveLeftButton = tk.Button(movementControls, text="<", anchor=CENTER, font="16")
moveLeftButton.bind("<ButtonPress>", PiInterface.moveLeftPress)
moveLeftButton.bind("<ButtonRelease>", PiInterface.moveLeftRelease)
#top.bind("<KeyPress-a>", moveLeftPress)
#top.bind("<KeyRelease-a>", moveLeftRelease)
moveLeftButton.grid(row=4, column=4)

moveRightButton = tk.Button(movementControls, text=">", anchor=CENTER, font="16")
moveRightButton.bind("<ButtonPress>", PiInterface.moveRightPress)
moveRightButton.bind("<ButtonRelease>", PiInterface.moveRightRelease)
moveRightButton.grid(row=4, column=6)

# Stop and lock buttons
tk.Label(movementControls, text="Mode", anchor=CENTER, font="bold").grid(row=2, column=9)
tk.Button(movementControls, text="Stop", command=PiInterface.stopMovement, anchor=CENTER, fg="red", font="16").grid(row=3, column=9)
tk.Button(movementControls, text="Lock", command=PiInterface.lock, anchor=CENTER, font="16").grid(row=5, column=9)

movementControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    movementControls.grid_columnconfigure(i, minsize=20)
    
# Keyboard Buttons
top.bind("<KeyPress-w>", PiInterface.moveForwardPress)
top.bind("<KeyRelease-w>", PiInterface.moveForwardRelease)
top.bind("<KeyPress-s>", PiInterface.moveBackwardPress)
top.bind("<KeyRelease-s>", PiInterface.moveBackwardRelease)
top.bind("<KeyPress-a>", PiInterface.moveLeftPress)
top.bind("<KeyRelease-a>", PiInterface.moveLeftRelease)
top.bind("<KeyPress-d>", PiInterface.moveRightPress)
top.bind("<KeyRelease-d>", PiInterface.moveRightRelease)
    
# ----- Camera Controls -----
cameraControls.grid(row=5, column=1, rowspan=1, columnspan=10)
tk.Label(cameraControls, text="Camera", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)

# Directional buttons
tk.Label(cameraControls, text="Angle", anchor=CENTER, font="bold").grid(row=2, column=2, columnspan=3)
tk.Button(cameraControls, text="^", command=PiInterface.cameraUp, anchor=CENTER, font="16").grid(row=3, column=3)
tk.Button(cameraControls, text="v", command=PiInterface.cameraDown, anchor=CENTER, font="16").grid(row=5, column=3)
tk.Button(cameraControls, text="<", command=PiInterface.cameraLeft, anchor=CENTER, font="16").grid(row=4, column=2)
tk.Button(cameraControls, text=">", command=PiInterface.cameraRight, anchor=CENTER, font="16").grid(row=4, column=4)
tk.Button(cameraControls, text="Pic", command=PiInterface.takePhoto, anchor=CENTER, font="16").grid(row=4, column=3)

# Stop and lock buttons
tk.Label(cameraControls, text="Light", anchor=CENTER, font="bold").grid(row=2, column=6)
tk.Button(cameraControls, text="On", command=PiInterface.ledOn, anchor=CENTER, font="16").grid(row=4, column=6)
tk.Button(cameraControls, text="Off", command=PiInterface.ledOff, anchor=CENTER, font="16").grid(row=5, column=6)

# Zoom slider
tk.Label(cameraControls, text="Zoom", anchor=CENTER, font="bold").grid(row=2, column=8)
zoomScale = tk.Scale(cameraControls, from_=100, to=0, orient=tk.VERTICAL, variable = zoom, length=150, showvalue=0, sliderlength=20)
zoomScale.grid(row=3, column=8, rowspan=4)
zoomScale.set(50)

cameraControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    cameraControls.grid_columnconfigure(i, minsize=20)
    

# ----- Alerts -----
alertControls.grid(row=7, column=1, rowspan=1, columnspan=10)
tk.Label(alertControls, text="Alerts", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)


tk.Label(alertControls, text="Type", anchor=CENTER, font="none 11").grid(row=2, column=4, columnspan=2)
tk.Label(alertControls, text="Threshold", anchor=CENTER, font="none 11").grid(row=2, column=7, columnspan=2)
tk.Label(alertControls, text="Alerts", anchor=CENTER, font="none 11").grid(row=2, column=10, columnspan=2)


    
# Create each alert instance and add frames to the UI  
vibrationAlert = Alerts.Alert(alertControls, "Vibration", "m/s2", Alerts.Alert.AlertType.Above)
soundAlert = Alerts.Alert(alertControls, "Sound", "dB", Alerts.Alert.AlertType.Above)
temperatureAlert = Alerts.Alert(alertControls, "Temperature", "°C", Alerts.Alert.AlertType.Between)


alerts = [vibrationAlert, soundAlert, temperatureAlert]
nextAlertRow = 3
for alert in alerts:
    alert.getAlertFrame().grid(row=nextAlertRow, column=1, columnspan = 10)
    nextAlertRow = nextAlertRow + 1


# Press this button to confirm and lock in Alert changes
def updateAlerts():
    for alert in alerts:
        alert.confirmUpdates()
confirmButton = tk.Button(alertControls, text="Confirm", command=updateAlerts)#, state=DISABLED) #TODO: enable/disable the button for updates
confirmButton.grid(row=nextAlertRow, column=8, columnspan=2)


alertControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    alertControls.grid_columnconfigure(i, minsize=20)
for i in range(2, nextAlertRow+1):
    alertControls.grid_rowconfigure(i, minsize=30)

    
# ----- Other -----

# Testing buttons
tk.Button(controlFrame, text="Motor", command=PiInterface.motorTurnTest).grid(row=14, column=2)
tk.Button(controlFrame, text="Off", command=PiInterface.stopGpio).grid(row=14, column=3)


def toggleData():
    global collectData
    collectData = not collectData
    print(f"Setting colletData to {collectData}")

# ------------------ Data Pane -----------------------
tk.Label(dataFrame, text="Data", font="none 18 bold").grid(row=1, column=1, columnspan=50)
tk.Button(dataFrame, text="Toggle Data", command=toggleData).grid(row=1, column=2)

# Individual Frames
soundLevelFrame = tk.Frame(dataFrame, width=350, height=350)#, bg="red")
vibrationFrame = tk.Frame(dataFrame, width=350, height=350)#, bg="yellow")
temperatureFrame = tk.Frame(dataFrame, width=350, height=350)#, bg="orange")
positionFrame = tk.Frame(dataFrame, width=350, height=350)#, bg="green")
dataFrames = [soundLevelFrame, vibrationFrame, temperatureFrame, positionFrame]
units = ["dB", "m/s2", "C", "m"]


# Sound Level
def readSoundLevel():
    num = randint(-10, 10)
    #print("Reading sound level! - " + str(num))
    return num
soundLevel = DataCollection.DataCollection("Sound Level", "dB", soundLevelFrame, readSoundLevel, uiMutex, startTime)
soundLevel.tkAddDataPane()
soundLevelFrame.grid(row=2, column=1, padx=10)


# Vibration
def readVibration():
    num = randint(-10, 10)
    #print("Reading vibration! - " + str(num))
    return num
vibration = DataCollection.DataCollection("Vibration", "m/s2", vibrationFrame, readVibration, uiMutex, startTime)
vibration.tkAddDataPane()
vibrationFrame.grid(row=2, column=2, padx=10)


# Temperature
def readTemperature():
    num = randint(-10, 10)
    #print("Reading temperature! - " + str(num))
    return num
temperature = DataCollection.DataCollection("Temperature", "�C", temperatureFrame, readTemperature, uiMutex, startTime)
temperature.tkAddDataPane()
temperatureFrame.grid(row=2, column=3, padx=10)


# Position
def readPosition():
    num = randint(-10, 10)
    #print("Reading position! - " + str(num))
    return num
position = DataCollection.DataCollection("Position", "m", positionFrame, readPosition, uiMutex, startTime)
position.tkAddDataPane()
positionFrame.grid(row=2, column=4, padx=10)


# Group of all the data classes
dataClassList = [soundLevel, vibration, temperature, position]



# ------------------ Video Pane -----------------------
#tk.Button(videoFrame, text="Video", command=videoStatus).grid(row=1, column=1)
testImg = ImageTk.PhotoImage(Image.open("vanderlandeTest.png"))#.resize((1000, 500)))
imgLabel = Label(videoFrame, image=testImg)
imgLabel.grid(row=1, column=1)


def updateFrameImage():
    fileName = "frame.png"
    camera.capture(fileName)
    img = ImageTk.PhotoImage(Image.open(fileName).resize((1000, 500)))
    imgLabel = Label(videoFrame, image=img)
    imgLabel.grid(row=1, column=1)



# Place the frames
controlFrame.place(relx=0.01, rely=0.01, anchor=tk.NW)
dataFrame.place(relx=0.3, rely=0.01, anchor=tk.NW)
videoFrame.place(x=400, y=300, anchor=tk.NW)

# ----- Threading functions -----

# Wrapper to other functions which loops 
def loopAtFrequency(freqHz, loopFunction, *args):
    global programRunning
    loopTime = 1/freqHz
    while programRunning:
        loopStartTime = time.time()
        loopFunction(*args)
        loopEndTime = time.time()
        loopTimeTaken = loopEndTime - loopStartTime
        timeRemaining = loopTime - (loopTimeTaken)
        if timeRemaining > 0:
            time.sleep(timeRemaining)
        else:
            print(f"Thread {loopFunction.__name__} took longer to execute ({loopTimeTaken} s) than its given time({loopTimeTaken} s)! Assigning 1s sleep")
            time.sleep(1)


# Every data class needs it own graph, data set, and sensor function
def updateData():
    global collectData
    if collectData:
        for dataClass in dataClassList:
            dataClass.readData()


#tk.Button(videoFrame, text="Update Image", command=updateFrameImage).grid(row=2, column=1)

def updateGraphs():
    global collectData
    if collectData:
        try:
            top.event_generate("<<graphEvent>>")
        except:
            print("Error in event_generate! Unable to update graphs")

def updateGraphsWrapper(event):
    elapsedTime(updateGraphsHandler)

def updateGraphsHandler():
    global startTime
    global loopCount
    for dataClass in dataClassList:
        dataClass.updateGraph()
    # Threading version
    #threads = []
    #for dataClass in dataClassList:
    #    print(f"Start threads: {dataClass.name} Loop #{loopCount} {totalElapsedTime()}")
    #    newThread = threading.Thread(target=dataClass.updateGraph, args=(loopCount,))
    #    newThread.start()
    #    threads.append(newThread)
    #print(f"Started threads Loop #{loopCount} {totalElapsedTime()} ")
    #print("Join threads.. " + str(threads))
    #for t in threads:
    #    t.join()
    #print("Completed joining")    
        

top.bind("<<graphEvent>>", updateGraphsWrapper)

def printTime(*args):
    print(totalElapsedTime())

def main():
    global programRunning
    global startTime
    
    # Create additional threads
    dataThread = threading.Thread(target=loopAtFrequency, args=(1, updateData))
    graphThread = threading.Thread(target=loopAtFrequency, args=(1/graphRefreshTime, updateGraphs))
    
    # Start threads
    dataThread.start()
    graphThread.start()
    
    #start_camera()
        
    #totalTimeNs = time.time_ns() - startTime
    #print("Start thread time: " + str((totalTimeNs/1_000_000)) + " ms")
    top.mainloop()
    programRunning = False # Stop extra threads


if __name__ == "__main__":
    main()

