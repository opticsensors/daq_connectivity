import os
import datetime
import time
# import pandas as pd
import daq_connectivity as daq 


output_mode = 'binary'
binary_method = 2

path_to_save = "./results"
os.makedirs(path_to_save, exist_ok=True)  # Ensure the results directory exists

date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.csv')

usb = daq.Daq_serial(channels=[0,1,2,3], voltage_ranges=[10, 10,10,10], dec=1000, deca=1, srate=6000, output_mode=output_mode)
usb.config_daq()

list_of_dict = []
dict_param = {}
later = time.time()  # Initialize outside to ensure availability
i = 0

try:
    while True:
        try:    
            values = usb.collect_data(binary_method) 
            now = time.time()
            if values is not None:
                dict_param['Frame'] = i
                dict_param['Time'] = now - later
                dict_param['Val1'] = values[0]
                dict_param['Val2'] = values[1]
                dict_param['Val3'] = values[2]
                dict_param['Val4'] = values[3]
                list_of_dict.append(dict_param.copy())
                print(f'Frame: {i}, Time: {now-later:.4f}, Val 1: {values[0]}, Val 2: {values[1]}, Val 3: {values[2]}, Val 4: {values[3]}')
                i += 1

        except Exception as e:
            print(f"Error collecting data: {e}")
            break

except KeyboardInterrupt:
    print("\nData collection stopped by user.")

finally:
    # Save collected data
    # if list_of_dict:
    #     df = pd.DataFrame(list_of_dict)
    #     df.to_csv(file_path, index=False)
    #     print(f"Data saved to {file_path}")
    
    # Cleanup and close DAQ connection if needed
    try:
        usb.close_serial()  # Assuming there's a close method in your DAQ connectivity class
    except:
        pass