import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import os
import datetime
import time
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 1
repeat_length = 30
inter=80 # plot refresh freq

path_to_save = "./results"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=[0,], voltage_ranges=[10,], dec=50, deca=1, srate=6000, output_mode=output_mode)
usb.config_daq()

# Initialize empty lists to store data
x_vals = []
ch1_data = []
#ch2_data = []
first = True
later = time.time()  # Initialize outside to ensure availability

def process_data():
    global first, later
    now = time.time()
    values = usb.collect_data(binary_method)
    if values:
        if first:
            later = now
            first = False 
        x_vals.append(float(now-later))
        ch1_data.append(values[0])
        #ch2_data.append(values[1])

        print(f'Time: {now}, Val 0: {values[0]}') # Val 1: {values[1]}')


# Create a function to update the plot
def update_plot(frame):
       process_data()
       plt.cla()
       if x_vals:  # Check if x_vals is not empty
           plt.plot(x_vals, ch1_data, label='Val 1')
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
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Val1', ]) #'Val2', ])
        for x, s1 in zip(x_vals, ch1_data): # , ch2_data):
            writer.writerow([x, s1])

# Register the callback function for when the plot window is closed
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)

ani = FuncAnimation(fig, update_plot, interval=inter, blit=False)
plt.show()