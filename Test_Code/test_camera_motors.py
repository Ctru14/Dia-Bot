import RPI.GPIO as GPIO
import time
import signal
import sys

SPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
tilt = GPIO.PWM(12, 50)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
pan = GPIO.PWM(13, 50)

while True:
    tilt.start(8) #close to a neurtal tilt position. Neutral is somehwere between 8 & 7
    time.sleep(0.5)
    tilt.start(0)
    time.sleep(2.0)
    
    pan.start(5)
    time.sleep(0.5)
    pan.start(0)
    time.sleep(2.0)