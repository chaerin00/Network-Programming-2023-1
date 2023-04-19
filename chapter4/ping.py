import argparse
import socket
import sys


def connect_to(hostname_or_ip):
    try:
        infolist = socket.getaddrinfo(
            hostname_or_ip, 'www', 0, socket.SOCK_STREAM, 0,
            socket.AI_ADDRCONFIG | socket.AI_V4MAPPED | socket.AI_CANONNAME
        )
    except socket.gaierror as e:
        print(e.args[1])
        sys.exit(1)

    info = infolist[0]
    socket_agrs = info[0:3]
    address = info[4]
    s = socket.socket(*socket_agrs)
    try:
        s.connect(address)
    except socket.error as e:
        print(e.args[1])
    else:
        print(info[3])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Try connecting to port 80')
    parser.add_argument('hostname', help='hostname')
    connect_to(parser.parse_args().hostname)
