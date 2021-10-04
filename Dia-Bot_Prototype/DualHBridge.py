import time
import math
import RPi.GPIO as GPIO
import pigpio
import DCMotor

class DualHBridge:
    
    def __init__(self, pwmA, in1A, in2A, pwmB, in1B, in2B, en, gpioMode = GPIO.BOARD):
        self.gpioMode = gpioMode
        self.motorA = DCMotor.DCMotor(pwmA, in1A, in2A, en, gpioMode)
        self.motorB = DCMotor.DCMotor(pwmB, in1B, in2B, en, gpioMode)
        
    
    def brake(self):
        self.motorA.brake()
        self.motorB.brake()
        
    def go(self, velo):
        self.motorA.setVelo(velo)
        self.motorB.setVelo(velo)
        
    def stop(self):
        self.motorA.stop()
        self.motorB.stop()
    
        
    