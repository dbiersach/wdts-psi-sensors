# code.py for Raspberry Pi Pico
# Lab 04_neopixel
# Cycle NeoPixel through colors on button press

from adafruit_debouncer import Debouncer

import board
import digitalio
import neopixel
import time

# Initialize GPIO pin for INPUT
# Note: Pico's physical pin #20 is mapped to GP15
pin_button = digitalio.DigitalInOut(board.GP15)
pin_button.pull = digitalio.Pull.DOWN

# Intialize Adafruit Debouncer object
switch = Debouncer(pin_button, interval=0.05)

# Initialize Adafruit NeoPixel object
# Note: Pico's physical pin #21 is mapped to GP16
pixel = neopixel.NeoPixel(board.GP16, 1, brightness=0.25)
# Turn off the NeoPixel off (set its color to BLACK)
pixel[0] = (0, 0, 0)

# Define the color tuplets for RED, GREEN, and BLUE
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

push_count = 0

while True:
    switch.update()
    if switch.rose:
        # Set the neopixel color using push_count as an index into colors list
        pixel[0] = colors[push_count]
        # Increment the push_count but remain within interval [0, 2]
        push_count = (push_count + 1) % 3
        