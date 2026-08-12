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


# ---- AUTHENTICATED REQUEST


headers = {
    "Authorization": f"Bearer {access_token}"
}


# ---- PAGINATION


url = "https://dummyjson.com/auth/products"

limit = 10
skip = 0


while True:

    params = {
        "limit": limit,
        "skip": skip
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    products = data["products"]

    if not products:
        break

    for product in products:
        print(
            product["id"],
            product["title"],
            product["price"]
        )

    # ---- NEXT PAGE
  
    skip += limit

    # ---- RATE LIMIT

    time.sleep(1)