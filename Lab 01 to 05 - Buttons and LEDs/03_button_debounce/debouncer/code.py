# code.py for Raspberry Pi Pico
# Lab 03_button_debounce
# Read state of external button

from adafruit_debouncer import Debouncer

import board
import digitalio
import time

# Initialize GPIO pin for INPUT
# Note: Pico's physical pin #20 is mapped to GP15
pin_button = digitalio.DigitalInOut(board.GP15)
pin_button.pull = digitalio.Pull.DOWN

# Intialize Adafruit Debouncer object
switch = Debouncer(pin_button, interval=0.05)

push_count = 0

while True:
    switch.update()
    if switch.rose:
        push_count += 1
        print(f"Button pressed {push_count} times")
        
