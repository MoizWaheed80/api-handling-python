import requests

response = requests.get("https://dummyjson.com/users")

print(response.status_code)
print(response.text)