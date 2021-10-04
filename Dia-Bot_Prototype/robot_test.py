import tkinter as tk
import picamera
import time
import math
import RPi.GPIO as GPIO
import pigpio
import DCMotor
import DualHBridge

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
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
speed = 50
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
    print("Moving forward!")

def backward():
    print("Moving backward!")
    
def turnRight():
    print("Turn right!")
    
def turnLeft():
    print("Turn left!")
    
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


def stopGpio():
    GPIO.setmode(gpioMode)
    GPIO.output(motorEn, GPIO.LOW)
    GPIO.output(pwmPinA, GPIO.LOW)
    #pwm.stop()
    GPIO.cleanup()


# GUI SETUP CODE 
top.resizable(width=False, height=False)
top.geometry("1600x900")

buttonFrame = tk.Frame(top, width=400, height=900)
dataFrame = tk.Frame(top, width=1120, height=270)
videoFrame = tk.Frame(top, width=1120, height=630)

buttonFrame.grid(row=1, column=1, sticky="nesw")
dataFrame.grid(row=1, column=2)
#videoFrame.grid(row=2, column=2)


# Random data
data1 = [[0, 1],
         [1, 3],
         [2, 7],
         [3, 2],
         [4, 4],
         [5, -2],
         [6, 3]]


# Controls Pane
text = tk.StringVar()
text.set("Testing the text box!")
label = tk.Label(buttonFrame, textvariable=text).grid(row=1, column=1, columnspan=4)

tk.Button(buttonFrame, text="LED On", command=ledOn).grid(row=2, column=2)
tk.Button(buttonFrame, text="LED Off", command=ledOff).grid(row=2, column=3)

tk.Button(buttonFrame, text="Forward", command=forward).grid(row=3, column=2)
tk.Button(buttonFrame, text="Backward", command=backward).grid(row=3, column=3)

tk.Button(buttonFrame, text="Motor", command=motorTurnTest).grid(row=4, column=2)
tk.Button(buttonFrame, text="Stop", command=stopGpio).grid(row=4, column=3)

tk.Scale(buttonFrame, from_=99, to=0, orient=tk.VERTICAL, label = "Speed", command=setSpeed, length=280).grid(row=1,column=6, rowspan=3)

# Data Pane
tk.Button(dataFrame, text="test1", command=print("test1")).grid(row=1, column=1)
tk.Button(dataFrame, text="test2", command=print("test2")).grid(row=2, column=5, columnspan=8)

# Video Pane


buttonFrame.place(relx=0.01, rely=0.01, anchor=tk.NW)
dataFrame.place(relx=0.3, rely=0.01, anchor=tk.NW)
#videoFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def main():
    #x = threading.Thread(target=update_distance, args=(1,))
    #x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
