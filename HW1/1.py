import socket

request_text = """\
GET /json?fields={}&lang={} HTTP/1.1\r\n\
Host: ip-api.com\r\n\
User-Agent: Foundations of Python Network Programming example search4.py\r\n\
Connection: close\r\n\
\r\n\
"""


def ip_geolocation():
    sock = socket.socket()
    sock.connect(('ip-api.com', 80))  # connect with http port 80
    field_list = ['city', 'regionName', 'country', 'lat', 'lon']  # field query
    lang = 'fr'  # lang query
    request = request_text.format(','.join(field_list), lang)
    sock.sendall(request.encode('ascii'))
    raw_reply = b''
    while True:
        more = sock.recv(4096)
        if not more:
            break
        raw_reply += more
    print(raw_reply.decode('utf-8'))


if __name__ == '__main__':
    ip_geolocation()
