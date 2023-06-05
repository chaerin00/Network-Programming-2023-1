import csv
from wsgiref.simple_server import make_server

csv_file_path = './solution1_csv.csv'

keywords = []
definitions = []


def find_definition(keyword):
    idx = keywords.index(keyword)
    return definitions[idx]


def read_csv():
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)

        # Skip the header row if needed
        next(csv_reader)

        # Iterate through each row in the CSV file
        for row in csv_reader:
            keyword = row[0]
            definition = row[1]

            # Append keyword and definition to the respective lists
            keywords.append(keyword)
            definitions.append(definition)


def app(environ, start_response):
    read_csv()
    host = environ.get('HTTP_HOST', '127.0.0.1')
    path = environ.get('PATH_INFO', '/')
    keyword = environ.get('QUERY_STRING').split("=")[1]
    if ':' in host:
        host, port = host.split(':', 1)
    if '?' in path:
        path, query = path.split('?', 1)

    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    if environ['REQUEST_METHOD'] != 'GET':
        start_response('501 Not Implemented', headers)
        yield b'501 Not Implemented'
    elif host != '127.0.0.1' or path != '/':
        start_response('404 Not Found', headers)
        yield b'404 Not Found'
    else:
        start_response('200 OK', headers)
        yield find_definition(keyword).encode('utf-8')


if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    host, port = httpd.socket.getsockname()
    print('Serving on', host, 'port', port)
    httpd.serve_forever()
