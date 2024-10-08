import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import datetime
import time
import pandas as pd
import numpy as np
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 1
repeat_length = 30
inter=80 # plot refresh freq
channels= [0,]
voltage_ranges = [10,]

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


# Create a function to update the plot
def update_plot(frame):
       process_data()
       plt.cla()
       if x_vals:  # Check if x_vals is not empty
           plt.plot(x_vals, ch_data, label='Val 1')
           plt.xlabel('Time')
           plt.ylabel('Sensor Values')
           plt.legend()

           if x_vals[-1] > repeat_length:
               plt.xlim(x_vals[-1] - repeat_length, x_vals[-1])
           else:
               plt.xlim(0, repeat_length)
       else:
           plt.text(0.5, 0.5, 'Waiting for data...', ha='center', va='center')
           plt.xlim(0, repeat_length)
           plt.ylim(0, 1)

# Create a function to save data to a CSV file when the plot window is closed
def on_close(event):
    df = pd.DataFrame()
    df['Time'] = x_vals
    for ch in channels:
        name = f'Val{ch}'
        df[name] = ch_data[ch]
    df.to_csv(file_path, index=False)

# Register the callback function for when the plot window is closed
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)

ani = FuncAnimation(fig, update_plot, interval=inter, blit=False)
plt.show()

end=0