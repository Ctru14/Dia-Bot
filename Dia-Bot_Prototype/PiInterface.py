import sys
import time
import threading
import math
from random import *
import picamera
import RPi.GPIO as GPIO
import pigpio

import board
import busio
import adafruit_lsm303_accel_edited as adafruit_lsm303_accel

import DCMotor
import DualHBridge
import DataCollection

import signal


# RPi GPIO Initializations
#led = 11
#pwmPinA = 12
#motorAIn1 = 15
#motorAIn2 = 16
#pwmPinB = 19
#motorBIn1 = 21
#motorBIn2 = 22
#motorEn = 18
#adcMISO = 35
#adcCS0 = 36
#adcMOSI = 38
#adcSCLK = 40

# GPIO Setup
gpioMode = GPIO.BCM
#gpioMode = GPIO.BOARD
GPIO.setwarnings(False)
GPIO.setmode(gpioMode)
#GPIO.setup(led, GPIO.OUT)
pi = pigpio.pi()
#motors = DualHBridge.DualHBridge(pwmPinA, motorAIn1, motorAIn2, pwmPinB, motorBIn1, motorBIn2, motorEn, gpioMode)
camera = picamera.PiCamera()
cameraMutex = threading.Lock()

# Motor Pins
motorIn1L = 24
motorIn2L = 23
motorEnL = 25
motorIn1R = 0
motorIn2R = 5
motorEnR = 6

