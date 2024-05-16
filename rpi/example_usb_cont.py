import time
import os
import datetime
import pandas as pd
import daq_connectivity as daq

output_mode = 'ascii'
binary_method = 1

path_to_save = "./results"
remote_name = 'test1'
remote_type = 'drive'
in_path = 'results'
out_path = f'{remote_name}:Eurecat'
list_of_remotes = list_remotes()

date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(dec=800, deca=3, srate=6000, output_mode=output_mode)
usb.config_daq()

daq.create_remote(remote_name, remote_type)

i = 0
list_of_dict = []
dict_param = {}
M = False
prev_M = M  # Track the previous state of M

while True:
    values = usb.collect_data(binary_method)
    if values is None:
        continue
    
    trigger = values[0] > 1
    M = trigger  # Set M based on trigger

    if M and not prev_M:
        print("Start recording...")
    
    if M:
        date = datetime.datetime.now()
        dict_param = {
            'Frame': i,
            'Time': date,
            'Val1': values[0],
            'Val2': values[1],
            'Val3': values[2],
            'Val4': values[3]
        }
        list_of_dict.append(dict_param)
        # print(f'Frame: {i}, Time: {date}, Val 1: {values[0]}, Val 2: {values[1]}, Val 3: {values[2]}, Val 4: {values[3]}')
        i += 1

    if not M and prev_M:
        print("Stop recording, saving to CSV...")
        date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
        file_path = os.path.join(path_to_save, f'{date_name}.csv')
        df = pd.DataFrame(list_of_dict)
        df.to_csv(path_or_buf=file_path, sep=',', index=False)
        list_of_dict = []  # Reset the list for the next recording session
        daq.copy_to_remote(in_path, out_path)

    prev_M = M  # Update the previous state of M
