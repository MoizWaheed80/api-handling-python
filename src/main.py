import pandas as pd

from api_client import APIClient
from extractor import extract_products

from normalizer import (
    normalize_product,
    normalize_dimensions,
    normalize_reviews
)


def main():

    client = APIClient()

    # -----------------------------
    # AUTHENTICATION
    # -----------------------------

    client.authenticate()

    print("Authentication successful")

    # -----------------------------
    # STORAGE FOR NORMALIZED DATA
    # -----------------------------

    product_rows = []

    dimension_rows = []

    review_rows = []

    # -----------------------------
    # EXTRACTION + NORMALIZATION
    # -----------------------------

    for api_product in extract_products(client):

        # Product
        product = normalize_product(
            api_product
        )

        product_rows.append(product)

        # Dimensions
        dimensions = normalize_dimensions(
            api_product
        )

        dimension_rows.append(dimensions)

        # Reviews
        reviews = normalize_reviews(
            api_product
        )

        review_rows.extend(reviews)

    # -----------------------------
    # CREATE TABLE-LIKE DATAFRAMES
    # -----------------------------

    products_df = pd.DataFrame(
        product_rows
    )

    dimensions_df = pd.DataFrame(
        dimension_rows
    )

    reviews_df = pd.DataFrame(
        review_rows
    )

    # -----------------------------
    # DISPLAY
    # -----------------------------

    print("\nPRODUCTS")
    print(products_df)

    print("\nDIMENSIONS")
    print(dimensions_df)

    print("\nREVIEWS")
    print(reviews_df)


if __name__ == "__main__":
    main()