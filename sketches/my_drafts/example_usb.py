
import os
import datetime
import keyboard
import time
import pandas as pd
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 2
i=0

path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\daq_connectivity\\logger"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=[0,1], configs=[1280,1], dec=1,deca=1800, srate=6000, output_mode=output_mode)
usb.config_daq()

list_of_dict = []
dict_param={}

while True:
    if keyboard.is_pressed('x'):
        usb.close_serial()
        break
    try:    
        values = usb.collect_data(binary_method) 
        if values is not None:
            time_measurement = time.time()
            dict_param['Frame']=i
            dict_param['Time']=time_measurement
            dict_param['Val1']=values[0]
            dict_param['Val2']=values[1]
            list_of_dict.append(dict_param.copy())
            print(f'Frame: {i}, Time: {time_measurement}, Val 1: {values[0]}, Val 2: {values[1]}')
            i+=1

    except:
        pass

#for convenience we convert the list of dict to a dataframe
df = pd.DataFrame(list_of_dict, columns=list(list_of_dict[0].keys()))
df.to_csv(path_or_buf=file_path, sep=',',index=False)