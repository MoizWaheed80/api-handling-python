import requests

from config import (
    USERNAME,
    PASSWORD,
    BASE_URL
)


class APIClient:

    def __init__(self):

        self.session = requests.Session()

        self.access_token = None

    # -----------------------------
    # AUTHENTICATION
    # -----------------------------

    def authenticate(self):

        url = f"{BASE_URL}/auth/login"

        payload = {
            "username": USERNAME,
            "password": PASSWORD
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        self.access_token = data["accessToken"]

        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

    # -----------------------------
    # GET REQUEST
    # -----------------------------

    def get(self, endpoint, params=None):

        url = f"{BASE_URL}{endpoint}"

        response = self.session.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()