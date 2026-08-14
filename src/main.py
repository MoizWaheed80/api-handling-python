import pandas as pd

from api_client import APIClient
from extractor import extract_products
from schema_manager import SchemaManager
from normalizer import normalize_product


def main():

    # ======================================
    # CREATE API CLIENT
    # ======================================

    client = APIClient()


    # ======================================
    # AUTHENTICATE
    # ======================================

    print("Authenticating...")

    client.authenticate()

    print("Authentication successful.")


    # ======================================
    # CREATE SCHEMA MANAGER
    # ======================================

    schema_manager = SchemaManager()


    # ======================================
    # PROCESS API PAGES
    # ======================================

    batch_number = 0

    for products in extract_products(client):

        batch_number += 1

        print(
            f"\nProcessing batch "
            f"{batch_number}"
        )


        normalized_rows = []


        # ==================================
        # PROCESS PRODUCTS
        # ==================================

        for product in products:


            # ------------------------------
            # CHECK NEW FIELDS
            # ------------------------------

            new_fields = (
                schema_manager.detect_new_fields(
                    product
                )
            )


            # ------------------------------
            # ADD NEW FIELDS
            # ------------------------------

            for field in new_fields:

                schema_manager.add_new_field(
                    field,
                    product.get(field)
                )


            # ------------------------------
            # CHECK MISSING FIELDS
            # ------------------------------

            missing_fields = (
                schema_manager.detect_missing_fields(
                    product
                )
            )


            if missing_fields:

                print(
                    "Fields missing from "
                    "current API record:"
                )

                print(
                    missing_fields
                )

                print(
                    "Existing schema will "
                    "NOT be deleted."
                )


            # ------------------------------
            # NORMALIZE
            # ------------------------------

            normalized_product = (
                normalize_product(
                    product,
                    schema_manager
                )
            )


            normalized_rows.append(
                normalized_product
            )


        # ==================================
        # CREATE DATAFRAME FOR THIS BATCH
        # ==================================

        df = pd.DataFrame(
            normalized_rows
        )


        print("\nNormalized batch:")

        print(df)


        # ==================================
        # LATER:
        # SEND THIS BATCH TO SQL
        # ==================================

        # df.to_sql(...)


        # ----------------------------------
        # BATCH MEMORY CAN NOW BE RELEASED
        # ----------------------------------

        del normalized_rows

        del df


    # ======================================
    # FINAL SCHEMA
    # ======================================

    print("\nFinal schema:")

    for field, metadata in (
        schema_manager.schema.items()
    ):

        print(
            f"{field} -> "
            f"{metadata['column']} "
            f"({metadata['type']})"
        )


if __name__ == "__main__":

    main()