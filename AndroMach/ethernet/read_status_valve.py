import csv
import matplotlib.pyplot as plt

# Initialize an empty list to store the results
results = []

# Open the CSV file
with open('data.csv', mode='r') as file:
    reader = csv.reader(file)
    
    # Process each row in the CSV file
    for row in reader:
        # Extract the first and the last seven columns and convert them to floats
        selected_columns = [float(row[0])] + [float(val) for val in row[-7:]]
        results.append(selected_columns)

# Convert results to a NumPy array for easier manipulation
import numpy as np
results = np.array(results)

# Assuming the first column is the independent variable
x = results[:, 0]

# Number of subplots (excluding the first column)
num_subplots = results.shape[1] - 1

# Create subplots
fig, axs = plt.subplots(num_subplots, 1, figsize=(10, 20), constrained_layout=True)

# Plot each column against the first column
for i in range(num_subplots):
    axs[i].plot(x, results[:, i+1], marker='o', linestyle='-')
    axs[i].set_title(f'Plot of column {i+2} vs column 1')
    axs[i].set_xlabel('Column 1')
    axs[i].set_ylabel(f'Column {i+2}')

# Show the plots
plt.show()