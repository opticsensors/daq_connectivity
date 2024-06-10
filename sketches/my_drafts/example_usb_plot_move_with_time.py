import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import os
import datetime
import time
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 2
repeat_length = 5

path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\daq_connectivity\\logger"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=[0,], voltage_ranges=[0.2,], dec=80, deca=3, srate=6000, output_mode=output_mode)
usb.config_daq()

# Initialize empty lists to store data
x_vals = []
ch1_data = []
ch2_data = []
ch3_data = []
ch4_data = []
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

        print(f'Time: {now}, Val 1: {values[0]}')


# Create a function to update the plot
def update_plot(frame):
    process_data()
    plt.cla()
    plt.plot(x_vals, ch1_data, label='Val 1')
    #plt.plot(x_vals, ch2_data, label='Val 2')
    plt.xlabel('Time')
    plt.ylabel('Sensor Values')
    plt.legend()

    if x_vals[-1]>repeat_length:
        lim = plt.xlim(x_vals[-1]-repeat_length, x_vals[-1])
    else:
        lim = plt.xlim(0,repeat_length)

# Create a function to save data to a CSV file when the plot window is closed
def on_close(event):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Val1', 'Val2', 'Val3', 'Val4'])
        for x, s1, s2, s3, s4 in zip(x_vals, ch1_data, ch2_data, ch3_data, ch4_data):
            writer.writerow([x, s1, s2, s3, s4])

# Register the callback function for when the plot window is closed
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)

ani = FuncAnimation(fig, update_plot, interval=100, blit=False)
plt.show()