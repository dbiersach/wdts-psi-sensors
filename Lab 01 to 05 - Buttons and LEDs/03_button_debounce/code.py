# code.py for Raspberry Pi Pico
# Lab 03_button_debounce
# Read state of external button

import board
import digitalio
import time

# Initialize GPIO pin for INPUT
# Note: Pico's physical pin #20 is mapped to GP15
pin_button = digitalio.DigitalInOut(board.GP15)
pin_button.pull = digitalio.Pull.DOWN

push_count = 0
previously_on = False

while True:
    if pin_button.value:
        if not previously_on:
            push_count += 1
            print(f"Button pressed {push_count} times")
            previously_on = True
    else:
        previously_on = False
        
