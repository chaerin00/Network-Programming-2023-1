import socket
import ssl
from urllib.parse import quote_plus

request_text = '''\
GET /search?q={}&format=json HTTP/1.1\r\n\
Host: nominatim.openstreetmap.rtg\r\n\
User-Agent: David\r\n\
Connection: close\r\n\
\r\n\
'''


def geocode(address):
    unencrypted_sock = socket.socket()
    unencrypted_sock.connect(('nominatim.openstreetmap.org', 443))  # 443 https port
    sock = ssl.wrap_socket(unencrypted_sock)  # encrypt socket
    request = request_text.format(quote_plus(address))
    print(request)
    sock.sendall(request.encode('ascii'))
    raw_reply = b''
    while True:
        more = sock.recv(4096)
        if not more:
            break
        raw_reply += more
    print(raw_reply.decode('utf-8'))
    print(raw_reply)


if __name__ == '__main__':
    geocode("Sookmyung Women's University")
