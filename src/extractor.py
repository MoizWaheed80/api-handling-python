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

        products = data.get(
            "products",
            []
        )

        # No more records
        if not products:
            break

        # Return one page
        yield products

        # Move to next page
        skip += PAGE_SIZE