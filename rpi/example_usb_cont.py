
import time
import os
import datetime
import pandas as pd
import daq_connectivity as daq

output_mode = 'ascii'
binary_method = 1
i=0

path_to_save = "./results"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(dec=800,deca=3, srate=6000, output_mode=output_mode)
usb.config_daq()

list_of_dict = []
dict_param={}
start_val = 0

while True:
    if start_val>1:
        usb.close_serial()
        #for convenience we convert the list of dict to a dataframe
        date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
        file_path = os.path.join(path_to_save, f'{date_name}.csv')
        df = pd.DataFrame(list_of_dict, columns=list(list_of_dict[0].keys()))
        df.to_csv(path_or_buf=file_path, sep=',',index=False)
        start_val = 0
        time.sleep(0.5)
    try:    
        values = usb.collect_data(binary_method) 
        if values is not None:
            date = datetime.datetime.now()
            dict_param['Frame']=i
            dict_param['Time']=date
            dict_param['Val1']=values[0]
            dict_param['Val2']=values[1]
            dict_param['Val3']=values[2]
            dict_param['Val4']=values[3]
            list_of_dict.append(dict_param.copy())
            print(f'Frame: {i}, Time: {date}, Val 1: {values[0]}, Val 2: {values[1]}, Val 3: {values[2]}, Val 4: {values[3]}')
            i+=1
            start_val = values[0]

    except:
        pass
