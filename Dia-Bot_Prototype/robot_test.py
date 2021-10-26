import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import picamera
import time
import threading
import math
from random import *
import RPi.GPIO as GPIO
import pigpio
import DCMotor
import DualHBridge
import DataCollection

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Initialize necessary variables
camera = picamera.PiCamera()
top = tk.Tk()
top.title('Dia-Bot')
led = 11
pwmPinA = 12
motorAIn1 = 15
motorAIn2 = 16
pwmPinB = 19
motorBIn1 = 21
motorBIn2 = 22
motorEn = 18
speed = IntVar()
zoom = IntVar()
#pwmPin2 = 19
gpioMode = GPIO.BOARD
GPIO.setwarnings(False)
GPIO.setmode(gpioMode)
GPIO.setup(led, GPIO.OUT)
#GPIO.setup(pwmPin, GPIO.OUT)
#GPIO.output(pwmPin, GPIO.LOW)
#pwm = GPIO.PWM(pwmPin, 1000) # Frequency=1KHz
#pwm.start(0)
pi = pigpio.pi()
#motorA = DCMotor.DCMotor(pwmPinA, motorAIn1, motorAIn2, motorEn, gpioMode)
motors = DualHBridge.DualHBridge(pwmPinA, motorAIn1, motorAIn2, pwmPinB, motorBIn1, motorBIn2, motorEn, gpioMode)
programRunning = True


# Closes relevant processes
def exit():
    top.destroy
    #camera.stop_preview()
    #camera.close()
    pwm.stop()
    GPIO.output(pwm, GPIO.LOW)
    GPIO.cleanup()
    quit()
    

if not pi.connected:
    print("Error: Pi Not connected")
    exit()
    

# Opens the camera preview on the screen
#   Note: for VNC users to see the feed, the setting "Enable Direct Capture Mode" must be on
#def start_camera():
#    camera.preview_fullscreen=False
#    camera.preview_window=(90,100, 1280, 720)
#    camera.resolution=(1280,720)
#    camera.start_preview()
    
# Callback function for the zoom scroll bar
def setSpeed(var):
    speed = var
    
def moveForwardPress(event):
    print("Moving forward! Press - Speed = " + str(speed.get()))

def moveForwardRelease(event):
    print("Release moving forward")

def moveBackwardPress(event):
    print("Moving backward! Press - Speed = " + str(speed.get()))

def moveBackwardRelease(event):
    print("Release moving backward")

def moveLeftPress(event):
    print("Turn left! Press")
    
def moveLeftRelease(event):
    print("Release moving left")
    
def moveRightPress(event):
    print("Turn right! Press")
    
def moveRightRelease(event):
    print("Release moving right")
    


    
def stopMovement():
    print("Emergency stop!")
    
def lock():
    print("Locking suspension")
    
def ledOn():
    print("Turning on LED")
    GPIO.output(led, True)
    
def ledOff():
    print("Turning off LED")
    GPIO.output(led, False)
    
