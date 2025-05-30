import serial
import serial.tools.list_ports
import time
import struct
import logging

class Daq_serial:
    def __init__(self, channels, voltage_ranges, dec, deca, srate, output_mode, ):
        logging.basicConfig(level=logging.INFO)
        self.dec = dec 
        self.deca = deca 
        self.srate = srate
        self.ser = serial.Serial()
        self.output_mode = output_mode
        self.channels = channels
        self.configs = self.voltage_range_to_config(voltage_ranges) 
        self.numofchannel = len(channels) # if you modify the slist, you need modify this accordingly
        self.numofbyteperscan = 2*self.numofchannel

    def voltage_range_to_config(self, voltage_ranges):
        """
        The conversion is done using the value from Analog Measurement Range Table of protocol manual 
        (if same number as channel, max voltage range is applied)
        """
        configs = []
        convesrion_dict = {0.2: '00000101',
                           0.5: '00000100',
                           1:   '00000011',
                           2:   '00000010',
                           5:   '00000001',
                           10:  '00000000',}
        
        for ch, voltage_range in zip(self.channels, voltage_ranges):
            ch_bin = f'{ch:08b}'
            voltage_range_bin = convesrion_dict[voltage_range]
            config = "".join([voltage_range_bin, ch_bin])
            config = int(config, 2)
            configs.append(config)
        return configs

    def discovery(self, ):
        """ 
        Discover DATAQ Instruments devices and models.  Note that if multiple devices are connected, only the 
        device discovered first is used. We leave it to you to ensure that it's the desired device model.
        """
        # Get a list of active com ports to scan for possible DATAQ Instruments devices
        available_ports = list(serial.tools.list_ports.comports())
        # Will eventually hold the com port of the detected device, if any
        hooked_port = ""
        for p in available_ports:
            # Do we have a DATAQ Instruments device?
            if ("VID:PID=0683" in p.hwid):
                # Yes!  Dectect and assign the hooked com port
                hooked_port = p.device
                break

        if hooked_port:
            logging.info(f"Found a DATAQ Instruments device on {hooked_port}")
            if self.output_mode == 'ascii':
                self.ser.timeout = 0
            elif self.output_mode == 'binary':
                self.ser.timeout = 0.5
            self.ser.port = hooked_port
            self.ser.baudrate = '115200'
            self.ser.open()
            return (True)
        else:
            # Get here if no DATAQ Instruments devices are detected
            logging.info("Please connect a DATAQ Instruments device")
            return (False)
    
    def config_daq(self, ):

        while self.discovery() == False:
            self.discovery()
            time.sleep(2)

        self.ser.write(b"stop\r")            #stop in case device was left scanning

        if self.output_mode == 'ascii':
            self.ser.write(b"eol 1\r")     
            self.ser.write(b"encode 1\r")        # set up the device for ascii mode

        elif self.output_mode == 'binary':
            self.ser.write(b"encode 0\r")        # set up the device for binary mode
        
        for ch,config in zip(self.channels, self.configs):
            self.ser.write(f"slist {ch} {config}\r".encode('UTF-8'))

        self.ser.write(f"srate {self.srate}\r".encode('UTF-8')) 
        self.ser.write(f"dec {self.dec}\r".encode('UTF-8')) 
        self.ser.write(f"deca {self.deca}\r".encode('UTF-8')) 

        if self.output_mode == 'ascii':
            time.sleep(1)  
            self.ser.read_all()                  #flush all command responses
            self.ser.write(b"start\r")           #start scanning
        
        elif self.output_mode == 'binary':
            self.ser.write(b"ps 0\r")        #if you modify sample rate, you need modify this accordingly
            time.sleep(0.5)

            while True:
                try:
                    i= self.ser.in_waiting
                    if i>0:
                        response = self.ser.read(i)
                        break
                except:
                    pass
            
            self.ser.reset_input_buffer()
            self.ser.write(b"start\r")       #start scanning

    def collect_data_ascii(self, ):
        i= self.ser.inWaiting()
        if i>0:
            values = self.ser.readline().decode("utf-8")
            values = [float(num.strip()) for num in values.split(',')]
            return values


    def collect_data_binary1(self, ):
        
        i= self.ser.in_waiting
        if (i//self.numofbyteperscan)>0:
            #we always read in scans
            response = self.ser.read(i - i%self.numofbyteperscan)

            Channel = []

            for x in range (0, self.numofchannel):
                adc=response[x*2]+response[x*2+1]*256
                if adc>32767:
                    adc=adc-65536
                Channel.append(adc)
        
            return Channel

    def collect_data_binary2(self, ):
    
        i= self.ser.in_waiting
        if (i//self.numofbyteperscan)>0:
            #we always read in scans
            response = self.ser.read(i - i%self.numofbyteperscan)

            count=(i - i%self.numofbyteperscan)//2
        
            response2=bytearray(response)
            
            Channel=struct.unpack("<"+"h"*count, response2)

            return Channel


    def collect_data(self, binary_method = 1):
        
        if self.output_mode == 'ascii':
            line = self.collect_data_ascii()

        elif self.output_mode == 'binary':
            if binary_method == 1:
                line = self.collect_data_binary1()
            elif binary_method == 2:
                line = self.collect_data_binary2()
        return line

    def close_serial(self):
        self.ser.write(b"stop\r")
        time.sleep(1)           
        self.ser.close()
    