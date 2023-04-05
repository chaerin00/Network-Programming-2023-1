import argparse
import random
import socket


def server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        x = random.randint(1, 10)
        print('random number is ', x)
        is_started = False
        is_correct = False
        attempt_count = 1
        while True:
            data = sc.recv(1024)
            if not data or is_correct or attempt_count > 5:
                break

            guess = data.decode('ascii')

            if not is_started:
                if guess == 'start':
                    is_started = True
                    sc.sendall(b'start')
                else:
                    sc.sendall(b'if you want to start a game, type "start": ')
            else:
                try:
                    if int(guess) == x:
                        output = b'Congratulations you did it.'
                        is_correct = True
                    elif attempt_count >= 5:
                        output = b'You lost.'
                    elif int(guess) < x:
                        output = b' You guessed too small!"'
                    elif int(guess) > x:
                        output = b' You Guessed too high!'
                    attempt_count += 1
                except ValueError:
                    output = b'please send number'
                sc.sendall(output)

        sc.sendall(b'')
        sc.close()
        print('  Socket closed')


def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    attempt_count = 0
    while True:
        message = input('if you want to start a game, type "start": ')
        sock.sendall(message.encode('ascii'))

        is_started = False
        while True:
            data = sock.recv(42)
            response = data.decode('ascii')
            print(response, end=' ')

            if not data or response == 'correct' or attempt_count >= 5:
                break

            if not is_started:
                if response == 'start':
                    is_started = True
                else:
                    message = input()
                    sock.sendall(message.encode('ascii'))
                    continue

            message = input('\n Guess the number: ')
            sock.sendall(message.encode('ascii'))
            attempt_count += 1

        break
    sock.close()


if __name__ == '__main__':
    roles = ('client', 'server')
    parser = argparse.ArgumentParser(description='Get deadlocked over TCP')
    parser.add_argument('role', choices=roles, help='which role to play')
    parser.add_argument('host', help='interface the server listens at;'
                                     ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    if args.role == 'client':
        client(args.host, args.p)
    else:
        server(args.host, args.p)
