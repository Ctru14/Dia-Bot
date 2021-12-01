
""" Display both accelerometer and magnetometer data once per second """

import time
import board  
import busio
#import adafruit_lsm303_accel
import adafruit_lsm303_accel_edited as adafruit_lsm303_accel

print(board.SCL)
print(board.SDA)
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1.0)
print(i2c)
sensor = adafruit_lsm303_accel.LSM303_Accel(i2c)

print(f"SCL: {board.SCL}, SDA: {board.SDA}")

while True:
    acc_x, acc_y, acc_z = sensor.acceleration
    #mag_x, mag_y, mag_z = sensor.magnetic

    print('Acceleration (m/s^2): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(acc_x, acc_y, acc_z))
    mag = (acc_x**2 + acc_y**2 + acc_z**2)**(.5) 
    print(f"Magnitude: {mag}")
    
    #print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag_x, mag_y, mag_z))
    #print('')
    time.sleep(.1)