def motorGpioSetup():
    GPIO.setup(motorIn1L, GPIO.OUT)
    GPIO.setup(motorIn2L, GPIO.OUT)
    GPIO.setup(motorEnL, GPIO.OUT)
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.LOW)
    pwmEnL=GPIO.PWM(motorEnL, 1000)
    GPIO.setup(motorIn1R, GPIO.OUT)
    GPIO.setup(motorIn2R, GPIO.OUT)
    GPIO.setup(motorEnR, GPIO.OUT)
    GPIO.output(motorIn1R, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnR=GPIO.PWM(motorEnR, 1000)
    
    pwmEnL.start(25)
    pwmEnR.start(25)


# Camera Control
class CameraAngle:

    def __init__(self, tiltPin=12, panPin=13):
        GPIO.setup(tiltPin, GPIO.OUT)
        GPIO.setup(panPin, GPIO.OUT)
        self.tiltDuty = 8
        self.panDuty = 5
        self.tilt = GPIO.PWM(tiltPin, 50)
        self.pan = GPIO.PWM(panPin, 50)
        self.tilt.start(self.tiltDuty)
        self.pan.start(self.panDuty)

    def changeTilt(self, duty):
        self.tiltDuty = duty
        self.tilt.changeDutyCycle(self.tiltDuty)

    def changePan(self, duty):
        self.panDuty = duty
        self.pan.changeDutyCycle(self.panDuty)
        
    def tiltIncrement(self, num):
        self.tiltDuty += num
        self.tilt.changeDutyCycle(self.tiltDuty)

    def panIncrement(self, num):
        self.panDuty += num
        self.pan.changeDutyCycle(self.panDuty)

cameraAngle = CameraAngle()

class Accelerometer:

    def __init__(self):
        #import board
        #import busio
        #import adafruit_lsm303_accel_edited as adafruit_lsm303_accel

        self.i2c = busio.I2C(board.SCL, board.SDA)
        time.sleep(0.2)
        self.accelSensor = adafruit_lsm303_accel.LSM303_Accel(i2c)

    def readAccData(self):
        accX, accY, accZ = sensor.acceleration
        return (accX, accY, accZ)

# Closes relevant processes and stops GPIO
def exit():
    GPIO.output(pwm, GPIO.LOW)
    GPIO.cleanup()
    quit()


def stopGpio():
    GPIO.setmode(gpioMode)
    GPIO.output(motorEn, GPIO.LOW)
    GPIO.output(pwmPinA, GPIO.LOW)
    #pwm.stop()
    GPIO.cleanup()

# Opens the camera preview on the screen
#   Note: for VNC users to see the feed, the setting "Enable Direct Capture Mode" must be on
def start_camera(previewWindow=(452,366, 1380, 715), resolution=(1380,715), rotation=180, framerate=15):
    camera.preview_fullscreen=False
    camera.preview_window=previewWindow
    camera.framerate = framerate
    camera.resolution=resolution
    camera.rotation = rotation
    camera.start_preview()

def captureImage(fileName):
    try:
        cameraMutex.acquire()
        camera.capture(fileName)
        cameraMutex.release()
    except Exception as e:
        print(f"Error capturing camera image: {e}")
    
# Closes camera
def stop_camera():
    camera.stop_preview()
    camera.close()
    

def moveForwardPress(event):
    print(f"Moving forward! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.HIGH)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.HIGH)
    pwmEnL.changeDutyCycle(speed)
    pwmEnR.changeDutyCycle(speed)


def moveForwardRelease(event):
    print(f"Release moving forward")
    pwmEnL.changeDutyCycle(0)
    pwmEnR.changeDutyCycle(0)
    
def moveForwardRightPress(event):
    print(f"Moving forward-right! Press - Speed = {speed}")

def moveForwardRightRelease(event):
    print(f"Release moving forward-right")

def moveForwardLeftPress(event):
    print(f"Moving forward-left! Press - Speed = {speed}")

def moveForwardLeftRelease(event):
    print(f"Release moving forward-left")
    
def moveBackwardPress(event):
    print(f"Moving backward! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.HIGH)
    GPIO.output(motorIn1R, GPIO.HIGH)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnL.changeDutyCycle(speed)
    pwmEnR.changeDutyCycle(speed)

def moveBackwardRelease(event):
    print(f"Release moving backward")
    pwmEnL.changeDutyCycle(0)
    pwmEnR.changeDutyCycle(0)

def moveBackwardRightPress(event):
    print(f"Moving backward-right! Press - Speed = {speed}")

def moveBackwardRightRelease(event):
    print(f"Release moving backward-right")

def moveBackwardLeftPress(event):
    print(f"Moving backward-left! Press - Speed = {speed}")

def moveBackwardLeftRelease(event):
    print(f"Release moving backward-left")

def moveLeftPress(event):
    print(f"Turn left! Press")
    
def moveLeftRelease(event):
    print(f"Release moving left")
    
def moveRightPress(event):
    print(f"Turn right! Press")
    
def moveRightRelease(event):
    print(f"Release moving right")
        
def stopMovement():
    print(f"Emergency stop!")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.LOW)
    pwmEnL.changeDutyCycle(0)
    pwmEnR.changeDutyCycle(0)
    
def lock():
    print(f"Locking suspension")
    
def ledOn():
    print(f"Turning on LED")
    GPIO.output(led, True)
    
def ledOff():
    print(f"Turning off LED")
    GPIO.output(led, False)
    
# Testing purposes only - to be deprecated
def motorTurnTest():
    print(f"Testing DC motor")
    print(f"What goes up...")
    for dc in range(0, 101, 2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    time.sleep(1)
    print(f"...must come down")
    for dc in range(100, -1, -2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    time.sleep(1)
    print(f"Aaaand backwards")
    for dc in range(0, -101, -2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    print(f"And back")
    for dc in range(-100, 1, 2):
        #motor.setVelo(dc)
        motors.go(dc)
        time.sleep(0.05)
    print(f"Motor turn done")
    

def cameraUp():
    cameraAngle.tiltIncrement(1)
    print(f"Camera tilt up! {cameraAngle.tiltDuty}")


def cameraDown():
    cameraAngle.tiltIncrement(-1)
    print(f"Camera tilt down! {cameraAngle.tiltDuty}")


def cameraLeft():
    cameraAngle.panIncrement(-1)
    print(f"Camera tilt left! {cameraAngle.panDuty}")
    
    
def cameraRight():
    cameraAngle.panIncrement(1)
    print(f"Camera tilt right! {cameraAngle.panDuty}")


def takePhoto():
    print(f"Taking photo!")
