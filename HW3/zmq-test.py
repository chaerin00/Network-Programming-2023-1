#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter08/queuepi.py
# Small application that uses several different message queues
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
    price = zsock.recv_string()
    print(price)


def stock_ticker(zcontext, url):
    """Tally how many points fall within the unit circle, and print pi."""
    zsock = zcontext.socket(zmq.PUSH)
    zsock.connect(url)
    ticker = StockTicker()
    print(ticker.get_companies())
    company = input("select company: ")
    price = ticker.generate_stock_price(company)
    if price:
        zsock.send_string(str(price))


def start_thread(function, *args):
    thread = threading.Thread(target=function, args=args)
    thread.daemon = True  # so you can easily Ctrl-C the whole program
    thread.start()


def main(zcontext):
    pubsub = 'tcp://127.0.0.1:6700'
    # reqrep = 'tcp://127.0.0.1:6701'
    pushpull = 'tcp://127.0.0.1:6702'
    task = sys.stdin.readline().rstrip()
    if task == "news":
        start_thread(subscriber, zcontext, pubsub)
        start_thread(publisher, zcontext, pubsub)
    if task == "stock_ticker":
        start_thread(stock_client, zcontext, pushpull)
        start_thread(stock_ticker, zcontext, pushpull)
    else:
        exit()
    # start_thread(publisher, zcontext, pubsub)
    # start_thread(judge, zcontext, pubsub, reqrep, pushpull)
    # start_thread(pythagoras, zcontext, reqrep)
    # start_thread(tally, zcontext, pushpull)
    time.sleep(30)


if __name__ == '__main__':
    main(zmq.Context())
