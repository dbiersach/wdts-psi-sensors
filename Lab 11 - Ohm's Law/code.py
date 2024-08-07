# code.py

VERSION_NUM = 1.2

import adafruit_displayio_sh1107
import adafruit_ina219
import analogio
import asyncio
import board
import busio
import countio
import digitalio
import displayio
import neopixel
import pwmio
import sys
import terminalio
import time

from adafruit_display_text import label
from adafruit_max1704x import MAX17048
from adafruit_lc709203f import LC709203F, PackSize
from adafruit_seesaw.seesaw import Seesaw
from micropython import const

# Initialize I2C bus
i2c_bus = board.I2C()
while not i2c_bus.try_lock():
    pass
i2c_address_list = i2c_bus.scan()
i2c_bus.unlock()

# Initialize battery monitor
battery_monitor = None
if 0x0B in i2c_address_list:
    lc709203 = LC709203F(board.I2C())
    # Update to match the mAh of your battery for more accurate readings.
    # Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
    # Choose the closest match. Include "PackSize." before it, as shown.
    lc709203.pack_size = PackSize.MAH2200
    battery_monitor = lc709203
elif 0x36 in i2c_address_list:
    max17048 = MAX17048(board.I2C())
    battery_monitor = max17048

# Initialize OLED
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c_bus, device_address=0x3C)
display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)
screen = displayio.Group()
display.root_group = screen

# Define Joy Wing's button constants
BUTTON_LEFT = const(9)  # Button A
BUTTON_RIGHT = const(6)  # Button Y
BUTTON_UP = const(10)  # Button X
BUTTON_DOWN = const(7)  # Button B
button_mask = const(
    (1 << BUTTON_RIGHT) | (1 << BUTTON_DOWN) | (1 << BUTTON_LEFT) | (1 << BUTTON_UP)
)

# Initialize Joystick
ss = Seesaw(i2c_bus)
ss.pin_mode_bulk(button_mask, ss.INPUT_PULLUP)

# Initialize Current Sensor
ina219 = adafruit_ina219.INA219(i2c_bus)
ina219.set_calibration_16V_400mA()

# Initialize NeoPixel
pixel_builtin = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel_builtin.brightness = 0.3

# Initialize UART
uart = busio.UART(board.TX, board.RX, baudrate=115200)


def init_screen():
    # Set entire OLED to black
    bg_bitmap = displayio.Bitmap(128, 64, 1)  # One bitmap only
    bg_palette = displayio.Palette(1)  # One color only
    bg_palette[0] = 0x000000  # Black
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    screen.append(bg_sprite)
    # Prepopulate four lines of blank (black) text
    for _ in range(4):
        text_area = label.Label(terminalio.FONT, text="", color=0x000000, x=0, y=0)
        screen.append(text_area)


def display_line(line, text):
    # Overwrite the existing line # of text
    # Only a max of 4 lines fits in the OLED height
    # Only a max of 21 characters per line fits in OLED width
    sy = line * 14
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=sy + 4)
    screen[line] = text_area
    time.sleep(0.01)


def read_buttons():
    buttons = ss.digital_read_bulk(button_mask)
    if not buttons & (1 << BUTTON_LEFT):
        return BUTTON_LEFT
    if not buttons & (1 << BUTTON_RIGHT):
        return BUTTON_RIGHT
    if not buttons & (1 << BUTTON_UP):
        return BUTTON_UP
    if not buttons & (1 << BUTTON_DOWN):
        return BUTTON_DOWN
    return None


def send_cmd(cmd):
    # Append newline character to terminate command
    # Then convert string to bytes() array which is what pySerial expects
    cmd_with_newline = bytes(cmd, "ASCII") + bytes("\n", "ASCII")
    # Send command (Hayes Modem AT format) to device
    uart.write(cmd_with_newline)
    # Read status line from device, convert bytes() to ASCII, and remove whitespace
    status = uart.readline().decode("ASCII").strip()
    return status


async def flash_neopixel(color, interval):
    while True:
        pixel_builtin.fill(color)
        await asyncio.sleep(interval)
        pixel_builtin.fill((0, 0, 0))
        await asyncio.sleep(interval)


