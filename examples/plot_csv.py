import pandas as pd
import matplotlib.pyplot as plt

# Configuration variables
variables_to_plot = ['Val0', 'Val1', 'Val2', 'Val3']  # List of columns to plot
start = 0  # Start time for plotting
end = None  # End time for plotting (None means use last recorded time)

# Load CSV file
csv_file = './results/2025-05-30_12.58.18.231819.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Set end time to last recorded time if not specified
if end is None:
    end = df['Time'].max()

# Filter data based on time range
mask = (df['Time'] >= start) & (df['Time'] <= end)
filtered_df = df[mask]

# Create the plot
plt.figure(figsize=(12, 8))

# Plot each variable
for var in variables_to_plot:
    if var in df.columns:
        plt.plot(filtered_df['Time'], filtered_df[var], label=var, marker='o', markersize=4)
    else:
        print(f"Warning: Column '{var}' not found in CSV file")

# Customize the plot
plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Time Series Plot')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Display plot information
print(f"Plotting time range: {start} to {end}")
print(f"Variables plotted: {[var for var in variables_to_plot if var in df.columns]}")
print(f"Total data points: {len(filtered_df)}")

# Show the plot
plt.show()