#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter01/search4.py

# (The Google API originally used in this example now requires API keys,
#  so here's an alternative that calls openstreetmap.org.)

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
    sock.connect(('ip-api.com', 80))
    field_list = ['city', 'regionName', 'country', 'lat', 'lon']
    lang = 'fr'
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
