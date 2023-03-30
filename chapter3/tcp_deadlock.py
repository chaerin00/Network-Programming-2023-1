import argparse
import socket
import sys


def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    sock.listen(1)
    print('Listening at ', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        print('Processing up to 1024', sockname)
        n = 0
        while True:
            data = sc.recv(1024)
            if not data:
                break
            output = data.decode('ascii').upper().encode('ascii')
            sc.sendall(output)
            n += len(data)
            print('\r %d bytes processed so far' % (n,), end=' ')
            sys.stdout.flush()
        print()
        sc.close()
        print('  Socket closed')


def client(port, bytecount):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bytecount = (bytecount + 15) // 16 * 16
    message = b'capitalize this!'

    print('Sending', bytecount, 'bytes if data, in chunks of 16 bytes')
    sock.connect(('localhost', port))

    sent = 0
    while sent < bytecount:
        sock.sendall(message)
        sent += len(message)
        print('\n %d bytes sent' % (sent,), end=' ')
        sys.stdout.flush()

    print()
    sock.shutdown(socket.SHUT_WR)

    print('Receiving all the data the server sends back')

    received = 0
    while True:
        data = sock.recv(42)
        if not received:
            print('  The first data received says', repr(data))
        if not data:
            break
        received += len(data)
        print('\r  %d bytes received' % (received,), end=' ')

    print()
    sock.close()


if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive UDP locally')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('bytecount', type=int, nargs='?', default=16,
                        help='number of bytes for client to send (default 16)')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='UDP port (default 1060)')
    args = parser.parse_args()
    if args.role == 'client':
        client(args.p, args.bytecount)
    else:
        server(args.p)
