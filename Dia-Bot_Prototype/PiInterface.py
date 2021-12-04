import sys
import time
import threading
import math
from random import *
#import picamera
#import RPi.GPIO as GPIO
#import pigpio
#import DCMotor
#import DualHBridge
import DataCollection


# RPi GPIO Initializations
led = 11
pwmPinA = 12
motorAIn1 = 15
motorAIn2 = 16
pwmPinB = 19
motorBIn1 = 21
motorBIn2 = 22
motorEn = 18
adcMISO = 35
adcCS0 = 36
adcMOSI = 38
adcSCLK = 40
#gpioMode = GPIO.BOARD
#GPIO.setwarnings(False)
#GPIO.setmode(gpioMode)
#GPIO.setup(led, GPIO.OUT)
#pi = pigpio.pi()
#motors = DualHBridge.DualHBridge(pwmPinA, motorAIn1, motorAIn2, pwmPinB, motorBIn1, motorBIn2, motorEn, gpioMode)
#camera = picamera.PiCamera()


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
def start_camera(previewWindow=(452,366, 1380, 715), resolution=(1380,715), rotation=180):
    camera.preview_fullscreen=False
    camera.preview_window=previewWindow
    camera.resolution=resolution
    camera.rotation = rotation
    camera.start_preview()

def captureImage(fileName):
    camera.capture(fileName)
    
# Closes camera
def stop_camera():
    camera.stop_preview()
    camera.close()
    
    

def moveForwardPress(event):
    print(f"Moving forward! Press - Speed = {speed}")

def moveForwardRelease(event):
    print(f"Release moving forward")
    
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

def moveBackwardRelease(event):
    print(f"Release moving backward")

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
    print(f"Camera tilt up!")


def cameraDown():
    print(f"Camera tilt down!")


def cameraLeft():
    print(f"Camera tilt left!")
    
    
def cameraRight():
    print(f"Camera tilt right!")


def takePhoto():
    print(f"Taking photo!")
