import zmq

context = zmq.Context()

# Create SSL/TLS context
ssl_cert = 'ca.crt'
ssl_key = 'localhost.pem'
ssl_context = zmq.Context.instance().ssl_set(context, zmq.SSL_SERVER, certfile=ssl_cert, keyfile=ssl_key)

# Create a socket and bind to an address
socket = context.socket(zmq.REP)
socket.bind('tcp://*:5555')

while True:
    # Wait for a request
    request = socket.recv()

    # Process the request (example: echo the request back)
    response = request

    # Send the response
    socket.send(response)
