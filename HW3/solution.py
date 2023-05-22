import argparse
import json
import random
import socket
import ssl
import time
import zlib
from threading import Thread

import dns.resolver
import zmq


class NewsGenerator:
    def __init__(self):
        # Initialize the news generator.
        self.topics = ["business", "entertainment", "health", "science",
                       "sports", "technology"]
        self.events = ["new product launch", "merger", "acquisition",
                       "lawsuit", "scandal", "government regulation"]
        self.companies = ["Apple", "Microsoft", "Google", "Amazon",
                          "Facebook", "Tesla"]

    def get_topics(self):
        return self.topics

    def get_news(self):
        # Generate a random news headline.
        topic = random.choice(self.topics)
        event = random.choice(self.events)
        company = random.choice(self.companies)
        headline = topic + " " + company + " " + event
        return headline


def publisher(zcontext, url):
    """Produce random points in the unit square."""
    zsock = zcontext.socket(zmq.PUB)
    zsock.bind(url)
    newsGenerator = NewsGenerator()
    # send news for every 0.1
    while True:
        zsock.send_string(newsGenerator.get_news())
        time.sleep(0.1)


def subscriber(zcontext, url):
    sock = zcontext.socket(zmq.SUB)
    sock.connect(url)
    newsGenerator = NewsGenerator()
    print(newsGenerator.get_topics())
    topic = input("select topic: ")
    sock.setsockopt(zmq.SUBSCRIBE, topic.encode('ascii'))
    end_t = time.time() + 10
    while time.time() < end_t:
        data = sock.recv_string()
        print(data)
    sock.disconnect(url)


class StockTicker:
    def __init__(self):
        self.companies = ["AAPL", "MSFT", "GOOGL"]
        self.prices = {}
        for company in self.companies:
            self.prices[company] = random.randint(100, 1000)

    def get_companies(self):
        return self.companies

    def generate_stock_price(self, company):
        if company not in self.companies:
            raise ValueError("Invalid company")
        # Generate a random stock price for the company
        price = random.randint(100, 1000)
        self.prices[company] = price
        return price


def stock_client(zcontext, url):
    sock = zcontext.socket(zmq.PULL)
    sock.bind(url)
    company_list = StockTicker().get_companies()
    print(company_list)
    target_company = input("select company: ")
    while target_company not in company_list:
        target_company = input("select company: ")
    # get stock price for 10 seconds
    end_t = time.time() + 10
    while time.time() < end_t:
        company, price = sock.recv_json()
        # filter pushed depending on company
        if company == target_company:
            print(company + ": " + str(price))


def stock_ticker(zcontext, url):
    sock = zcontext.socket(zmq.PUSH)
    sock.connect(url)
    ticker = StockTicker()
    while True:
        # choose random company
        company = random.choice(ticker.get_companies())
        price = ticker.generate_stock_price(company)
        if price:
            sock.send_json((company, price))
        else:
            continue
        time.sleep(0.1)


class Chatroom:
    def __init__(self):
        self.clients = []

    def join(self, client):
        self.clients.append(client)
        print(self.clients)

    def leave(self, client):
        self.clients.remove(client)

    def send(self, sender, message):
        for client in self.clients:
            if client != sender:
                client.send((sender, message))


def chat_owner(zcontext, url):
    zsock = zcontext.socket(zmq.REP)
    zsock.bind(url)
    chat_room = Chatroom()

    while True:
        try:
            (request, sender, message) = zsock.recv_json()
            print(request, sender, message)
            if request == "join":
                chat_room.join(sender)
                response = ('success', 'chat_owner', sender + " joined")
            elif request == "send":
                chat_room.send(sender, message)
                response = ('success', sender, message)
            elif request == "leave":
                chat_room.leave(sender)
                response = ('success', "chat_owner", sender + " leaved")
            else:
                response = ("fail", 'chat_owner', "Not found task")
        except Exception as e:
            response = ("fail", 'chat_owner', "Not valid request")
        finally:
            zsock.send_json(response)


def chat_member(zcontext, url):
    zsock = zcontext.socket(zmq.REQ)
    zsock.connect(url)
    name = input("What is your name? ")
    while True:
        message = ''
        task = input("What do you want to do? (join, send, leave) : ")
        if task == 'send':
            message = input("message: ")
        zsock.send_json((task, name, message))
        status, sender, message = (zsock.recv_json())
        print("[{}] {}: {}".format(status, sender, message))
        if task == 'leave' and status == 'success':
            break


def handle_request(sock):
    message = recvall(sock)
    # decompress byte string using zlib
    decompressed_str = zlib.decompress(message).decode('utf-8')
    request = json.loads(decompressed_str)
    task = request['task']
    zcontext = zmq.Context()
    if task == 'ping':
        domain = request['domain']
        response = ping(domain)
    elif task == 'toggle_string':
        s = request['s']
        response = toggle_string(s)
    elif task == 'news':
        publisher(zcontext, 'tcp://127.0.0.1:6700')
    elif task == 'stock':
        stock_ticker(zcontext, 'tcp://127.0.0.1:6701')
    elif task == 'chat':
        chat_owner(zcontext, 'tcp://127.0.0.1:6702')
    else:
        raise RuntimeError('Unknown task')

    response_dict = {
        "status": "OK",
        "message": response
    }

    # encode JSON string as bytes
    response_bytes = json.dumps(response_dict).encode('utf-8')
    sock.sendall(response_bytes)


def ping(domain):
    for qtype in 'A', 'AAAA', 'CNAME', 'MX', 'NS':
        answer = dns.resolver.resolve(domain, qtype, raise_on_no_answer=False)
        if answer.rrset is not None:
            return str(answer[0])


def toggle_string(s):
    result = ""
    for c in s:
        # check if character is uppercase
        if ord('A') <= ord(c) <= ord('Z'):
            # convert to lowercase by adding 32 to ASCII code
            c = chr(ord(c) + 32)
        # check if character is lowercase
        elif ord('a') <= ord(c) <= ord('z'):
            # convert to uppercase by subtracting 32 from ASCII code
            c = chr(ord(c) - 32)
        # append converted character to result
        result += c
    return result


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
    task = input("Enter the name of task: ")
    data = {"task": task}
    if task in ['ping', 'toggle_string']:
        if task == 'ping':
            domain = input("Enter a domain name: ")
            data["domain"] = domain
        elif task == 'toggle_string':
            s = input("Enter a string: ")
            data["s"] = s

        json_bytes = json.dumps(data).encode('utf-8')

        # compress byte string using zlib
        compressed_bytes = zlib.compress(json_bytes)
        ssl_sock.sendall(compressed_bytes)

        response_bytes = recvall(ssl_sock)
        response_str = response_bytes.decode('utf-8')

        # parse JSON string into a Python dictionary
        response_dict = json.loads(response_str)

        # access fields in response dictionary and display them
        print("Status:", response_dict["status"])
        print("Message:", response_dict["message"])
        ssl_sock.close()

    elif task in ['news', 'stock', 'chat']:
        json_bytes = json.dumps(data).encode('utf-8')

        # compress byte string using zlib
        compressed_bytes = zlib.compress(json_bytes)
        ssl_sock.sendall(compressed_bytes)
        zcontext = zmq.Context()
        if task == 'news':
            subscriber(zcontext, 'tcp://127.0.0.1:6700')
        elif task == 'stock':
            stock_client(zcontext, 'tcp://127.0.0.1:6701')
        elif task == 'chat':
            chat_member(zcontext, 'tcp://127.0.0.1:6702')


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
