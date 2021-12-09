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

import Positioning

import os
import digitalio
import adafruit_mcp3xxx.mcp3002 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import neopixel

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory


# RPi GPIO Initializations

# GPIO Setup
gpioMode = GPIO.BCM
#gpioMode = GPIO.BOARD
GPIO.setwarnings(False)
GPIO.setmode(gpioMode)
pi = pigpio.pi()
camera = picamera.PiCamera()
cameraMutex = threading.Lock()

pixels = neopixel.NeoPixel(board.D18, 12)

# Motor Pins
motorIn1L = 24
motorIn2L = 23
motorEnL = 25
motorIn1R = 0
motorIn2R = 5
motorEnR = 6

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
        self.factory = PiGPIOFactory()
        self.tilt = Servo(tiltPin, pin_factory=self.factory)
        self.pan = Servo(panPin, min_pulse_width=0.83/1000, max_pulse_width=1.55/1000, pin_factory=self.factory)
        self.pan.mid()
        self.tilt.mid()
        self.tilt_value = 0;
        self.pan_value = 0;
        
    def tiltIncrement(self, num):
        if self.tilt_value < 0.95 and self.tilt_value > -0.95:
            self.tilt_value = self.tilt_value + num
            self.tilt.value = self.tilt_value
        elif self.tilt_value > 0.95 and num < 0:
            self.tilt_value = self.tilt_value + num
            self.tilt.value = self.tilt_value
        elif self.tilt_value < -0.95 and num > 0:
            self.tilt_value = self.tilt_value + num
            self.tilt.value = self.tilt_value
        print(self.tilt_value)

    def panIncrement(self, num):
        if self.pan_value < 0.95 and self.pan_value > -0.95:
            self.pan_value = self.pan_value + num
            self.pan.value = self.pan_value
        elif self.pan_value > 0.95 and num < 0:
            self.pan_value = self.pan_value + num
            self.pan.value = self.pan_value
        elif self.pan_value < -0.95 and num > 0:
            self.pan_value = self.pan_value + num
            self.pan.value = self.pan_value
        print(self.pan_value)

cameraAngle = CameraAngle()

class Accelerometer:

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        time.sleep(0.2)
        self.accelSensor = adafruit_lsm303_accel.LSM303_Accel(self.i2c)

    def readAccData(self):
        accX, accY, accZ = self.accelSensor.acceleration
        return (accX, accY, accZ)

class ADC:

    def __init__(self):
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
        self.cs = digitalio.DigitalInOut(board.D8) # create the cs (chip select)
        self.mcp = MCP.MCP3002(self.spi, self.cs) # create the mcp object

        self.chanTemp = AnalogIn(self.mcp, MCP.P0)# create an analog input channel on pin 0 for temperature
        self.chanSound = AnalogIn(self.mcp, MCP.P1)# create an analog input channel on pin 1 for sound

    def readSoundData(self):
        self.sound = self.chanSound.value
        return (self.sound)
    
    def readTemperatureData(self):
        self.temp = self.chanTemp.value
        return self.temp 

# Closes relevant processes and stops GPIO
def exit():
    GPIO.output(pwm, GPIO.LOW)
    GPIO.cleanup()
    quit()


def stopGpio():
    GPIO.setmode(gpioMode)
    pixels.fill((0, 0, 0))
    GPIO.output(motorEnL, GPIO.LOW)
    GPIO.output(motorEnR, GPIO.LOW)
    GPIO.output(pwmEnL, GPIO.LOW)
    GPIO.output(pwmEnR, GPIO.LOW)
    pwmEnL.stop()
    pwmEnR.stop()
    GPIO.cleanup()

# Opens the camera preview on the screen
#   Note: for VNC users to see the feed, the setting "Enable Direct Capture Mode" must be on
def start_camera(previewWindow=(452,366, 1380, 715), resolution=(1380,715), rotation=0, framerate=15):
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
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed)

        
def moveForwardRightPress(event):
    print(f"Moving forward-right! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.HIGH)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.HIGH)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed/3)


def moveForwardLeftPress(event):
    print(f"Moving forward-left! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.HIGH)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.HIGH)
    pwmEnL.ChangeDutyCycle(speed/3)
    pwmEnR.ChangeDutyCycle(speed)

    
def moveBackwardPress(event):
    print(f"Moving backward! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.HIGH)
    GPIO.output(motorIn1R, GPIO.HIGH)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed)


def moveBackwardRightPress(event):
    print(f"Moving backward-right! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.HIGH)
    GPIO.output(motorIn1R, GPIO.HIGH)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed/3)


def moveBackwardLeftPress(event):
    print(f"Moving backward-left! Press - Speed = {speed}")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.HIGH)
    GPIO.output(motorIn1R, GPIO.HIGH)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed/3)


def moveLeftPress(event):
    print(f"Turn left! Press")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.HIGH)
    GPIO.output(motorIn1R, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.HIGH)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed)
    
    
def moveRightPress(event):
    print(f"Turn right! Press")
    GPIO.output(motorIn1L, GPIO.HIGH)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.HIGH)
    GPIO.output(motorIn2R, GPIO.LOW)
    pwmEnL.ChangeDutyCycle(speed)
    pwmEnR.ChangeDutyCycle(speed)
    

def moveRelease(event):
    print(f"Release movement button")
    pwmEnL.ChangeDutyCycle(0)
    pwmEnR.ChangeDutyCycle(0)
    
def stopMovement():
    print(f"Emergency stop!")
    GPIO.output(motorIn1L, GPIO.LOW)
    GPIO.output(motorIn2L, GPIO.LOW)
    GPIO.output(motorIn2R, GPIO.LOW)
    GPIO.output(motorIn1R, GPIO.LOW)
    pwmEnL.ChangeDutyCycle(0)
    pwmEnR.ChangeDutyCycle(0)
    
def lock():
    print(f"Locking suspension")
    
def ledOn():
    print(f"Turning on LED")
    pixels.fill((255, 255, 255))
    
def ledOff():
    print(f"Turning off LED")
    pixels.fill((0, 0, 0))
    
# Testing purposes only
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
    cameraAngle.tiltIncrement(-0.1)


def cameraDown():
    cameraAngle.tiltIncrement(0.1)


def cameraLeft():
    cameraAngle.panIncrement(0.1)
    
    
def cameraRight():
    cameraAngle.panIncrement(-0.1)

