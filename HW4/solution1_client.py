import requests

keywords = [
    "HTTP",
    "Host",
    "Port",
    "Header",
    "Encryption",
    "Framing",
    "GET common method",
    "POST common method",
    "URL",
    "Status Code"
]
print("Available keywords: \n", keywords)
request = input("Choose one keyword: ")

payload = {'text': request}
result = requests.get("http://127.0.0.1:8000/", params=payload)

print(result.text)
