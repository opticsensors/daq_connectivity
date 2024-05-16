#client (pc)
import socket

soc = socket.socket()
soc.connect(('localhost',8080))
savefilename = './results/2024-05-16_11.12.06.035455.txt'
with soc,open(savefilename,'wb') as file:
    while True:
        recvfile = soc.recv(4096)
        if not recvfile: break
        file.write(recvfile)
print("File has been received.")