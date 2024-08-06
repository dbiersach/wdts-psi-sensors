# plot_field_strength.py
# Plot magnetic field strength samples
# Fit a curve using  Linear Regression


import json
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# Create a dictionary of existing sample readings
file_name = "field_strength.json"
file_path = Path(__file__).parent / file_name
if not file_path.exists():
    print(f'Missing "{file_name}"')
    sys.exit(0)
with file_path.open("r") as file:
    samples = json.load(file)

# Create NumPy arrays to hold independent and dependent sample values
dist = np.array([float(k) for k in samples.keys()])
field_strength = np.array([float(v) for v in samples.values()])

# Use linear regression (least squares) to fit two polynomials
c2 = np.polyfit(dist, field_strength, 2)
c3 = np.polyfit(dist, field_strength, 3)

# Create smooth arrays to store estimated values
est_x = np.linspace(2, 22, 500)
est_y2 = c2[0] * est_x**2 + c2[1] * est_x + c2[2]
est_y3 = c3[0] * est_x**3 + c3[1] * est_x**2 + c3[2] * est_x + c3[3]

# Plot the sample data and the two polynomials
plt.figure(Path(__file__).name)
plt.scatter(dist, field_strength, color="black")
plt.plot(est_x, est_y2, color="blue", label="Quadratic")
plt.plot(est_x, est_y3, color="red", label="Cubic")
plt.legend()
plt.title("Field Strength vs. Distance")
plt.xlabel("Distance (cm)")
plt.ylabel("Field Strength (uT)")
plt.gca().xaxis.set_major_locator(MultipleLocator(2))
plt.show()
