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

        # Send the initial message to the client
        sc.sendall(b'To start the game, please send "start" as the first message.\n')

        # Game loop
        is_started = False
        guess_count = 0
        while True:
            # Receive the client's message
            data = sc.recv(16)
            message = data.decode()

            # Check if the client wants to start the game
            if not is_started:
                if message == 'start':
                    guess_count += 1
                    is_started = True
                    sc.sendall(b'Guess a number between 1 to 10:\n')
                else:
                    sc.sendall(b'To start the game, please send "start" as the first message.')
            else:
                # Check if the client's guess is correct
                try:
                    guess = int(message)
                except ValueError:
                    sc.sendall(b'Send a number.')
                    continue

                if guess == x:
                    # Send the winning message and close the connection
                    sc.sendall(b'Congratulations you did it.\n')
                    sc.close()
                    break
                elif guess_count == 5:
                    # Send the losing message and close the connection
                    sc.sendall(b'Sorry, you lose. The number was ' + str(number).encode() + b'.\n')
                    sc.close()
                    break
                else:
                    # Increase the number of guesses and send the appropriate message to the client
                    guess_count += 1
                    if guess < x:
                        sc.sendall(b'You guessed too small!\n')
                    else:
                        sc.sendall(b'You guessed too high!\n')


def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    data = sock.recv(64)
    message = data.decode()
    print(message)

    # Game loop
    while True:
        # Send the client's guess to the server
        guess = input()
        sock.sendall(guess.encode())

        # Receive the server's message
        data = sock.recv(64)
        message = data.decode()
        print(message)

        # Check if the game is over
        if message.startswith('Congratulations') or message.startswith('Sorry'):
            break


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
