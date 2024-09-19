
import os
import datetime
import keyboard
import time
import pandas as pd
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 2

path_to_save = "./results"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=[0,], voltage_ranges=[10, ], dec=800,deca=1, srate=6000, output_mode=output_mode)
usb.config_daq()

list_of_dict = []
dict_param={}
later = time.time()  # Initialize outside to ensure availability
i=0

while True:
    if keyboard.is_pressed('x'):
        usb.close_serial()
        break
    try:    
        values = usb.collect_data(binary_method) 
        now = time.time()
        if values is not None:
            dict_param['Frame']=i
            dict_param['Time']=now-later
            dict_param['Val1']=values[0]
            list_of_dict.append(dict_param.copy())
            print(f'Frame: {i}, Time: {now-later:.4f}, Val 1: {values[0]}')
            i+=1


    except:
        pass

#for convenience we convert the list of dict to a dataframe
df = pd.DataFrame(list_of_dict, columns=list(list_of_dict[0].keys()))
df.to_csv(path_or_buf=file_path, sep=',',index=False)