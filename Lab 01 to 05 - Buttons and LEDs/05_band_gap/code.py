# code.py for Raspberry Pi Pico
# Lab 05_band_gap
# Compare forward voltage of RED vs BLUE LEDs
# Uses MCP4725 DAC & 100 Ohm Resistor

import board
import adafruit_mcp4725

# Configure I2C bus
i2c_bus = board.STEMMA_I2C()

# Configure MCP4725 DAC
dac = adafruit_mcp4725.MCP4725(i2c_bus)

# Set DAC output voltage
dac.normalized_value = 1.91 / 3.3