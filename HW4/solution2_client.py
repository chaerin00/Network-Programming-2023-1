import requests

payload = {'text': 'david'}
result = requests.get("http://127.0.0.1:5000/member", params=payload)

print(result.text)
