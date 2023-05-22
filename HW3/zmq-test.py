import random
import sys
import threading
import time

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
    while True:
        zsock.send_string(newsGenerator.get_news())
        time.sleep(0.1)


def subscriber(zcontext, url):
    isock = zcontext.socket(zmq.SUB)
    isock.connect(url)
    newsGenerator = NewsGenerator()
    print(newsGenerator.get_topics())
    topic = input("select topic: ")
    isock.setsockopt(zmq.SUBSCRIBE, topic.encode('ascii'))
    while True:
        data = isock.recv_string()
        print(data)


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
    """Tally how many points fall within the unit circle, and print pi."""
    zsock = zcontext.socket(zmq.PULL)
    zsock.bind(url)
    company_list = StockTicker().get_companies()
    print(company_list)
    target_company = input("select company: ")
    while target_company not in company_list:
        target_company = input("select company: ")
    end_t = time.time() + 10
    while time.time() < end_t:
        company, price = zsock.recv_json()
        if company == target_company:
            print(company + ": " + str(price))


def stock_ticker(zcontext, url):
    """Tally how many points fall within the unit circle, and print pi."""
    zsock = zcontext.socket(zmq.PUSH)
    zsock.connect(url)
    ticker = StockTicker()
    while True:
        company = random.choice(ticker.get_companies())
        price = ticker.generate_stock_price(company)
        if price:
            zsock.send_json((company, price))
        else:
            continue

        time.sleep(0.1)


class Chatroom:
    def __init__(self):
        self.clients = []

    def join(self, client):
        self.clients.append(client)

    def leave(self, client):
        self.clients.remove(client)

    def send(self, sender, message):
        for client in self.clients:
            if client != sender:
                client.send((sender, message))


def owner(zcontext, url):
    zsock = zcontext.socket(zmq.REP)
    zsock.bind(url)
    chat_room = Chatroom()
    while True:
        (request, sender, message) = zsock.recv_json()
        if request == "join":
            chat_room.join(message)
            response = ('success', 'owner', sender + " joined")
            print("owner: " + sender + " joined")
        elif request == "send":
            chat_room.send(sender, message)
            response = ('success', sender, message)
            print(sender + ": " + message)
        elif request == "leave":
            chat_room.leave(sender)
            response = ('success', "owner", sender + " leaved")
            print("owner: " + sender + " leaved")
        else:
            response = ("fail", 'owner', "Not found task")

        zsock.send_json(response)


def member(zcontext, url):
    zsock = zcontext.socket(zmq.REQ)
    zsock.connect(url)
    name = input("What is your name? ")
    zsock.send_json(("join", name, name))
    zsock.recv_json()
    zsock.send_json(("send", name, "Hi there! I'm " + name))
    status, sender, message = zsock.recv_json()
    if message and status and sender != name:
        print(message)
    zsock.send_json(("leave", name, "leave"))
    zsock.recv_json()


def start_thread(function, *args):
    thread = threading.Thread(target=function, args=args)
    thread.daemon = True  # so you can easily Ctrl-C the whole program
    thread.start()


def main(zcontext):
    pubsub = 'tcp://127.0.0.1:6700'
    reqrep = 'tcp://127.0.0.1:6701'
    pushpull = 'tcp://127.0.0.1:6702'
    print("select task (news, stock, chat): ")
    task = sys.stdin.readline().rstrip()
    if task == "news":
        start_thread(subscriber, zcontext, pubsub)
        start_thread(publisher, zcontext, pubsub)
    elif task == "stock":
        start_thread(stock_client, zcontext, pushpull)
        start_thread(stock_ticker, zcontext, pushpull)
    elif task == "chat":
        start_thread(owner, zcontext, reqrep)
        start_thread(member, zcontext, reqrep)
    else:
        exit()
    time.sleep(30)


if __name__ == '__main__':
    main(zmq.Context())
