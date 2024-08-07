# plot_rods.py


import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def fit_linear(vec_x, vec_y):
    vec_x = vec_x.reshape(-1, 1)
    model = LinearRegression().fit(vec_x, vec_y)
    m = model.coef_
    b = model.intercept_
    score = model.score(vec_x, vec_y)
    return m, b, score


def fit_quadratic(vec_x, vec_y):
    vec_x = vec_x.reshape(-1, 1)
    transformer = PolynomialFeatures(degree=2, include_bias=False)
    transformer.fit(vec_x)
    vec_x2 = transformer.transform(vec_x)
    model = LinearRegression().fit(vec_x2, vec_y)
    b, a = model.coef_
    c = model.intercept_
    score = model.score(vec_x2, vec_y)
    return a, b, c, score


# Load the data file and parse into columns
counts = np.loadtxt("rods.txt")

# Calculate the number of rods for each reading
# Note that each reading added two more rods
rods = np.arange(len(counts)) * 2 + 2

# Plot the data and two curves fitted to the data
plt.figure("plot_rods.py")
plt.scatter(rods, counts, color="red")
# Fit a straight line
m, b, score = fit_linear(rods, counts)
x = np.linspace(np.min(rods), np.max(rods), 500)
plt.plot(
    x, m * x + b, color="green", linestyle="--", label=f"Linear ($R^2$={score:.4f})"
)
# Fit a quadratic
a, b, c, score = fit_quadratic(rods, counts)
plt.plot(
    x, a * x**2 + b * x + c, color="blue", label=f"Quadratic ($R^2$={score:.4f})"
)
# Decorate the plot with title, axis labels, etc.
plt.title("Decay Events Per Rod")
plt.xlabel("Number of Rods")
plt.ylabel("Number of Events")
plt.legend()
plt.xlim(0, np.max(rods) + 1)
plt.ylim(0)
plt.gca().xaxis.set_major_locator(MultipleLocator(1))
plt.show()
