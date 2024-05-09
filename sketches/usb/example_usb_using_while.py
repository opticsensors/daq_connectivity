import datetime
import os
import daq_connectivity as daq 

path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\logger"
usb = daq.USB_connection(dec=512, srate=11718)


date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')

# This is the slist position pointer. Ranges from 0 (first position) to len(slist)
slist_pointer = 0
# This is the constructed output string
output_string = ""
usb.config_daq()
usb.actuate_daq('start')
while usb.acquiring:
    if (usb.ser.inWaiting() > (2 * len(usb.slist))): # removing this causes PermissionError
        file_path = os.path.join(path_to_save, f'{date_name}.txt')
        with open(file_path, 'a') as file:
            for i in range(len(usb.slist)):
                output_string = usb.read_data(output_string, slist_pointer)
                # Get the next position in slist
                slist_pointer += 1
                if (slist_pointer + 1) > (len(usb.slist)):
                    # End of a pass through slist items...output, reset, continue
                    print(output_string.rstrip(", ") + "           ", end="\r")
                    out = output_string.split(",")
                    # Condition to start recording: V > 1
                    if float(out[0]) > 1:
                        file.write(output_string.rstrip(", ") + "\n")
                        output_string = ""
                        slist_pointer = 0
                    else:
                        output_string = ""
                        slist_pointer = 0
usb.actuate_daq('exit')