async def run_geiger_counter():
    while True:
        task = asyncio.create_task(flash_neopixel((0, 255, 0), 1))  # GREEN
        display_line(0, "Position mantle or")
        display_line(1, "insert welding rods")
        display_line(2, "Press A to start test")
        display_line(3, "or press Y to return")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_RIGHT:  # A to start test
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_LEFT:  # Y to return
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                return

        # Measure decay events from Geiger Counter
        task = asyncio.create_task(flash_neopixel((153, 102, 0), 100))  # YELLOW
        display_line(0, "Counting decay events:")
        display_line(1, "")
        display_line(2, "")
        display_line(3, "")
        num_intervals = 6
        seconds_per_interval = 5
        total_seconds = num_intervals * seconds_per_interval
        counts = []
        for n in range(num_intervals):
            num_seconds = seconds_per_interval
            with countio.Counter(board.A1, edge=countio.Edge.FALL) as pin_tick:
                while num_seconds > 0:
                    await asyncio.sleep(0)
                    display_line(1, f"{total_seconds:2.0f} seconds remain...")
                    total_seconds -= 1
                    num_seconds -= 1
                    time.sleep(1)
                counts.append(pin_tick.count)
            c = sum(counts) / len(counts)  # Average count per interval
            display_line(2, f"Avg Count = {c:,.0f}")
        task.cancel()
        pixel_builtin.fill((0, 0, 0))

        task = asyncio.create_task(flash_neopixel((255, 0, 0), 0.25))  # RED
        display_line(0, "Sampling period done:")
        display_line(1, f"Avg Count = {c:,.0f}")
        display_line(2, "Press A to continue")
        display_line(3, "or press Y to return")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_RIGHT:  # A to continue
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_LEFT:  # Y to return
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                return


async def display_wavelengths(readings):
    # Convert readings to rounded integer wavelenghts
    w = [int(0)] * len(readings)
    for i, v in enumerate(readings):
        w[i] = int(round(v, 2))

    task = asyncio.create_task(flash_neopixel((255, 0, 0), 0.25))  # RED
    display_line(0, "Readings complete.")
    display_line(1, "Press A to cycle thru")
    display_line(2, "measured wavelengths")
    display_line(3, "or press Y to return")
    page = -1
    while True:
        await asyncio.sleep(0)
        button = read_buttons()
        if button == BUTTON_LEFT:  # Y to return
            task.cancel()
            pixel_builtin.fill((0, 0, 0))
            return False
        if button == BUTTON_RIGHT:  # A to page wavelengths
            page += 1
            if page == len(w):
                page = 0
            if page == 0:
                display_line(0, f"410: {w[0]:3d}   510: {w[4]:3d}")
                display_line(1, f"435: {w[1]:3d}   535: {w[5]:3d}")
                display_line(2, f"460: {w[2]:3d}   560: {w[6]:3d}")
                display_line(3, f"485: {w[3]:3d}   585: {w[7]:3d}")
            elif page == 1:
                display_line(0, f"610: {w[8]:3d}   730: {w[12]:3d}")
                display_line(1, f"645: {w[9]:3d}   760: {w[13]:3d}")
                display_line(2, f"680: {w[10]:3d}   810: {w[14]:3d}")
                display_line(3, f"705: {w[11]:3d}   860: {w[15]:3d}")
            elif page == 2:
                display_line(0, f"900: {w[16]:3d}")
                display_line(1, f"940: {w[17]:3d}")
                display_line(2, "Press A to cycle thru")
                display_line(3, "or press Y to return")


async def run_spectrophotometry():
    while True:
        task = asyncio.create_task(flash_neopixel((0, 255, 0), 1))  # GREEN
        display_line(0, "Sample under table?")
        display_line(1, "Isolation lid closed?")
        display_line(2, "Press A to start test")
        display_line(3, "or press Y to return")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_RIGHT:  # A to start test
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_LEFT:  # Y to return
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                return

        task = asyncio.create_task(flash_neopixel((153, 102, 0), 100))  # YELLOW
        display_line(0, "Reading wavelengths:")
        display_line(1, "")
        display_line(2, "")
        display_line(3, "")

        # Configure the sensor per the product's datasheet
        # See https://cdn.sparkfun.com/assets/learn_tutorials/8/3/0/AS7265x_Datasheet.pdf
        send_cmd("ATINTTIME=35")  # Set 100ms integration time
        send_cmd("ATGAIN=2")  # Set gain at 16x

        # Set each of the three LEDs (WHT, IR, NIR) on the sesnor
        # to use a 4mA indicator current and 500 mA driver current
        send_cmd("ATLEDC=0x22")  # WHT (AS72651 sensor)
        send_cmd("ATLEDD=0x22")  # IR  (AS72652 sensor)
        send_cmd("ATLEDE=0x22")  # NIR LED (AS7265 sensor)

        # Turn the blue indicator LED off on the sensor
        # and turn on the other three indicator LEDs
        send_cmd("ATLED0=0")  # Turn off blue indicator
        send_cmd("ATLED1=1")  # Turn on WHT LED
        send_cmd("ATLED2=1")  # Turn on IR LED
        send_cmd("ATLED3=1")  # Turn on NIR LED

        # Create list of 18 floats to hold the sum of each wavelength levels
        total_readings = [0.0] * 18

        # Perform 10 runs of the experiment
        for n in range(1, 11):
            display_line(1, f"{(22 - n * 2):2.0f} seconds remain...")
            # Sleep for two seconds between each run to let sensors settle
            await asyncio.sleep(2)
            status = send_cmd("ATCDATA")  # Now read all 18 wavelength levels
            # All successful commands return a string with "OK" at the end
            # Remove the "OK" then split the CSV string into a list of 18 floats
            readings = [float(s) for s in status.replace("OK", "").split(",")]
            # Accumulate the readings for each wavelength over each run
            for i in range(18):
                total_readings[i] += readings[i]

        # Return Sparkfun Triad Sensor to initial condition
        send_cmd("ATLED1=0")  # Turn on WHT LED
        send_cmd("ATLED2=0")  # Turn on IR LED
        send_cmd("ATLED3=0")  # Turn on NIR LED
        send_cmd("ATLED0=1")  # Turn off blue indicator

        task.cancel()
        pixel_builtin.fill((0, 0, 0))

        # Calculate the average of each frequency level over 10 runs
        # and reorder readings by increasing wavelength
        sensor_readings = [
            readings[i] / 10
            for i in [12, 13, 14, 15, 16, 17, 6, 7, 0, 8, 1, 9, 2, 3, 4, 5, 10, 11]
        ]
        await display_wavelengths(sensor_readings)
    return


