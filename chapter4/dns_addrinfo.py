import socket
from pprint import pprint

# infolist = socket.getaddrinfo(None, 'smtp', 0, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
# pprint(infolist)

infolist = socket.getaddrinfo('ssu.ac.kr', 'smtp', 0, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
pprint(infolist)

# info = infolist[0]
# pprint(info[4])
#
# s = socket.socket(*info[0:3])
# s.connect(info[4])
