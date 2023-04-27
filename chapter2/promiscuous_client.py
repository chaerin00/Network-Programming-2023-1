from socket import socket

MAX_BYTES = 65535


def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((hostname, port))
    print('Client socket name is {}'.format(sock.getsockname()))
    delay = 0.1
    text = 'This is another message'
    data = b'Hello'
    while True:
        sock.send(data)
        print('Waiting up to {} seconds for a reply'.format(delay))
        sock.settimeout(delay)
        try:
            data = sock.recv(MAX_BYTES)
        except socket.timeout as exc:
            # 0.2, 0.4, 0.8, 1.6, 3.2...
            delay *= 2  # wait even longer for the next request
            if delay > 2.0:
                raise RuntimeError('I think the server is down') from exc
        else:
            break  # we are done, and can stop looping
    print('The server {} replied {!r}'.format(hostname, text))
