import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import datetime
import time
import pandas as pd
import numpy as np
import signal
import sys
import threading
import queue
from collections import deque
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 1
repeat_length = 80
refresh_yaxis_length = 150
yaxis_margin = 1.2
plot_refresh_interval = 50  # Reduced from 80ms to 50ms for smoother plotting
channels = [0,1,2,3]
voltage_ranges = [10,10,10,10]

# Use deque for efficient data storage (faster than lists for append/pop operations)
max_data_points = 10000  # Limit memory usage
x_vals = deque(maxlen=max_data_points)
ch_data = [deque(maxlen=max_data_points) for _ in channels]

path_to_save = "./results"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=channels, voltage_ranges=voltage_ranges, dec=50, deca=1, srate=6000, output_mode=output_mode)
usb.config_daq()

# Thread-safe data sharing
data_queue = queue.Queue()
stop_acquisition = threading.Event()
first = True
start_time = None
counter = 0

def data_acquisition_thread():
    """Separate thread for continuous data acquisition"""
    global first, start_time, counter
    
    while not stop_acquisition.is_set():
        try:
            values = usb.collect_data(binary_method)
            now = time.time()
            
            if values:
                if first:
                    start_time = now
                    first = False 
                
                timestamp = now - start_time
                
                # Put data in queue for main thread to process
                data_queue.put((timestamp, values))
                
                # Reduced printing frequency to avoid I/O overhead
                if counter % 50 == 0:  # Print every 50th frame instead of every frame
                    values_string = ', '.join([f'Val{i}: {v}' for i,v in enumerate(values)])
                    print(f'Frame: {counter}, Time: {timestamp:.4f}, {values_string}')
                
                counter += 1
        
        except Exception as e:
            print(f"Error in data acquisition: {e}")
            time.sleep(0.001)  # Small delay on error

def process_queued_data():
    """Process all queued data efficiently"""
    processed_count = 0
    while not data_queue.empty() and processed_count < 100:  # Limit processing per update
        try:
            timestamp, values = data_queue.get_nowait()
            x_vals.append(timestamp)
            for i, v in enumerate(values):
                ch_data[i].append(v)
            processed_count += 1
        except queue.Empty:
            break

def save_data():
    """Save collected data to CSV file"""
    try:
        # Process any remaining queued data
        process_queued_data()
        
        if x_vals:
            df = pd.DataFrame()
            df['Time'] = list(x_vals)
            for i, ch in enumerate(channels):
                name = f'Val{ch}'
                df[name] = list(ch_data[i])
            df.to_csv(file_path, index=False)
            print(f"\nData saved to: {file_path}")
            print(f"Total frames collected: {counter}")
        else:
            print("\nNo data to save.")
    except Exception as e:
        print(f"\nError saving data: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    print("\nCtrl+C detected. Stopping acquisition and saving data...")
    
    # Stop the acquisition thread
    stop_acquisition.set()
    
    # Wait a moment for thread to finish
    time.sleep(0.1)
    
    # Save the data
    save_data()
    
    # Close matplotlib windows
    plt.close('all')
    
    # Exit the program
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Optimized plot update function
def update_plot(frame):
    # Process queued data efficiently
    process_queued_data()
    
    if not x_vals:
        # Show waiting message when no data is available
        plt.cla()
        plt.text(0.5, 0.5, 'Waiting for data...', ha='center', va='center', 
                transform=plt.gca().transAxes)
        plt.xlim(0, repeat_length)
        plt.ylim(-10, 10)
        return
    
    # Only clear and redraw if we have new data
    plt.cla()
    
    # Convert deques to numpy arrays for efficient plotting
    x_array = np.array(x_vals)
    
    # Plot each channel
    for i, data in enumerate(ch_data):
        if len(data) > 0:
            y_array = np.array(data)
            plt.plot(x_array, y_array, label=f'Val {i}', linewidth=1)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Sensor Values')
    plt.legend()
    
    # Set x-axis limits
    if x_array[-1] > repeat_length:
        plt.xlim(x_array[-1] - repeat_length, x_array[-1])
    else:
        plt.xlim(0, repeat_length)
    
    # Optimized y-axis scaling
    try:
        if len(ch_data[0]) > 0:
            # Get recent data for all channels
            recent_data = []
            for data in ch_data:
                if len(data) > 0:
                    recent_points = min(refresh_yaxis_length, len(data))
                    recent_data.extend(list(data)[-recent_points:])
            
            if recent_data:
                ymin = yaxis_margin * min(recent_data)
                ymax = yaxis_margin * max(recent_data)
                
                # Ensure ymin and ymax are different
                if abs(ymax - ymin) < 1e-6:
                    ymin -= 1
                    ymax += 1
                
                plt.ylim(ymin, ymax)
            else:
                plt.ylim(-10, 10)
        else:
            plt.ylim(-10, 10)
    except Exception as e:
        print(f"Warning: Error setting y-axis limits: {e}")
        plt.ylim(-10, 10)

def on_close(event):
    """Handle plot window closing"""
    stop_acquisition.set()
    save_data()

# Start the data acquisition thread
acquisition_thread = threading.Thread(target=data_acquisition_thread, daemon=True)
acquisition_thread.start()

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 6))
fig.canvas.mpl_connect('close_event', on_close)

# Create animation with optimized settings
ani = FuncAnimation(fig, update_plot, interval=plot_refresh_interval, 
                   blit=False, cache_frame_data=False)

print("Data acquisition started. Press Ctrl+C to save data and exit.")
print(f"Target sample rate: 6000 Hz ({1000/6000:.2f} ms per sample)")
print(f"Plot refresh rate: {plot_refresh_interval} ms")

plt.tight_layout()
plt.show()

# Clean up
stop_acquisition.set()
if acquisition_thread.is_alive():
    acquisition_thread.join(timeout=1.0)