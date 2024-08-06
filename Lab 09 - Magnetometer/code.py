# code.py

# Magnetometer Lab for Pi Pico
# Uses Adafruit MLX90393 Wide Range 3-Axis Magnetometer
# Uses a rare Earth magnet

import adafruit_mlx90393
import analogio
import board
import digitalio
import math
import time
import supervisor
import usb_cdc

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass

# Create USB data port
ser = usb_cdc.data

# Configure I2C bus and Magnetometer
i2c = board.STEMMA_I2C()
mlx = adafruit_mlx90393.MLX90393(i2c, address=0x18, gain=adafruit_mlx90393.GAIN_1X)

# Configure built-in (board) LED
board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT
board_led.value = False


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples(params):
    # Set experiment parameters
    num_samples = int(params[0])
    sensor_delay = float(params[1])

    # Caculate average magnetic field strength over sample period
    field_total = 0.0
    for _ in range(num_samples):
        x, y, z = mlx.magnetic
        field_total += math.sqrt(x**2 + y**2 + z**2)
        time.sleep(sensor_delay)
    field_mean = field_total / num_samples

    # Transfer data over USB
    usb_writeline(field_mean)


while True:
    params = usb_readline().split(",")
    board_led.value = True
    read_samples(params)
    board_led.value = False
