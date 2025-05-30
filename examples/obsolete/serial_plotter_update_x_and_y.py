import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import datetime
import time
import pandas as pd
import numpy as np
import signal
import sys
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 1
repeat_length = 30
refresh_yaxis_length = 80
yaxis_margin = 1.2
inter=80 # plot refresh freq
channels= [0,1,2,3]
voltage_ranges = [10,10,10,10]

path_to_save = "./results"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=channels, voltage_ranges=voltage_ranges, dec=50, deca=1, srate=6000, output_mode=output_mode)
usb.config_daq()

# Initialize empty lists to store data
x_vals = []
ch_data = [[] for _ in channels]
first = True
later = time.time()  # Initialize outside to ensure availability
counter=0

def process_data():
    global first, later, counter
    values = usb.collect_data(binary_method)
    now = time.time()
    if values:
        if first:
            later = now
            first = False 
        x_vals.append(float(now-later))
        for c,v in zip(ch_data, values):
            c.append(v)
        # for i,v in enumerate(values):
        #     ch_data[i].append(v)
        values_string = ', '.join([f'Val{i}: {v}' for i,v in enumerate(values)])
        print(f'Frame: {counter}, Time: {now-later}, {values_string}')
        counter+=1

def save_data():
    """Save collected data to CSV file"""
    try:
        if x_vals:  # Only save if there's data
            df = pd.DataFrame()
            df['Time'] = x_vals
            for i, ch in enumerate(channels):  # Fixed: use index i instead of ch
                name = f'Val{ch}'
                df[name] = ch_data[i]
            df.to_csv(file_path, index=False)
            print(f"\nData saved to: {file_path}")
            print(f"Total frames collected: {counter}")
        else:
            print("\nNo data to save.")
    except Exception as e:
        print(f"\nError saving data: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    print("\nCtrl+C detected. Saving data and exiting...")
    
    # Save the data
    save_data()
    
    # Close matplotlib windows
    plt.close('all')
    
    # Exit the program
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Create a function to update the plot
def update_plot(frame):
    process_data()
    plt.cla()
    
    if x_vals:  # Check if there's data to plot
        # Plot each channel
        for i, data in enumerate(ch_data):
            plt.plot(x_vals, data, label=f'Val {i}')
        
        plt.xlabel('Time')
        plt.ylabel('Sensor Values')
        plt.legend()

        # Set x-axis limits
        if x_vals[-1] > repeat_length:
            plt.xlim(x_vals[-1] - repeat_length, x_vals[-1])
        else:
            plt.xlim(0, repeat_length)

        # Dynamic y-axis scaling based on recent data
        try:
            y = np.array(ch_data)
            if y.size > 0:  # Check if array is not empty
                # Get the last refresh_yaxis_length points, or all points if fewer available
                y_recent = y[:, -refresh_yaxis_length:] if y.shape[1] >= refresh_yaxis_length else y
                
                if y_recent.size > 0:  # Make sure we have data to work with
                    ymin = yaxis_margin * np.min(y_recent)
                    ymax = yaxis_margin * np.max(y_recent)
                    
                    # Ensure ymin and ymax are different to avoid matplotlib errors
                    if ymin == ymax:
                        ymin -= 1
                        ymax += 1
                    
                    plt.ylim(ymin, ymax)
                else:
                    plt.ylim(-10, 10)  # Default range if no data
            else:
                plt.ylim(-10, 10)  # Default range if no data
        except Exception as e:
            print(f"Warning: Error setting y-axis limits: {e}")
            plt.ylim(-10, 10)  # Fallback to default range
    else:
        # Show waiting message when no data is available
        plt.text(0.5, 0.5, 'Waiting for data...', ha='center', va='center', 
                transform=plt.gca().transAxes)
        plt.xlim(0, repeat_length)
        plt.ylim(-10, 10)

# Create a function to save data to a CSV file when the plot window is closed
def on_close(event):
    save_data()

# Register the callback function for when the plot window is closed
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)

# Add cache_frame_data=False to suppress warning
ani = FuncAnimation(fig, update_plot, interval=inter, blit=False, cache_frame_data=False)

print("Data acquisition started. Press Ctrl+C to save data and exit.")
plt.show()

end=0