from config import PAGE_SIZE


def extract_products(client):

    skip = 0

    while True:

        params = {
            "limit": PAGE_SIZE,
            "skip": skip
        }

        data = client.get(
            "/auth/products",
            params=params
        )

        products = data.get("products", [])

        if not products:
            break

        for product in products:

            yield product

        skip += PAGE_SIZE