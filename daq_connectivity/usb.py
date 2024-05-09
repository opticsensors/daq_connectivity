import serial
import serial.tools.list_ports
import time
import os
import datetime
import signal
import sys

class USB_connection:
    def __init__(self, dec, srate, slist=None, analog_ranges=None, rate_ranges=None):

        self.dec = dec 
        self.srate = srate
        if slist is None:
            self.slist = [0x0000,0x0001,0x0002,0x0003]
        else:
            self.slist = slist

        if analog_ranges is None:
            # Analog ranges for model DI-4108
            self.analog_ranges = tuple((10,5,2,1,0.5,0.2))
        else:
            self.analog_ranges = analog_ranges

        if rate_ranges is None:
            # Define a tuple that contains an ordered list of rate measurement ranges supported by the hardware. 
            # The first item in the list is the lowest gain code (e.g. 50 kHz range = gain code 1).
            self.rate_ranges = tuple((50000,20000,10000,5000,2000,1000,500,200,100,50,20,10))
        else:
            self.rate_ranges = rate_ranges

        # This is a list of analog and rate ranges to apply in slist order
        self.range_table = list(())
        self.ser = serial.Serial()
        # Define flag to indicate if acquiring is active
        self.acquiring = False

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
            self.ser.timeout = 0
            self.ser.port = hooked_port
            self.ser.baudrate = '115200'
            self.ser.open()
            return (True)
        else:
            # Get here if no DATAQ Instruments devices are detected
            print("Please connect a DATAQ Instruments device")
            input("Press ENTER to try again...")
            return (False)


    def send_cmd(self, command):
        """
        Sends a passed command string after appending <cr>
        """
        self.ser.write((command + '\r').encode())
        time.sleep(.1)
        if not (self.acquiring):
            # Echo commands if not acquiring
            while True:
                if (self.ser.inWaiting() > 0):
                    while True:
                        try:
                            s = self.ser.readline().decode()
                            s = s.strip('\n')
                            s = s.strip('\r')
                            s = s.strip(chr(0))
                            break
                        except:
                            continue
                    if s != "":
                        print(s)
                        break


    # Configure the instrment's scan list
    def config_scn_lst(self, ):
        # Scan list position must start with 0 and increment sequentially
        position = 0
        for item in self.slist:
            self.send_cmd("slist " + str(position) + " " + str(item))
            position += 1
            # Update the Range table
            if ((item) & (0xf)) < 8:
                # This is an analog channel. Refer to the slist prototype for your instrument
                # as defined in the instrument protocol.
                self.range_table.append(self.analog_ranges[item >> 8])

            elif ((item) & (0xf)) == 8:
                # This is a dig in channel. No measurement range support.
                # Update range_table with any value to keep it aligned.
                self.range_table.append(0)

            elif ((item) & (0xf)) == 9:
                # This is a rate channel
                # Rate ranges begin with 1, so subtract 1 to maintain zero-based index
                # in the rate_ranges tuple
                self.range_table.append(self.rate_ranges[(item >> 8) - 1])

            else:
                # This is a count channel. No measurement range support.
                # Update range_table with any value to keep it aligned.
                self.range_table.append(0)

    def config_daq(self, ):

        while self.discovery() == False:
            self.discovery()
        # Stop in case Device was left running
        self.send_cmd("stop")
        # Define binary output mode
        self.send_cmd("encode 0")
        # Keep the packet size small for responsiveness
        self.send_cmd("ps 0")
        # Configure the instrument's scan list
        self.config_scn_lst()
        # Define sample rate = 10 Hz:
        # 60,000,000/(srate * dec) = 60,000,000/(11718 * 512) = 10 Hz
        self.send_cmd(f"dec {self.dec}")
        self.send_cmd(f"srate {self.srate}")

    def actuate_daq(self, action):
        if action=='start':
            self.acquiring = True
            self.send_cmd("start")
        if action=='reset':
            self.send_cmd("reset 1")
        if action=='stop':
            self.send_cmd("stop")
            time.sleep(1)
            self.ser.flushInput()
            print ("")
            print ("stopped")
            self.acquiring = False
        if action=='exit':
            self.send_cmd("stop")
            self.ser.flushInput()

    def read_data(self, output_string, slist_pointer):

        # The four LSBs of slist determine measurement function
        function = (self.slist[slist_pointer]) & (0xf)
        # Always two bytes per sample...read them
        bytes = self.ser.read(2)
        if function < 8:
            # Working with an Analog input channel
            result = self.range_table[slist_pointer] * int.from_bytes(bytes,byteorder='little', signed=True) / 32768
            output_string = output_string + "{: 3.5f}, ".format(result)

        elif function == 8:
            # Working with the Digital input channel
            result = (int.from_bytes(bytes,byteorder='big', signed=False)) & (0x007f)
            output_string = output_string + "{: 3d}, ".format(result)

        elif function == 9:
            # Working with the Rate input channel
            result = (int.from_bytes(bytes,byteorder='little', signed=True) + 32768) / 65535 * (self.range_table[slist_pointer])
            output_string = output_string + "{: 3.1f}, ".format(result)

        else:
            # Working with the Counter input channel
            result = (int.from_bytes(bytes,byteorder='little', signed=True)) + 32768
            output_string = output_string + "{: 1d}, ".format(result)
        
        return output_string

    def collect_data(self, file_path):

        # This is the slist position pointer. Ranges from 0 (first position) to len(slist)
        slist_pointer = 0
        # This is the constructed output string
        output_string = ""
        self.config_daq()
        self.actuate_daq('start')
        while self.acquiring:
            if (self.ser.inWaiting() > (2 * len(self.slist))):
                with open(file_path, 'a') as file:
                    for _ in range(len(self.slist)):
                        output_string = self.read_data(output_string, slist_pointer)
                        # Get the next position in slist
                        slist_pointer += 1
                        if (slist_pointer + 1) > (len(self.slist)):
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
    
    def collect_data_with_interrupt(self, path_to_save):

        def exit_gracefully(signum, frame):
            # restore the original signal handler as otherwise evil things will happen
            # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
            signal.signal(signal.SIGINT, original_sigint)
            if KeyboardInterrupt:
                self.actuate_daq('exit')
                sys.exit(1)

            # restore the exit gracefully handler here    
            signal.signal(signal.SIGINT, exit_gracefully)

        # store the original SIGINT handler
        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, exit_gracefully)
        self.collect_data(path_to_save)