# Testing purposes only - to be deprecated
def motorTurnTest():
    print("Testing DC motor")
    print("What goes up...")
    for dc in range(0, 101, 2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    time.sleep(1)
    print("...must come down")
    for dc in range(100, -1, -2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    time.sleep(1)
    print("Aaaand backwards")
    for dc in range(0, -101, -2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    print("And back")
    for dc in range(-100, 1, 2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    print("Motor turn done")
    

def cameraUp():
    print("Camera tilt up!")


def cameraDown():
    print("Camera tilt down!")


def cameraLeft():
    print("Camera tilt left!")
    
    
def cameraRight():
    print("Camera tilt right!")


def takePhoto():
    print("Taking photo!")


def soundStatus():
    print("Sound data status")
    
    
def accelerationStatus():
    print("Acceleration data status")
    
    
def videoStatus():
    print("Video status")


def stopGpio():
    GPIO.setmode(gpioMode)
    GPIO.output(motorEn, GPIO.LOW)
    GPIO.output(pwmPinA, GPIO.LOW)
    #pwm.stop()
    GPIO.cleanup()


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


controlFrame.grid(row=1, column=1, sticky="nesw")
dataFrame.grid(row=1, column=2)
videoFrame.grid(row=2, column=2)


# ------------------ Controls Pane -----------------------
# Controls top text
controlsLabel = tk.Label(controlFrame, text="Controls", font="none 18 bold")
controlsLabel.grid(row=1, column=1, columnspan=8)
controlsLabel.config(anchor=CENTER)
controlFrame.grid_rowconfigure(1, minsize=60)

# ----- Movement controls -----
movementControls.grid(row=2, column=1, rowspan=2, columnspan=10)
tk.Label(movementControls, text="Movement", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)

tk.Label(movementControls, text="Speed", anchor=CENTER, font="bold").grid(row=2, column=2)
speedScale = tk.Scale(movementControls, from_=100, to=0, orient=tk.VERTICAL, variable = speed, length=150, showvalue=0, sliderlength=20)
speedScale.grid(row=3, column=2, rowspan=4)
speedScale.set(50)

# Directional buttons
tk.Label(movementControls, text="Direction", anchor=CENTER, font="bold").grid(row=2, column=4, columnspan=3)

moveForwardButton = tk.Button(movementControls, text="^", anchor=CENTER, font="16")
moveForwardButton.bind("<ButtonPress>", moveForwardPress)
moveForwardButton.bind("<ButtonRelease>", moveForwardRelease)
moveForwardButton.grid(row=3, column=5)

moveBackwardButton = tk.Button(movementControls, text="v", anchor=CENTER, font="16")
moveBackwardButton.bind("<ButtonPress>", moveBackwardPress)
moveBackwardButton.bind("<ButtonRelease>", moveBackwardRelease)
top.bind("<KeyPress-Down>", moveBackwardPress)
top.bind("<KeyRelease-Down>", moveBackwardRelease)
moveBackwardButton.grid(row=5, column=5)

moveLeftButton = tk.Button(movementControls, text="<", anchor=CENTER, font="16")
moveLeftButton.bind("<ButtonPress>", moveLeftPress)
moveLeftButton.bind("<ButtonRelease>", moveLeftRelease)
moveLeftButton.grid(row=4, column=4)

moveRightButton = tk.Button(movementControls, text=">", anchor=CENTER, font="16")
moveRightButton.bind("<ButtonPress>", moveRightPress)
moveRightButton.bind("<ButtonRelease>", moveRightRelease)
moveRightButton.grid(row=4, column=6)

# Stop and lock buttons
tk.Label(movementControls, text="Mode", anchor=CENTER, font="bold").grid(row=2, column=9)
tk.Button(movementControls, text="Stop", command=stopMovement, anchor=CENTER, fg="red", font="16").grid(row=3, column=9)
tk.Button(movementControls, text="Lock", command=lock, anchor=CENTER, font="16").grid(row=5, column=9)

movementControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    movementControls.grid_columnconfigure(i, minsize=20)
    
# Keyboard Buttons
top.bind("<KeyPress-w>", moveForwardPress)
top.bind("<KeyRelease-w>", moveForwardRelease)
top.bind("<KeyPress-s>", moveBackwardPress)
top.bind("<KeyRelease-s>", moveBackwardRelease)
top.bind("<KeyPress-a>", moveLeftPress)
top.bind("<KeyRelease-a>", moveLeftRelease)
top.bind("<KeyPress-d>", moveRightPress)
top.bind("<KeyRelease-d>", moveRightRelease)
    
# ----- Camera Controls -----
cameraControls.grid(row=5, column=1, rowspan=1, columnspan=10)
tk.Label(cameraControls, text="Camera", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)

# Directional buttons
tk.Label(cameraControls, text="Angle", anchor=CENTER, font="bold").grid(row=2, column=2, columnspan=3)
tk.Button(cameraControls, text="^", command=cameraUp, anchor=CENTER, font="16").grid(row=3, column=3)
tk.Button(cameraControls, text="v", command=cameraDown, anchor=CENTER, font="16").grid(row=5, column=3)
tk.Button(cameraControls, text="<", command=cameraLeft, anchor=CENTER, font="16").grid(row=4, column=2)
tk.Button(cameraControls, text=">", command=cameraRight, anchor=CENTER, font="16").grid(row=4, column=4)
tk.Button(cameraControls, text="Pic", command=takePhoto, anchor=CENTER, font="16").grid(row=4, column=3)

# Stop and lock buttons
tk.Label(cameraControls, text="Light", anchor=CENTER, font="bold").grid(row=2, column=6)
tk.Button(cameraControls, text="On", command=ledOn, anchor=CENTER, font="16").grid(row=4, column=6)
tk.Button(cameraControls, text="Off", command=ledOff, anchor=CENTER, font="16").grid(row=5, column=6)

tk.Label(cameraControls, text="Zoom", anchor=CENTER, font="bold").grid(row=2, column=8)
zoomScale = tk.Scale(cameraControls, from_=100, to=0, orient=tk.VERTICAL, variable = zoom, length=150, showvalue=0, sliderlength=20)
zoomScale.grid(row=3, column=8, rowspan=4)
zoomScale.set(50)

cameraControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    cameraControls.grid_columnconfigure(i, minsize=20)
    

# Alerts
alertControls.grid(row=7, column=1, rowspan=1, columnspan=10)
tk.Label(alertControls, text="Alerts", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)


tk.Label(alertControls, text="Active", anchor=CENTER, font="none 11").grid(row=2, column=4, columnspan=2)
tk.Label(alertControls, text="Threshold", anchor=CENTER, font="none 11").grid(row=2, column=7, columnspan=2)
tk.Label(alertControls, text="Alerts", anchor=CENTER, font="none 11").grid(row=2, column=10, columnspan=2)

nextRow = 3

def addAlert(name, thresholdUnits):
    global nextRow
    #print("Adding alert row for " + name)
    tk.Label(alertControls, text=name, anchor="w", justify=LEFT, font="none 11").grid(row=nextRow, column=1, columnspan=3)
    tk.Checkbutton(alertControls, text="Enabled", anchor=CENTER, font="none 11").grid(row=nextRow, column=4, columnspan=2)
    tk.Entry(alertControls, justify=CENTER, width=5, font="none 11").grid(row=nextRow, column=6, columnspan=2)
    tk.Label(alertControls, text=thresholdUnits, anchor="w", justify=LEFT, font="none 11").grid(row=nextRow, column=8, columnspan=2)
    if randint(0,1) == 1:
        tk.Label(alertControls, text="Error", anchor=CENTER, font="none 11 bold", fg="red").grid(row=nextRow, column=10, columnspan=2)
    else:
        tk.Label(alertControls, text="None", anchor=CENTER, font="none 11", fg="black").grid(row=nextRow, column=10, columnspan=2)
    nextRow = nextRow + 1
    
    
addAlert("Vibration", "m/s2")
addAlert("Sound", "dB")
addAlert("Temperature", "°C")


alertControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    alertControls.grid_columnconfigure(i, minsize=20)
for i in range(2, nextRow+1):
    alertControls.grid_rowconfigure(i, minsize=30)

    
# ----- Other -----

controlFrame.grid_rowconfigure(10, minsize=60)
text = tk.StringVar()
#text.set("Testing the text box!")
label = tk.Label(controlFrame, textvariable=text).grid(row=11, column=1, columnspan=5)

#tk.Button(controlFrame, text="LED On", command=ledOn).grid(row=12, column=3, columnspan=2)
#tk.Button(controlFrame, text="LED Off", command=ledOff).grid(row=12, column=5, columnspan=2)


#tk.Button(controlFrame, text="Motor", command=motorTurnTest).grid(row=14, column=2)
tk.Button(controlFrame, text="Off", command=stopGpio).grid(row=14, column=3)



# ------------------ Data Pane -----------------------

tk.Label(dataFrame, text="Data", font="none 18 bold").grid(row=1, column=1, columnspan=50)

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
soundLevel = DataCollection.DataCollection("Sound Level", "dB", soundLevelFrame, readSoundLevel)
soundLevel.tkAddDataPane()
soundLevelFrame.grid(row=2, column=1, padx=10)


# Vibration
def readVibration():
    num = randint(-10, 10)
    #print("Reading vibration! - " + str(num))
    return num
vibration = DataCollection.DataCollection("Vibration", "m/s2", vibrationFrame, readVibration)
vibration.tkAddDataPane()
vibrationFrame.grid(row=2, column=2, padx=10)


# Temperature
def readTemperature():
    num = randint(-10, 10)
    #print("Reading temperature! - " + str(num))
    return num
temperature = DataCollection.DataCollection("Temperature", "°C", temperatureFrame, readTemperature)
temperature.tkAddDataPane()
temperatureFrame.grid(row=2, column=3, padx=10)


# Position
def readPosition():
    num = randint(-10, 10)
    #print("Reading position! - " + str(num))
    return num
position = DataCollection.DataCollection("Position", "m", positionFrame, readPosition)
position.tkAddDataPane()
positionFrame.grid(row=2, column=4, padx=10)


dataClassList = [soundLevel, vibration, temperature, position]

# Data pane: Random data and plots
#for i in range(1, len(dataFrames)):
#    unit = units[i]
#    frame = dataFrames[i]
#    x = list(range(10))
#    y = [randint(-5, 8) for i in range(10)]
#    fig = Figure(figsize=(3,2.5), dpi=80)
#    fig.patch.set_facecolor("#DBDBDB")
#    #fig.patch.set_alpha(randint(0,1))
#    plot1 = fig.add_subplot(111)
#    plot1.plot(x, y)
#    plot1.set_xlabel('time')
#    plot1.set_ylabel('unit')
#    canvas = FigureCanvasTkAgg(fig, master=frame)
#    canvas.draw()
#    canvas.get_tk_widget().grid(row=2, column=1, rowspan=3, columnspan=4)
#toolbar = NavigationToolbar2Tk(canvas, dataFrame)
#toolbar.update()
#canvas.get_tk_widget().grid(row=4, column=1, columnspan=4)


# Testing the graph updating

addDataButton = tk.Button(dataFrame, text="Add Data")#, command=forward)
#addDataButton.grid(row=3, column=8, columnspan=2)

def addDataPress(event):
    x = max(x1) + 1
    y = randint(-5, 8)
    x1.append(x)
    y1.append(y)
    plot1.plot(x1, y1)
    canvas.draw()
    print("Adding data! Press - x = " + str(x) + ", y = " + str(y))
    
def addDataRelease(event):
    x = max(x1) + 1
    y = randint(-5, 8)
    x1.append(x)
    y1.append(y)
    plot1.plot(x1, y1)
    canvas.draw()
    print("Adding data! Release - x = " + str(x) + ", y = " + str(y))
    
addDataButton.bind("<ButtonPress>", addDataPress)
addDataButton.bind("<ButtonRelease>", addDataRelease)



# ------------------ Video Pane -----------------------
#tk.Button(videoFrame, text="Video", command=videoStatus).grid(row=1, column=1)
#testImg = ImageTk.PhotoImage(Image.open("vanderlandeTest.png").resize((1000, 500)))
#imgLabel = Label(videoFrame, image=testImg)
#imgLabel.grid(row=1, column=1)


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


# Every data class needs it own graph, data set, and sensor function
def updateData():
    #global dataClassList
    for dataClass in dataClassList:
        dataClass.readData()
    

tk.Button(videoFrame, text="Update Image", command=updateFrameImage).grid(row=2, column=1)


def dataLoop():
    global programRunning
    while programRunning:
        startTime = time.time()
        updateData()
        if programRunning:
            try:
                top.event_generate("<<graphEvent>>")
            except:
                print("Error in event_generate! Unable to update graphs")
        remainingSleep = 1 - (time.time() - startTime)
        time.sleep(remainingSleep if remainingSleep > 0 else 0.5)


def updateGraphsHandler(args):
    for dataClass in dataClassList:
        dataClass.updateGraph()

top.bind("<<graphEvent>>", updateGraphsHandler)


def main():
    global programRunning
    dataThread = threading.Thread(target=dataLoop)#, args=(1,))
    dataThread.start()
    top.mainloop()
    programRunning = False # Stop extra threads


if __name__ == "__main__":
    main()