async def run_ohms_law():
    while True:
        task = asyncio.create_task(flash_neopixel((0, 255, 0), 1))  # GREEN
        display_line(0, "Connect red wire to")
        display_line(1, "resistor to measure")
        display_line(2, "Press A to start test")
        display_line(3, "or press Y to return")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_RIGHT:  # A to start test
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_LEFT:  # Y to return
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                return

        # Measure current through selected resistor
        task = asyncio.create_task(flash_neopixel((153, 102, 0), 100))  # YELLOW
        num_samples = 100
        display_line(0, "Measuring current:")
        display_line(1, "")
        display_line(2, "")
        display_line(3, "")
        n = num_samples
        c = 0  # Total current
        while n > 0:
            await asyncio.sleep(0)
            c += ina219.current
            display_line(1, f"{n:3.0f} samples remain...")
            n -= 1
        # Calculate average current
        c /= num_samples
        c /= 1000  # Covert from milliamps to amps
        task.cancel()
        pixel_builtin.fill((0, 0, 0))

        task = asyncio.create_task(flash_neopixel((255, 0, 0), 0.25))  # RED
        display_line(0, "!! UNPLUG RED WIRE !!")
        display_line(1, f"Current = {c:0.4f} A")
        display_line(2, "Press A to continue")
        display_line(3, "or press Y to return")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_RIGHT:  # A to continue
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_LEFT:  # Y to return
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                return


async def select_experiment():
    exp_title = ["GEIGER COUNTER", "SPECTROPHOTOMETRY", "OHM'S LAW"]
    exp_num = 1
    while True:
        task = asyncio.create_task(flash_neopixel((0, 0, 255), 1))  # BLUE
        display_line(0, "Cycle the experiments")
        display_line(1, "using the B button...")
        display_line(2, "Select with A button:")
        display_line(3, f"{exp_title[exp_num]}")
        while True:
            await asyncio.sleep(0)
            button = read_buttons()
            if button == BUTTON_DOWN:  # B to cycle
                exp_num += 1
                if exp_num == len(exp_title):
                    exp_num = 0
                display_line(3, f"{exp_title[exp_num]}")
                time.sleep(0.5)
            if button == BUTTON_RIGHT:  # A to start experiment
                task.cancel()
                pixel_builtin.fill((0, 0, 0))
                break
            if button == BUTTON_UP:  # X to get system information
                display_line(0, f"code.py ver: {VERSION_NUM}")
                v = sys.implementation[1]
                display_line(1, f"CP ver: {v[0]}.{v[1]}.{v[2]}")
                display_line(2, f"Battery: {battery_monitor.cell_percent:.1f} %")
                display_line(3, "Press Y to return")
                while True:
                    await asyncio.sleep(0)
                    button = read_buttons()
                    if button == BUTTON_LEFT:  # Y
                        break
                display_line(0, "Cycle the experiments")
                display_line(1, "using the B button...")
                display_line(2, "Select with A button:")
                display_line(3, f"{exp_title[exp_num]}")

        # Start selected experiment
        if exp_num == 0:
            await run_geiger_counter()
        elif exp_num == 1:
            await run_spectrophotometry()
        elif exp_num == 2:
            await run_ohms_law()


async def main():
    init_screen()
    await select_experiment()


asyncio.run(main())
