#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter07/srv_threaded.py
# Using multiple threads to serve several clients in parallel.

import argparse
import random
import socket
import time
from threading import Thread

aphorisms = {b'Beautiful is better than?': b'Ugly.',
             b'Explicit is better than?': b'Implicit.',
             b'Simple is better than?': b'Complex.'}


def get_answer(aphorism):
    """Return the string response to a particular Zen-of-Python aphorism."""
    time.sleep(0.0)  # increase to simulate an expensive operation
    return aphorisms.get(aphorism, b'Error: unknown aphorism.')


def parse_command_line(description):
    """Parse command line and return a socket address."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    return address


def create_srv_socket(address):
    """Build and return a listening server socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener


def accept_connections_forever(listener):
    """Forever answer incoming connections on a listening socket."""
    while True:
        sock, address = listener.accept()
        print('Accepted connection from {}'.format(address))
        handle_conversation(sock, address)


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


# 여기를 이제 수정해야지
def handle_request(sock):
    """Receive a single client request on `sock` and send the answer."""
    aphorism = recv_until(sock, b'?')
    answer = get_answer(aphorism)
    sock.sendall(answer)


def recv_until(sock, suffix):
    """Receive bytes over socket `sock` until we receive the `suffix`."""
    message = sock.recv(4096)
    if not message:
        raise EOFError('socket closed')
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message


def start_threads(listener, workers=4):
    t = (listener,)
    for i in range(workers):
        Thread(target=accept_connections_forever, args=t).start()


def client(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    aphorism_list = list(aphorisms)
    for aphorism in random.sample(aphorism_list, 3):
        sock.sendall(aphorism)
        print(aphorism, recv_until(sock, b'.'))
    sock.close()


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
        start_threads(listener)
    else:
        client(address)
