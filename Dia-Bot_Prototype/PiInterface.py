import sys
import time
import threading
import math
from random import *
import picamera
import RPi.GPIO as GPIO
import pigpio
import DCMotor
import DualHBridge
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
gpioMode = GPIO.BOARD
GPIO.setwarnings(False)
GPIO.setmode(gpioMode)
GPIO.setup(led, GPIO.OUT)
pi = pigpio.pi()
motors = DualHBridge.DualHBridge(pwmPinA, motorAIn1, motorAIn2, pwmPinB, motorBIn1, motorBIn2, motorEn, gpioMode)


# Closes relevant processes and stops GPIO
def exit():
    GPIO.output(pwm, GPIO.LOW)
    GPIO.cleanup()
    quit()