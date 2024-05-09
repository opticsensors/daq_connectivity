
import os
import datetime
import daq_connectivity as daq 

path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\logger"
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
file_path = os.path.join(path_to_save, f'{date_name}.txt')

usb = daq.USB_connection(dec=512, srate=11718)

usb.collect_data_with_interrupt(file_path)