import socket
from pprint import pprint

infolist = socket.getaddrinfo('gatech.edu', 'www')
pprint(infolist)

info = infolist[0]
info[0:3]

s = socket.socket(*info[0:3])
s.connect(info[4])
