import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("DUMMYJSON_USERNAME")
password = os.getenv("DUMMYJSON_PASSWORD")

# ---- AUTHENTICATION

login_url = "https://dummyjson.com/auth/login"

login_data = {
    "username": username,
    "password": password
}

response = requests.post(login_url, json=login_data)

response.raise_for_status()

data = response.json()

access_token = data["accessToken"]

print("Authentication successful")

# ---- AUTHENTICATION REQUEST

headers = {
    "Authorization": f"Bearer {access_token}"
}