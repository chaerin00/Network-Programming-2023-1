import socket

if __name__ == '__main__':
    hostname = 'maps.google.com'
    address = socket.gethostbyname(hostname)
    print('The IP address of {} is {}'.format(hostname, address))
    # The IP address of maps.google.com is 172.217.24.78
