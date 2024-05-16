import logging
import time
import signal
import os
import numpy as np
import keyboard
import datetime
import daq_connectivity as daq

dataq = daq.Detect_daq_ethernet()
dataq.do_udp_discovery()

# Add command line arguments
date_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
path_to_save = "C:\\Users\\eduard.almar\\OneDrive - EURECAT\\Escritorio\\proyectos\\7. Suricata\\repo\\logger"
file_path = os.path.join(path_to_save, f'{date_name}.txt')

# This maps the IP address of the units to a name used below to configure individual channels
hardware_info = {'Strip_Chart_1': {'ip_address': '192.168.0.80',}, 
                 'Strip_Chart_2': {'ip_address': '192.168.0.81',},}

# This specifies which channels to setup and how to set them up
stripcharts_info = {'Example_Channel_Name_01': {'channel': 6, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_02': {'channel': 7, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1000, 'value_scale': 1}, 
                    'Example_Channel_Name_03': {'channel': 5, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_04': {'channel': 4, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 1000, 'value_scale': 1}, 
                    'Example_Channel_Name_05': {'channel': 7, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_06': {'channel': 6, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 1000, 'value_scale': 1}, 
                    'Example_Channel_Name_07': {'channel': 1, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 0.1, 'value_scale': 1000}, 
                    'Example_Channel_Name_08': {'channel': 0, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1000, 'value_scale': 1}, 
                    'Example_Channel_Name_09': {'channel': 3, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_10': {'channel': 2, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1000, 'value_scale': 1}, 
                    'Example_Channel_Name_11': {'channel': 4, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_12': {'channel': 5, 'strip_chart': 'Strip_Chart_2', 
                                                'daq_scale': 100, 'value_scale': 1}, 
                    'Example_Channel_Name_13': {'channel': 1, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 0.1, 'value_scale': 10000}, 
                    'Example_Channel_Name_14': {'channel': 0, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 100, 'value_scale': 1}, 
                    'Example_Channel_Name_15': {'channel': 3, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 1, 'value_scale': 1000}, 
                    'Example_Channel_Name_16': {'channel': 2, 'strip_chart': 'Strip_Chart_1', 
                                                'daq_scale': 100, 'value_scale': 1}}

# Initialize the class
#print ("stripcharts_info=", stripcharts_info)
dataq = daq.Ethernet_connection(hardware_dict=hardware_info, stripchart_setup_dict=stripcharts_info)

# Add an event handler to run stop_devices function if script is killed
def handler(signum, frame):
    try:
        dataq.stop_devices()
    except:
        pass     # Want to continue to exit if this logic fails
    exit(1)

# Setup a handler for all signals
for i in [x for x in dir(signal) if x.startswith("SIG")]:
    try:
        signum = getattr(signal,i)
        signal.signal(signum,handler)
    except:
        pass

def create_timed_rotating_log(path):
    """
    """
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    
    # Will log to a rotating file for 1 minute, then pinch off up to 5 logs
    handler = logging.handlers.TimedRotatingFileHandler(path, when="m", interval=1, backupCount=5)
    logger.addHandler(handler)
    return logger
    
log = create_timed_rotating_log(file_path)

# Writes to log, creates appropriate nanosecond timestamp
def write_to_log(sequence, duration, logger):
    stop_time = time.time_ns()
    start_time = time.time_ns()-(duration * (10**9))

    time_sequence = np.linspace(start_time, stop_time, len(sequence))
    time_sequence = time_sequence.astype(np.int64)
    time_sequence = time_sequence.tolist()

    send_sequence = []
    for i in range(0,len(sequence)):
        send_sequence.append(sequence[i] + " time_ns=" + str(time_sequence[i]))

    logger.info("\n".join(str(item) for item in send_sequence))

# IF ADC is running, attempt to stop here, wait for disconnect to complete
dataq.stop_devices()
time.sleep(2)

dataq.read_messages()  # Clear out any messages
dataq.do_udp_discovery()
dataq.connect_devices()
dataq.send_setup_commands()
dataq.start()

print("Getting data... (press X to quit)")

# Just read back any information received 
init_time = time.time()
sequences = []
while(True):
    try:
        if keyboard.is_pressed('x' or 'X'):
            dataq.stop_devices()
            print("Bye!")
            break
        else:    
            sequences = sequences + dataq.read_messages(print_data=False, data_type='DQAdcData', \
                                timeout=30,decode=True, expected_count=1)
    except:
        pass

    if len(sequences) > dataq.sample_rate * 8:
        duration = time.time() - init_time
        # print(duration)
        # print("%0.2f S/s/Channel" % (len(sequences) / duration / dataq.connected_count / 8))
        init_time = time.time()

        write_to_log(sequences, duration, logger=log)
        sequences = []