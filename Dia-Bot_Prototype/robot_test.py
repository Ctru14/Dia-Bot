import sys
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import picamera
import time
import math
import RPi.GPIO as GPIO
import pigpio
import DCMotor
import DualHBridge

print("Python version: " + str(sys.version))
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Script to start camera preview

#camera = picamera.PiCamera()
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
    
def forward():
    print("Moving forward! Speed = " + str(speed.get()))

def backward():
    print("Moving backward! Speed = " + str(speed.get()))
    
def turnRight():
    print("Turn right!")
    
def turnLeft():
    print("Turn left!")
    
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


def cameraRight():
    print("Camera tilt right!")


def cameraLeft():
    print("Camera tilt left!")


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


# GUI SETUP CODE 
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
tk.Button(movementControls, text="^", command=forward, anchor=CENTER, font="16").grid(row=3, column=5)
tk.Button(movementControls, text="v", command=backward, anchor=CENTER, font="16").grid(row=5, column=5)
tk.Button(movementControls, text="<", command=turnLeft, anchor=CENTER, font="16").grid(row=4, column=4)
tk.Button(movementControls, text=">", command=turnRight, anchor=CENTER, font="16").grid(row=4, column=6)

# Stop and lock buttons
tk.Label(movementControls, text="Mode", anchor=CENTER, font="bold").grid(row=2, column=9)
tk.Button(movementControls, text="Stop", command=stopMovement, anchor=CENTER, fg="red", font="16").grid(row=3, column=9)
tk.Button(movementControls, text="Lock", command=lock, anchor=CENTER, font="16").grid(row=5, column=9)

movementControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    movementControls.grid_columnconfigure(i, minsize=20)
    
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
speedScale = tk.Scale(cameraControls, from_=100, to=0, orient=tk.VERTICAL, variable = speed, length=150, showvalue=0, sliderlength=20)
speedScale.grid(row=3, column=8, rowspan=4)
speedScale.set(50)

cameraControls.grid_columnconfigure(1, minsize=10)
for i in range(2,10):
    cameraControls.grid_columnconfigure(i, minsize=20)
    

    
# ----- Other -----

controlFrame.grid_rowconfigure(10, minsize=60)
text = tk.StringVar()
#text.set("Testing the text box!")
label = tk.Label(controlFrame, textvariable=text).grid(row=11, column=1, columnspan=5)

#tk.Button(controlFrame, text="LED On", command=ledOn).grid(row=12, column=3, columnspan=2)
#tk.Button(controlFrame, text="LED Off", command=ledOff).grid(row=12, column=5, columnspan=2)

#tk.Button(controlFrame, text="Forward", command=forward).grid(row=13, column=2)
#tk.Button(controlFrame, text="Backward", command=backward).grid(row=13, column=3)

#tk.Button(controlFrame, text="Motor", command=motorTurnTest).grid(row=14, column=2)
#tk.Button(controlFrame, text="Off", command=stopGpio).grid(row=14, column=3)



# ------------------ Data Pane -----------------------
   # Data pane: Random data and plots
x1 = [0, 1, 2, 3, 4, 5, 6]
y1 = [1, 3, 7, 2, 4, -2, 3]
fig = Figure(figsize=(3,3), dpi=80)
plot1 = fig.add_subplot(111)
plot1.plot(x1, y1)
canvas = FigureCanvasTkAgg(fig, master=dataFrame)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=1, rowspan=3, columnspan=4)
#toolbar = NavigationToolbar2Tk(canvas, dataFrame)
#toolbar.update()
#canvas.get_tk_widget().grid(row=4, column=1, columnspan=4)

#dataFrame.grid_rowconfigure(3, minsize=200)
dataFrame.grid_columnconfigure(5, minsize=200)

tk.Button(dataFrame, text="Sound", command=soundStatus).grid(row=2, column=6)
tk.Button(dataFrame, text="Accel", command=accelerationStatus).grid(row=1, column=7)
tk.Button(dataFrame, text="Accel2", command=accelerationStatus).grid(row=3, column=7)


# ------------------ Video Pane -----------------------
#tk.Button(videoFrame, text="Video", command=videoStatus).grid(row=1, column=1)
img = ImageTk.PhotoImage(Image.open("vanderlandeTest.png"))
imgLabel = Label(videoFrame, image=img)
imgLabel.pack()



# Place the frames
controlFrame.place(relx=0.01, rely=0.01, anchor=tk.NW)
dataFrame.place(relx=0.3, rely=0.01, anchor=tk.NW)
videoFrame.place(x=400, y=270, anchor=tk.NW)




def main():
    #x = threading.Thread(target=update_distance, args=(1,))
    #x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
