import time
import board  
import busio
import adafruit_lsm303_accel_edited as adafruit_lsm303_accel
import RPi.GPIO as GPIO
import signal
import sys
import os
import digitalio
import adafruit_mcp3xxx.mcp3002 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import neopixel

# LED
pixels = neopixel.NeoPixel(board.D18, 12)


#accelerometer
print(board.SCL)
print(board.SDA)
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1.0)
print(i2c)
sensor = adafruit_lsm303_accel.LSM303_Accel(i2c)

print(f"SCL: {board.SCL}, SDA: {board.SDA}")

# Camera Motors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
tilt = GPIO.PWM(12, 50)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
pan = GPIO.PWM(13, 50)


# temp & souund sensors
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
cs = digitalio.DigitalInOut(board.D8) # create the cs (chip select)
mcp = MCP.MCP3002(spi, cs) # create the mcp object
chan0 = AnalogIn(mcp, MCP.P0) # create an analog input channel on pin 0 for temperature
chan1 = AnalogIn(mcp, MCP.P1) # create an analog input channel on pin 1 for sound

def remap_range(value, left_min, left_max, right_min, right_max):
    # this remaps a value from original (left) range to new (right) range
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min
    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - left_min) / int(left_span)
    # Convert the 0-1 range into a value in the right range.
    return int(right_min + (valueScaled * right_span))


while True:
    # ACCELERATION
    acc_x, acc_y, acc_z = sensor.acceleration
    #mag_x, mag_y, mag_z = sensor.magnetic
    print('Acceleration (m/s^2): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(acc_x, acc_y, acc_z))
    mag = (acc_x**2 + acc_y**2 + acc_z**2)**(.5) 
    print(f"Magnitude: {mag}")
    #print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag_x, mag_y, mag_z))
    #print('')
    time.sleep(1.0)
    
    # CAMERA MOTORS
    tilt.start(0) #Neutral is somehwere between 8 & 7
    time.sleep(1.0)
    tilt.start(5)
    time.sleep(1.0)
    tilt.start(7)
    time.sleep(1.0)
    
    pan.start(5)
    time.sleep(1.0)
    pan.start(10)
    time.sleep(1.0)
    pan.start(5)
    time.sleep(1.0)
    pan.start(0)
    time.sleep(2.0)
    
    # ADC ITEMS
    # read the temp pin NO SCALING
    temp_raw = chan0.value
    print('Raw Temp ADC Value: ', temp_raw)
    print('ADC Voltage: ' + str(chan0.voltage) + 'V')
    # read the volume pin NO SCALING
    sound_raw = chan1.value
    print('Raw Souund ADC Value: ', sound_raw)
    print('ADC Voltage: ' + str(chan1.voltage) + 'V')
    # read the temp pin NO SCALING
    temp_scaled = temp_raw - 14200
    print('Temp ADC Value SCALED : ', temp_scaled)
    # read the volume pin NO SCALING
    sound_scaled = sound_raw - 32000
    print('Souund ADC Value SCALED: ', sound_scaled)
    # hang out and do nothing for a half second
    time.sleep(1.0)
    
    pixels.fill((255, 255, 255))
    time.sleep(1)
    pixels.fill((255, 0, 0))
    time.sleep(1)
    pixels.fill((255, 255, 0))
    time.sleep(1)
    pixels.fill((0, 255, 0))
    time.sleep(1)
    pixels.fill((0, 0, 255))
    time.sleep(1)
    pixels.fill((0, 0, 0))
    time.sleep(1)