import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("DUMMYJSON_USERNAME")
PASSWORD = os.getenv("DUMMYJSON_PASSWORD")

BASE_URL = "https://dummyjson.com"

PAGE_SIZE = 10
MAX_RETRIES = 3


# ---- LOGGING


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---- API CLIENT


class APIClient:

    def __init__(self):

        self.session = requests.Session()
        self.access_token = None

    def authenticate(self):

        url = f"{BASE_URL}/auth/login"

        auth = {
            "username": USERNAME,
            "password": PASSWORD
        }

        response = self.session.post(
            url,
            json=auth,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        self.access_token = data["accessToken"]

        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

        logging.info("Authentication successful")

    # ---- Sending Reqest

    def get(self, url, params=None):

        for attempt in range(MAX_RETRIES):
            try:

                response = self.session.get(
                    url,
                    params=params,
                    timeout=30
                )

                # Rate limit
                if response.status_code == 429:

                    retry_after = response.headers.get(
                        "Retry-After",
                        5
                    )

                    logging.warning(
                        f"Rate limited. Waiting {retry_after} seconds."
                    )

                    time.sleep(int(retry_after))

                    continue


                # Server errors
                if response.status_code >= 500:

                    wait_time = 2 ** attempt

                    logging.warning(
                        f"Server error {response.status_code}. "
                        f"Retrying in {wait_time} seconds."
                    )

                    time.sleep(wait_time)

                    continue

                response.raise_for_status()

                return response.json()
            except requests.RequestException as error:

                if attempt == MAX_RETRIES - 1:
                    raise

                wait_time = 2 ** attempt

                logging.warning(
                    f"Request failed: {error}. "
                    f"Retrying in {wait_time} seconds."
                )

                time.sleep(wait_time)

        raise Exception("Request failed after retries")

    # ---- PAGINATION

    def get_products(self):

        url = f"{BASE_URL}/auth/products"

        skip = 0

        while True:

            params = {
                "limit": PAGE_SIZE,
                "skip": skip
            }

            logging.info(
                f"Requesting products: skip={skip}"
            )

            data = self.get(
                url,
                params=params
            )

            products = data.get("products", [])

            if not products:
                break

            for product in products:

                yield product

            skip += PAGE_SIZE



# ---- MAIN -----

def main():

    client = APIClient()

    client.authenticate()

    product_count = 0

    for product in client.get_products():

        product_count += 1

        print(
            product["id"],
            product["title"],
            product["price"]
        )

    logging.info(
        f"Total products processed: {product_count}"
    )


if __name__ == "__main__":
    main()