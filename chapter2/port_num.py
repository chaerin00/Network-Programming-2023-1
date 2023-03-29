import socket

serviceList = ['echo', 'ftp', 'ssh', 'telnet', 'domain', 'http', 'https', 'smtp']

underlyingProtocol = 'tcp'

for service in serviceList:
    portNum = socket.getservbyname(service, underlyingProtocol)
    print('The service {} uses port number {}'.format(service, portNum))

# The service echo uses port number 7
# The service ftp uses port number 21
# The service ssh uses port number 22
# The service telnet uses port number 23
# The service domain uses port number 53
# The service http uses port number 80
# The service https uses port number 443
# The service smtp uses port number 25
