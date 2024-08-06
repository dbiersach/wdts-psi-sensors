# measure_fields.py
# Read magnetic field strength samples
# Save readings to a JSON file

import adafruit_board_toolkit.circuitpython_serial
import serial
import json
from pathlib import Path
from pprint import pprint


# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Create a dictionary of existing sample readings
file_name = "field_strength.json"
file_path = Path(__file__).parent / file_name
if file_path.exists():
    with file_path.open("r") as file:
        samples = json.load(file)
else:
    # Create an empty dictionary if data file doesn't exist
    samples = {}

# Query the user for current magnet distance
while True:
    try:
        dist = int(input("Current Magnet Distance (2 - 22 cm)? "))
        if 2 <= dist <= 22:
            break
        else:
            print("Please enter an integer between 2 and 22 inclusive.")
    except ValueError:
        print("That is not a valid integer. Please try again.")

# Send parameters and start experiment
num_samples = 25
sensor_delay = 0.1
params = f"{num_samples},{sensor_delay}"
usb_writeline(params)
print("Magnetometer experiment is running...")

# Read from MCU the magnetic field strength
field_str = float(usb_readline())
ser.close()
print(f"Mean Magnetic Field Strength = {field_str:.2f} uT")

# Update the samples dictionary
samples[f"{dist:02d}"] = f"{field_str:.2f}"
samples = {key: samples[key] for key in sorted(samples)}

# Update the JSON datafile
with file_path.open("w") as file:
    json.dump(samples, file, indent=4)

# Display the samples dictionary
print()
print("Updated field_strength.json:")
pprint(samples, width=1)
