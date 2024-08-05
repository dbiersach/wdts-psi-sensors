# code.py for Raspberry Pi Pico
# Lab 01_blink_led
# Blink external RED LED

import board
import digitalio
import time

# Initialize GPIO pin for OUTPUT
# Note: Pico's physical pin #20 is mapped to GP15
pin_led = digitalio.DigitalInOut(board.GP15)
pin_led.direction = digitalio.Direction.OUTPUT

while True:
    pin_led.value = True
    time.sleep(0.5)
    pin_led.value = False
    time.sleep(0.5)
