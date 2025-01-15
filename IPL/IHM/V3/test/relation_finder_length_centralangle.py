import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression

# Load the data with space as delimiter
df = pd.read_csv('csv.csv', delimiter=r'\s+', header=None)

# Print the DataFrame to verify its structure
print("DataFrame:")
print(df.head())  # Print first few rows to verify structure

# Print the columns to verify the column count
print("\nColumn Names:")
print(df.columns)

# Extract columns
z1 = df.iloc[:, 0]  # First column
x = df.iloc[:, 2]   # Second column
y = df.iloc[:, 3]   # Third column
z2 = df.iloc[:, 1]  # Fourth column

# Prepare data for polynomial regression
X = np.column_stack((x, y))

# Polynomial regression model for z1
poly = PolynomialFeatures(degree=2)
model_z1 = make_pipeline(poly, LinearRegression())
model_z1.fit(X, z1)
z1_pred = model_z1.predict(X)

# Polynomial regression model for z2
model_z2 = make_pipeline(poly, LinearRegression())
model_z2.fit(X, z2)
z2_pred = model_z2.predict(X)

# Print the polynomial coefficients
print("\nPolynomial Regression Coefficients for z1:")
print("Intercept:", model_z1.named_steps['linearregression'].intercept_)
print("Coefficients:", model_z1.named_steps['linearregression'].coef_)

print("\nPolynomial Regression Coefficients for z2:")
print("Intercept:", model_z2.named_steps['linearregression'].intercept_)
print("Coefficients:", model_z2.named_steps['linearregression'].coef_)

# Function to format polynomial coefficients into an equation string
def format_equation(coefficients):
    intercept = coefficients[0]
    x_coef = coefficients[1]
    y_coef = coefficients[2]
    xy_coef = coefficients[3]
    x2_coef = coefficients[4]
    y2_coef = coefficients[5]
    equation = (f'z = {intercept:.2f} + {x_coef:.2f}*x + {y_coef:.2f}*y + '
                f'{xy_coef:.2f}*x*y + {x2_coef:.2f}*x^2 + {y2_coef:.2f}*y^2')
    return equation

# Create the first 3D plot
fig = plt.figure(figsize=(12, 6))

# First plot: Z1 as the first column
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(x, y, z1, c='r', marker='o', label='Actual z1')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z1')
ax1.set_title('3D Plot with Z1 as First Column')

# Create a grid for plotting the surface
x_grid, y_grid = np.meshgrid(np.linspace(x.min(), x.max(), 100),
                             np.linspace(y.min(), y.max(), 100))
X_grid = np.column_stack((x_grid.ravel(), y_grid.ravel()))
z1_grid = model_z1.predict(X_grid).reshape(x_grid.shape)
ax1.plot_surface(x_grid, y_grid, z1_grid, color='r', alpha=0.5, edgecolor='none')

# Annotate with the polynomial equation for z1
z1_eq = format_equation(model_z1.named_steps['linearregression'].coef_)
ax1.text2D(0.05, 0.95, f'Equation: {z1_eq}', transform=ax1.transAxes, fontsize=12, verticalalignment='top')

# Second plot: Z2 as the first column
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(x, y, z2, c='b', marker='o', label='Actual z2')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z2')
ax2.set_title('3D Plot with Z2 as First Column')

# Create a grid for plotting the surface
z2_grid = model_z2.predict(X_grid).reshape(x_grid.shape)
ax2.plot_surface(x_grid, y_grid, z2_grid, color='b', alpha=0.5, edgecolor='none')

# Annotate with the polynomial equation for z2
z2_eq = format_equation(model_z2.named_steps['linearregression'].coef_)
ax2.text2D(0.05, 0.95, f'Equation: {z2_eq}', transform=ax2.transAxes, fontsize=12, verticalalignment='top')

plt.tight_layout()
plt.show()