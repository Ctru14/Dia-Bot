import board
import neopixel
import time
pixels = neopixel.NeoPixel(board.D10, 12)
pixels.fill((255, 255, 255))
time.sleep(10)