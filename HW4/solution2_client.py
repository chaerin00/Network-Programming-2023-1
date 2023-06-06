import json

import requests

name = input("Enter a member name: ")
payload = {'name': name}
response = requests.get("http://127.0.0.1:5000/member", params=payload)
data = response.text

# Parse the response data as JSON
json_data = json.loads(data)

# Print the data in JSON format
print(json.dumps(json_data, indent=4))
