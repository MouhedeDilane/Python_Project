import pandas as pd
import matplotlib.pyplot as plt

# Function to process each CSV file
def process_csv(file_path):
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Apply rolling window average
    df[['PS1', 'PS2', 'PS3']] = df[['PS1', 'PS2', 'PS3']].rolling(window=100, min_periods=1).mean()
    
    # Subtract 0.2 from pressure values
    df[['PS1', 'PS2', 'PS3']] -= 0.2
    
    # Remove rows where pressure values are less than or equal to zero
    df = df[(df['PS1'] > 0) & (df['PS2'] > 0) & (df['PS3'] > 0)]
    
    return df

# List to store processed dataframes
processed_dfs = []

# List of CSV files
csv_files = ['pressure_data_7bar.csv','pressure_data_cooling_0_5bar.csv','pressure_data_cooling_0_55bar.csv',
             'pressure_data_cooling_6bar.csv','pressure_data_cooling_9bar.csv']

# Process each CSV file
for file in csv_files:
    processed_df = process_csv(file)
    processed_dfs.append(processed_df)

# Aligning pressure data to x=0
start_times = [df['time'].min() for df in processed_dfs]

for df, start_time in zip(processed_dfs, start_times):
    df['time'] -= start_time

# Plotting
plt.figure(figsize=(10, 6))

colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'gold', 'black', 'orange', 'purple', 'brown', 'pink', 'gray']
vals=[2,8,3,4,5,8,8.2]
for df,color,val in zip(processed_dfs,colors,vals):
    # Plot PS2 data
    plt.plot(df['time']/1000, df['PS2'], label=f'PS2_{val}bar', color=color)
    # Plot PS3 data
    plt.plot(df['time']/1000, df['PS3'], label=f'PS3_{val}bar', color=color, linestyle='--')

plt.xlabel('Time')
plt.ylabel('Pressure')
plt.title('Pressure Data')
plt.grid(True)
plt.legend()
plt.show()
for df,color,val in zip(processed_dfs,colors,vals):
    # Plot PS2 data
    plt.plot(df['time']/1000, df['PS2']-df['PS3'], label=f'dPS_{val}bar', color=color)

plt.xlabel('Time')
plt.ylabel('Pressure')
plt.title('Pressure Data')
plt.grid(True)
plt.legend()
plt.show()