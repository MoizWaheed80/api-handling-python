import pandas as pd
import time

from api_client import APIClient
from extractor import extract_products
from schema_manager import SchemaManager
from normalizer import normalize_product


def main():

    # ======================================
    # API CLIENT
    # ======================================

    client = APIClient()


    # ======================================
    # AUTHENTICATION
    # ======================================

    print("Authentication: ", end="")

    client.authenticate()

    print("SUCCESS")


    # ======================================
    # SCHEMA MANAGER
    # ======================================

    schema_manager = SchemaManager()


    # ======================================
    # TRACK CHANGES
    # ======================================

    new_fields = set()

    missing_fields = set()

    total_records = 0


    # ======================================
    # EXTRACTION
    # ======================================

    print("Extracting data...")


    for products in extract_products(client):


        # ==================================
        # PROCESS PRODUCTS
        # ==================================

        normalized_rows = []


        for product in products:

            total_records += 1


            # ------------------------------
            # CHECK NEW FIELDS
            # ------------------------------

            detected_new = (
                schema_manager.detect_new_fields(
                    product
                )
            )


            for field in detected_new:

                schema_manager.add_new_field(
                    field,
                    product.get(field)
                )

                new_fields.add(field)


            # ------------------------------
            # CHECK MISSING FIELDS
            # ------------------------------

            detected_missing = (
                schema_manager.detect_missing_fields(
                    product
                )
            )


            for field in detected_missing:

                missing_fields.add(field)


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
        # CREATE DATAFRAME
        # ==================================

        df = pd.DataFrame(
            normalized_rows
        )


        # ==================================
        # SQL WILL GO HERE LATER
        # ==================================

        # df.to_sql(...)


        # Release batch memory
        del normalized_rows

        del df


    # ======================================
    # SHOW SCHEMA CHANGES
    # ======================================

    print("\nSchema update:")


    # --------------------------------------
    # NEW FIELDS
    # --------------------------------------

    if new_fields:

        print("\nNew fields:")

        for field in sorted(new_fields):

            print(f"- {field}")

    else:

        print("\nNew fields: None")


    # --------------------------------------
    # MISSING FIELDS
    # --------------------------------------

    if missing_fields:

        print("\nMissing fields:")

        for field in sorted(missing_fields):

            print(f"- {field} (KEPT)")

    else:

        print("\nMissing fields: None")


    # ======================================
    # FINAL STATUS
    # ======================================

    print(
        f"\nProcessing: SUCCESS"
    )

    print(
        f"Records processed: {total_records}"
    )

    print(
        "Schema status: OK"
    )

    print(
        "Pipeline completed successfully."
    )


# ==========================================
# RUN EVERY 24 HOURS
# ==========================================

if __name__ == "__main__":

    while True:

        print(
            "\n=============================="
        )

        print(
            "Starting API pipeline"
        )

        print(
            "=============================="
        )


        try:

            main()

        except Exception as error:

            print(
                f"\nPipeline failed: {error}"
            )


        print(
            "\nWaiting 24 hours..."
        )


        time.sleep(
            24 * 60 * 60
        )