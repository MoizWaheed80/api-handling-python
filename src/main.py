import pandas as pd
import time

from api_client import APIClient
from extractor import extract_products
from schema_manager import SchemaManager
from normalizer import normalize_product
from sql_data_push import SQLManager

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
    # MANAGERS
    # ======================================

    schema_manager = SchemaManager()

    sql_manager = SQLManager()


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


    for products in extract_products(
        client
    ):

        normalized_rows = []


        # ==================================
        # PROCESS PRODUCTS
        # ==================================

        for product in products:

            total_records += 1


            # ------------------------------
            # NEW FIELDS
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
            # MISSING FIELDS
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
        # DATAFRAME
        # ==================================

        df = pd.DataFrame(
            normalized_rows
        )


        # ==================================
        # SQL SERVER
        # ==================================

        table_name = "products"


        # Create table if necessary

        sql_manager.create_table(
            df,
            table_name
        )


        # Add new API fields

        sql_manager.add_new_columns(
            df,
            table_name
        )


        # Insert new / update existing

        sql_manager.upsert_data(
            df,
            table_name
        )


        # Release batch memory

        del normalized_rows

        del df


    # ======================================
    # REPORT
    # ======================================

    print("\nSchema update:")


    if new_fields:

        print("\nNew fields:")

        for field in sorted(
            new_fields
        ):

            print(f"- {field}")

    else:

        print("\nNew fields: None")


    if missing_fields:

        print("\nMissing fields:")

        for field in sorted(
            missing_fields
        ):

            print(
                f"- {field} (KEPT)"
            )

    else:

        print("\nMissing fields: None")


    # ======================================
    # FINAL STATUS
    # ======================================

    print(
        f"\nProcessing: SUCCESS"
    )

    print(
        f"Records processed: "
        f"{total_records}"
    )

    print(
        "SQL load: SUCCESS"
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