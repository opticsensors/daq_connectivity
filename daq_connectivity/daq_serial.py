import serial
import serial.tools.list_ports
import time
import struct
import keyboard

class Daq_serial:
    def __init__(self, dec, deca, srate, output_mode):
        self.dec = dec 
        self.deca = deca 
        self.srate = srate
        self.ser = serial.Serial()
        self.output_mode = output_mode

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
            print("Found a DATAQ Instruments device on", hooked_port)
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
            print("Please connect a DATAQ Instruments device")
            input("Press ENTER to try again...")
            return (False)
    
    def config_daq(self, ):

        while self.discovery() == False:
            self.discovery()

        self.ser.write(b"stop\r")            #stop in case device was left scanning

        if self.output_mode == 'ascii':
            self.ser.write(b"eol 1\r")     
            self.ser.write(b"encode 1\r")        #set up the device for ascii mode

        elif self.output_mode == 'binary':
            self.ser.write(b"encode 0\r")

        self.ser.write(b"slist 0 0\r")       #scan list position 0 channel 0 thru channel 7
        self.ser.write(b"slist 1 1\r")
        self.ser.write(b"slist 2 2\r")
        self.ser.write(b"slist 3 3\r")

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

    def collect_data_ascii(self, file_path):
        with open(file_path, 'a') as file:  # Opens the file in append mode
            while True:
                if keyboard.is_pressed('x'):
                    self.ser.write(b"stop\r")
                    time.sleep(1)           
                    self.ser.close()
                    break
                try:
                    i= self.ser.inWaiting()
                    if i>0:
                        line = self.ser.readline().decode("utf-8")
                        print(line, end="\r")
                        file.write(line.rstrip("\r\n") + "\n")  
                except:
                    pass

    def collect_data_binary1(self, file_path):
        
        numofchannel=4 #if you modify the slist, you need modify this accordingly
        numofbyteperscan=2*numofchannel
        
        with open(file_path, 'a') as file:  # Opens the file in append mode
            while True:
                try:
                    if keyboard.is_pressed('x'):    #if key 'x' is pressed, stop the scanning and terminate the program
                        self.ser.write(b"stop\r")
                        time.sleep(1)           
                        self.ser.close()
                        print("Good-Bye")
                        break
                    else:
                        i= self.ser.in_waiting
                        if (i//numofbyteperscan)>0:
                            #we always read in scans
                            response = self.ser.read(i - i%numofbyteperscan)

                            Channel =[]

                            for x in range (0, numofchannel):
                                adc=response[x*2]+response[x*2+1]*256
                                if adc>32767:
                                    adc=adc-65536
                                Channel.append (adc)
                
                            #Print only the first scan for demo purpose
                            print (Channel)
                        pass
                except:
                    pass

    def collect_data_binary2(self, file_path):
        
        numofchannel=4 #if you modify the slist, you need modify this accordingly
        numofbyteperscan=2*numofchannel

        with open(file_path, 'a') as file:  # Opens the file in append mode
            while True:
                if keyboard.is_pressed('x'):
                    self.ser.write(b"stop\r")
                    time.sleep(1)           
                    self.ser.close()
                    break
                try:
                    i= self.ser.in_waiting
                    if (i//numofbyteperscan)>0:
                        #we always read in scans
                        response = self.ser.read(i - i%numofbyteperscan)

                        count=(i - i%numofbyteperscan)//2
                    
                        response2=bytearray(response)
                        
                        Channel=struct.unpack("<"+"h"*count, response2)

                        #print all
                        print (Channel)
                        file.write(Channel.rstrip("\r\n") + "\n")  
                except:
                    pass

    def collect_data(self, file_path, binary_method = 1):
        
        self.config_daq()
        if self.output_mode == 'ascii':
            self.collect_data_ascii(file_path)

        elif self.output_mode == 'binary':
            if binary_method == 1:
                self.collect_data_binary1(file_path)
            elif binary_method == 2:
                self.collect_data_binary2(file_path)