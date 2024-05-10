
import os
import datetime
import daq_connectivity as daq 

test_mode = 'simple'
output_mode = 'binary'


path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\daq_connectivity\\logger"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.txt')

if test_mode == 'advanced':
    usb = daq.USB_connection(dec=512, srate=11718)
    usb.collect_data(file_path)

elif test_mode == 'simple':
    usb = daq.USB_connection_simple(dec=100,deca=1, srate=6000, )
    usb.collect_data_simple(file_path, output_mode='binary' ,binary_method=1)