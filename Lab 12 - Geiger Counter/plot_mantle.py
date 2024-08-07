# plot_mantle.py


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
counts = np.loadtxt("mantle.txt")

# Calculate the distance for each count reading
# Note that each single 1x Lego block is 8mm wide
dist = np.arange(len(counts), 0, -1) * 8 - 8

# Plot the data and two curves fitted to the data
plt.figure("plot_distance.py")
plt.scatter(dist, counts, color="red")
# Fit a straight line
m, b, score = fit_linear(dist, counts)
x = np.linspace(np.min(dist), np.max(dist), 500)
plt.plot(
    x, m * x + b, color="green", linestyle="--", label=f"Linear ($R^2$={score:.4f})"
)
# Fit a quadratic
a, b, c, score = fit_quadratic(dist, counts)
plt.plot(
    x, a * x**2 + b * x + c, color="blue", label=f"Quadratic ($R^2$={score:.4f})"
)
# Decorate the plot with title, axis labels, etc.
plt.title("Decay Events By Distance")
plt.xlabel("Distance (mm)")
plt.ylabel("Number of Events")
plt.legend()
plt.xlim(-1, np.max(dist) + 1)
plt.ylim(0)
plt.gca().xaxis.set_minor_locator(MultipleLocator(2))
plt.show()
