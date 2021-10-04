import time
import math
import RPi.GPIO as GPIO
import pigpio


class DCMotor:
    
    def __init__(self, pwmPin, in1, in2, en, gpioMode = GPIO.BOARD):
        # Initialize variables
       self.pwmPin = pwmPin
       self.in1 = in1
       self.in2 = in2
       self.en = en
       self.gpioMode = gpioMode
       # Initialize GPIO pins
       self.gpioStart()
       GPIO.output(pwmPin, GPIO.LOW)
       self.pwm = GPIO.PWM(pwmPin, 1000) # Frequency=1KHz
       self.pwm.start(0)
       
    def gpioStart(self):
        # Initialize GPIO pins
       GPIO.setwarnings(False)
       GPIO.setmode(self.gpioMode)
       GPIO.setup(self.in1, GPIO.OUT)
       GPIO.setup(self.in2, GPIO.OUT)
       GPIO.setup(self.en, GPIO.OUT)
       GPIO.setup(self.pwmPin, GPIO.OUT)
       
    def brake(self):
        self.gpioStart()
        GPIO.setmode(self.gpioMode)
        GPIO.output(self.pwmPin, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.HIGH)
       
    def stop(self):
        self.gpioStart()
        GPIO.setmode(self.gpioMode)
        GPIO.output(self.en, GPIO.LOW)
        GPIO.output(self.pwmPin, GPIO.LOW)
        self.pwm.stop()
        GPIO.cleanup()
       
    # Velo [-100, 100]
    def setVelo(self, velo):
        self.gpioStart()
        GPIO.setmode(self.gpioMode)
        # Sets relative motor speed and direction
        if (velo == 1000):
            # Brake if the speed is zero
            self.brake()
        else:
            GPIO.output(self.en, GPIO.HIGH)
            speed = abs(velo) # NOTE: relative speed is capped at 100
            if (speed > 100):
                speed = 100
            # Set direction
            if (velo > 0):
                # Forwards
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.LOW)
            else:
                # Backwards
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.HIGH)
            self.pwm.ChangeDutyCycle(speed)
            #ssself.stop()
            
        
        
        