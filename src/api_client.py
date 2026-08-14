import time
import requests

from config import (
    BASE_URL,
    USERNAME,
    PASSWORD,
    MAX_RETRIES,
    REQUEST_TIMEOUT
)


class APIClient:

    def __init__(self):

        self.session = requests.Session()

        self.access_token = None


    # ======================================
    # AUTHENTICATION
    # ======================================

    def authenticate(self):

        url = f"{BASE_URL}/auth/login"

        payload = {
            "username": USERNAME,
            "password": PASSWORD
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        self.access_token = data["accessToken"]

        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })


    # ======================================
    # GET REQUEST
    # ======================================

    def get(self, endpoint, params=None):

        url = f"{BASE_URL}{endpoint}"

        for attempt in range(MAX_RETRIES):

            try:

                response = self.session.get(
                    url,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )


                # --------------------------
                # RATE LIMIT
                # --------------------------

                if response.status_code == 429:

                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:

                        wait_time = int(
                            retry_after
                        )

                    else:

                        wait_time = 2 ** attempt

                    print(
                        f"Rate limited. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue


                # --------------------------
                # SERVER ERROR
                # --------------------------

                if response.status_code >= 500:

                    wait_time = 2 ** attempt

                    time.sleep(wait_time)

                    continue


                response.raise_for_status()

                return response.json()


            except requests.RequestException:

                if attempt == MAX_RETRIES - 1:

                    raise

                wait_time = 2 ** attempt

                time.sleep(wait_time)


        raise Exception(
            "API request failed after retries."
        )