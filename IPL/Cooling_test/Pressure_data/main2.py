import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import numpy as np

colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'gold', 'black', 'orange', 'purple', 'brown', 'pink', 'gray']
vals=[2,8,3,4,5,8,8.2]
# Function to process each CSV file
def process_csv(file_path):
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Apply rolling window average
    df[['PS1', 'PS2', 'PS3']] = df[['PS1', 'PS2', 'PS3']].rolling(window=100, min_periods=1).mean()
    
    # Subtract 0.2 from pressure values
    df[['PS1', 'PS2', 'PS3']] -= 0.2
    
    # Remove rows where pressure values are less than or equal to zero
    df = df[(800000<df['time'])&(df['time']<1000000)]
    df = df[(df['PS1'] > 0) & (df['PS2'] > 0) & (df['PS3'] > 0)]

    
    return df

# List to store processed dataframes
processed_dfs = []

# List of CSV files
csv_files = ['pressure_data_cooling_1bar.csv']

# Process each CSV file
for file in csv_files:
    processed_df = process_csv(file)
    processed_dfs.append(processed_df)

# Aligning pressure data to x=0
start_times = [df['time'].min() for df in processed_dfs]

for df, start_time in zip(processed_dfs, start_times):
    df['time'] -= start_time

def rolling_window(data, window):
    weights = np.repeat(1.0, window) / window
    return np.convolve(data, weights, 'valid')

# Iterate through each processed dataframe
for df in processed_dfs:
    # Calculate the derivative of df['PS2'] - df['PS3']
    derivative = np.gradient(df['PS2'] - df['PS3'], df['time'])
    a=rolling_window(derivative,100)
    i=0
    index=[]
    for element in a:
        if np.abs(element) <=0.001:
            index.append(i)
        i+=1
    print(np.abs(df['time'].iloc[min(index)]-df['time'].iloc[max(index)]))
    b=[np.abs(df['PS2'].iloc[_]-df['PS3'].iloc[_]) for _ in range(min(index),max(index)+1)]
    print(np.mean(b))


# Plotting
plt.figure(figsize=(10, 6))

for df,color,val in zip(processed_dfs,colors,vals):
    # Plot PS2 data
    plt.plot(df['time']/1000, df['PS2']-df['PS3'], label=f'dPS_{val}bar', color=color)

plt.xlabel('Time')
plt.ylabel('Pressure')
plt.title('Pressure Data')
plt.grid(True)
plt.legend()
plt.show()