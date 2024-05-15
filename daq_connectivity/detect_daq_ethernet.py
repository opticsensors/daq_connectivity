import socket
import re
import logging

class Detect_daq_ethernet:
    # Ports Configuration
    DISCOVERY_RECEIVING_PORT = 1235
    COMMAND_RECEIVING_PORT = 51235
    PC_DEFAULT_RECEIVING_PORT = 1234
    BROADCAST_ADDRESS = '255.255.255.255'
    BROADCAST_MESSAGE = b'dataq_instruments'
    SOCKET_BUFFER_SIZE = 2048

    def __init__(self, ip_address='0.0.0.0'):
        logging.basicConfig(level=logging.INFO)
        
        # Open socket for sending broadcast and another to receive our responses
        self.disc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        self.disc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        hostname=socket.gethostname()
        IPAddr=socket.gethostbyname(hostname)
        
        # DataQ device's discovery receiving port, from documentation
        self.disc_sock.bind((IPAddr,self.DISCOVERY_RECEIVING_PORT))       
        logging.info(f"Socket bound to {IPAddr}:{self.DISCOVERY_RECEIVING_PORT}")

        # socket for receiving
        self.rec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # indicates IPv4 and User Datagram Protocol (UDP)
        self.rec_sock.bind((IPAddr,self.PC_DEFAULT_RECEIVING_PORT))  # Have to make sure this port is open --> 'sudo ufw allow 1234/udp'
        logging.info(f"Socket bound to {IPAddr}:{self.PC_DEFAULT_RECEIVING_PORT}")

    def do_udp_discovery(self):
        logging.info(f"Sending UDP Broadcast '{self.BROADCAST_MESSAGE.decode()}'")
        self.disc_sock.sendto(self.BROADCAST_MESSAGE, (self.BROADCAST_ADDRESS, self.DISCOVERY_RECEIVING_PORT))
        
        messages = self.receive_messages(self.rec_sock)

        # Process received messages
        decoded_messages = [self.parse_message(data) for addr, data in messages if data]
        for message in decoded_messages:
            logging.info(f"Found DataQ device {message['DeviceModel']} on IP {message['IP']}")
            for key, value in message.items():
                logging.info(f"   {key}: {value}")

    def receive_messages(self, socket):
        messages = []
        socket.settimeout(3)  # Set timeout to 3 seconds
        while True:
            try:
                data, addr = socket.recvfrom(self.SOCKET_BUFFER_SIZE)
                messages.append((addr, data))
            except socket.timeout:
                break
        return messages

    def parse_message(self, data):
        data = data.decode()
        pattern = re.compile(
            r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) "
            r"([\w:]{17}) "
            r"(\w*) (\w*) (\w*) (\w*) (\w*) (\w*) (\w*) (\w*) (\w*) (\w*)"
        )
        result = pattern.search(data)
        keys = ['IP', 'MAC', 'SoftwareRev', 'DeviceModel', 'ADCRunning', 'Reserved', 
                'LengthOfDescription', 'Description', 'SerialNumber', 'GroupID', 'OrderInGroup', 'Master/Slave']
        return {key: result.group(i+1) for i, key in enumerate(keys) if result}

    def close_sockets(self):
        self.disc_sock.close()
        self.rec_sock.close()

