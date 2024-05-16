# server (rpi)
import socket

soc = socket.socket()
soc.bind(('192.168.1.43',8080))
soc.listen(1)
filename = './results/2024-05-16_11.12.06.035455.csv'

print('waiting for connection...')
with soc:
    con,addr = soc.accept()
    print('server connected to',addr)
    with con:
        with open(filename, 'rb') as file:
            sendfile = file.read()
        con.sendall(sendfile)
        print('file sent')

