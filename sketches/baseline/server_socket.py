# server (rpi)
import socket

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

