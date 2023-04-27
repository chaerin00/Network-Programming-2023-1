import argparse
import json
import socket
import ssl
from threading import Thread


def create_srv_socket(address):
    """Build and return a listening server socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener


def accept_connections_forever(listener, certfile, cafile):
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose, cafile=cafile)
    context.load_cert_chain(certfile)

    while True:
        raw_sock, address = listener.accept()
        print('Accepted connection from {}'.format(address))
        ssl_sock = context.wrap_socket(raw_sock, server_side=True)
        handle_conversation(ssl_sock, address)


def handle_conversation(sock, address):
    """Converse with a client over `sock` until they are done talking."""
    try:
        while True:
            handle_request(sock)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        sock.close()


def handle_request(sock):
    message = recvall(sock)
    string = message.decode('utf-8')
    json_obj = json.loads(string)
    task = json_obj['task']
    if task == 'ping':
        response = ping()
    elif task == 'toggle_string':
        response = toggle_string()
    else:
        raise RuntimeError('Unknown task')

    sock.sendall(response)


def ping():
    return b'ping'


def toggle_string():
    return b'toggle'


def recvall(sock):
    message = sock.recv(4096)
    if not message:
        raise EOFError('socket closed')
    while not message:
        data = sock.recv(4096)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message


def start_threads(listener, certfile, cafile, workers=4):
    t = (listener, certfile, cafile,)
    for i in range(workers):
        Thread(target=accept_connections_forever, args=t).start()


def client(address, cafile=None):
    purpose = ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose, cafile=cafile)
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.connect(address)
    print('Accepted connection from {}'.format(address))
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=address[0])
    ssl_sock.sendall(b'{"task":"ping"}')
    recvall(ssl_sock)
    ssl_sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('multi-threaded server')
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='authority: path to CA certificate PEM file')
    parser.add_argument('-s', metavar='certfile', default=None,
                        help='run as server: path to server PEM file')
    args = parser.parse_args()
    address = (args.host, args.p)
    if args.s:
        listener = create_srv_socket(address)
        start_threads(listener, args.s, args.a)
    else:
        client(address, args.a)
