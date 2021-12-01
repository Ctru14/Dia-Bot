import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3002 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D8)

# create the mcp object
mcp = MCP.MCP3002(spi, cs)

# create an analog input channel on pin 0 for temperature
chan0 = AnalogIn(mcp, MCP.P0)
# create an analog input channel on pin 1 for sound
chan1 = AnalogIn(mcp, MCP.P1)


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

