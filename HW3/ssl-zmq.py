import zmq.auth
import zmq.auth.thread

context = zmq.Context()

# Generate SSL certificates
cert_dir = "./certificates"
public_keys_dir = cert_dir + "/public_keys"
private_keys_dir = cert_dir + "/private_keys"
server_secret_file = private_keys_dir + "/server.key_secret"
server_public, server_secret = zmq.auth.create_certificates(cert_dir, "server")

# Configure the server with CURVE encryption
zmq.auth.load_certificates(public_keys_dir)

# Start the authentication thread
auth = zmq.auth.thread.ThreadAuthenticator(context)
auth.start()
auth.configure_curve(domain='127.0.0.1', location=public_keys_dir)

# Create a socket and bind to an address
socket = context.socket(zmq.REP)
socket.curve_secretkey = server_secret
socket.curve_publickey = server_public
socket.curve_server = True
socket.bind('tcp://*:5555')

while True:
    # Wait for a request
    request = socket.recv()

    # Process the request (example: echo the request back)
    response = request

    # Send the response
    socket.send(response)
