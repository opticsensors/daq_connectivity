
import os
import datetime
import daq_connectivity as daq 

output_mode = 'binary'
binary_method = 2

path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\daq_connectivity\\logger"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.txt')

usb = daq.Daq_serial(dec=100,deca=3, srate=6000, output_mode=output_mode)
usb.collect_data(file_path, binary_method)