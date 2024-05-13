import socket

class Daq_socket:
    # *** UDP Port Number Function *** 
    # 1235 (fixed)         Device's discovery receiving port
    # 1234 (programmable)  PC's default discovery receiving port.
    # 51235 (fixed)        Device's command receiving port
    # 1234 (programmable)  PC's default status/data receiving port. Programmable via the PORT command.

    def __init__(self, ):


        self.socket_buffer_size = 2048

        # Open socket for sending broadcast and another to receive our responses
        self.disc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        self.disc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        hostname=socket.gethostname()
        IPAddr=socket.gethostbyname(hostname)
        
        print ("PC's IP is ", IPAddr)
        self.disc_sock.bind((IPAddr,1235))       # DataQ device's discovery receiving port, from documentation
        print ("Done binding!")

        # socket for receiving
        rec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rec_sock.bind((IPAddr,1234))  # Have to make sure this port is open --> 'sudo ufw allow 1234/udp' or Windows key + R and type wf.msc


def client():
    soc = socket.socket()
    soc.connect(('localhost',8080))
    savefilename = 'a.txt'
    with soc,open(savefilename,'wb') as file:
        while True:
            recvfile = soc.recv(4096)
            if not recvfile: break
            file.write(recvfile)
    print("File has been received.")


def server():
    soc = socket.socket()
    soc.bind(('',8080))
    soc.listen(1)
    filename = 'a.txt'

    print('waiting for connection...')
    with soc:
        con,addr = soc.accept()
        print('server connected to',addr)
        with con:
            with open(filename, 'rb') as file:
                sendfile = file.read()
            con.sendall(sendfile)
            print('file sent')

