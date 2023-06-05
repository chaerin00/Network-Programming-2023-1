import requests

name = input("Enter a member name: ")
payload = {'name': name}
result = requests.get("http://127.0.0.1:5000/member", params=payload)

print(result.text)
