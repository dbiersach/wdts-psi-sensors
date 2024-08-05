# code.py for Raspberry Pi Pico
# Lab 02_pwm_led
# Dim external RED LED using PWM

import board
import pwmio
import time

# Initialize GPIO pin for Pulse Width Modulation (PWM)
# Note: Pico's physical pin #20 is mapped to GP15
pin_led = pwmio.PWMOut(board.GP15, frequency=60)

while True:
    # Increase voltage on PWM pin
    for i in range(100):
        pin_led.duty_cycle = int(65535 * i / 100)
        time.sleep(0.01)
    # Decrease voltage on PWM pin    
    for i in range(100):
        pin_led.duty_cycle = int(65535 * (1 - i / 100))
        time.sleep(0.01)

