#do not use!! please reference the test_temp_and_mic.py file


'''
import time
import mcp3002 as mcp #

def readPotentiometer():
    global potentiometer
    potentiometer = mcp.readAnalog() #

def main():
    while True: #
        readPotentiometer() #
        print("The current potentiometer value is %i " % potentiometer) #
        time.sleep( 0.5) # s

if __name__ = = "__main__":
    main()
'''
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

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

print('Raw ADC Value: ', chan0.value)
print('ADC Voltage: ' + str(chan0.voltage) + 'V')


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

    # read the analog pin
    trim_pot = chan0.value


    # convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
    set_volume = remap_range(trim_pot, 0, 65535, 0, 65000)

    # set OS volume playback volume
    print('Volume = {volume}%' .format(volume = set_volume))
    set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' . format(volume = set_volume)
    os.system(set_vol_cmd)
    
    # hang out and do nothing for a half second
    time.sleep(0.5)
