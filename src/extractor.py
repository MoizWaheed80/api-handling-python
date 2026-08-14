from config import PAGE_SIZE


def extract_products(client):

    skip = 0

    while True:

        params = {
            "limit": PAGE_SIZE,
            "skip": skip
        }

        print(
            f"Extracting products "
            f"skip={skip}"
        )

        data = client.get(
            "/auth/products",
            params=params
        )

        products = data.get(
            "products",
            []
        )


        # ----------------------------------
        # NO MORE DATA
        # ----------------------------------

        if not products:

            print("Extraction finished.")

            break


        # ----------------------------------
        # YIELD ONE PAGE
        # ----------------------------------

        yield products


        # ----------------------------------
        # NEXT PAGE
        # ----------------------------------

        skip += PAGE_SIZE