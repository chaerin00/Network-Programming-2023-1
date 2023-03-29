import argparse
import socket


def recvall(sock, length):
    data = b''
    # keep check it til every data is received
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data


def client(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', port))
    print('Clinet has been assigned socket name', sock.getsockname())
    sock.sendall(b'Hi there, server')
    reply = recvall(sock, 16)
    print('The server said', repr(reply))
    sock.close()


def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True:
        print('Waiting to accept a new connection')
        active, address = sock.accept()
        print('We have accepted a connection from', address)  # active socket
        print(' Socket name:', active.getsockname())  # listening socket
        print(' Socket peer:', active.getpeername())  # active socket
        message = recvall(active, 16)
        print(' Incoming message:', repr(message))
        active.sendall(b'Farewell, client')
        active.close()
        print(' Replay sent, socket closed')


if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive UDP locally')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='UDP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.p)
