import time

import pandas as pd

from api_client import APIClient
from extractor import extract_products
from normalizer import normalize_product
from schema_manager import SchemaManager
from sql_data_push import SQLManager


def main() -> None:
    """Run the API to SQL Server pipeline."""

    # ==========================================
    # START
    # ==========================================

    print("==============================")
    print("Starting API pipeline")
    print("==============================\n")


    # ==========================================
    # API AUTHENTICATION
    # ==========================================

    client = APIClient()

    print("Authentication: ", end="")

    client.authenticate()

    print("SUCCESS")


    # ==========================================
    # MANAGERS
    # ==========================================

    schema_manager = SchemaManager()
    sql_manager = SQLManager()


    # ==========================================
    # EXTRACTION
    # ==========================================

    print("Extracting data...")

    all_rows = []

    new_fields = set()
    missing_fields = set()


    for products in extract_products(client):

        for product in products:

            # ----------------------------------
            # Detect new fields
            # ----------------------------------

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


            # ----------------------------------
            # Detect missing fields
            # ----------------------------------

            detected_missing = (
                schema_manager.detect_missing_fields(
                    product
                )
            )

            missing_fields.update(
                detected_missing
            )


            # ----------------------------------
            # Normalize
            # ----------------------------------

            normalized_product = (
                normalize_product(
                    product,
                    schema_manager
                )
            )

            all_rows.append(
                normalized_product
            )


    # ==========================================
    # EXTRACTION RESULT
    # ==========================================

    total_records = len(all_rows)

    print("Extraction: SUCCESS")
    print(
        f"Records extracted: {total_records}"
    )


    # ==========================================
    # SCHEMA
    # ==========================================

    print("\nSchema:")


    if new_fields:

        print(
            f"New fields added: {len(new_fields)}"
        )

        for field in sorted(new_fields):

            print(f"  - {field}")

    else:

        print("New fields added: None")


    if missing_fields:

        print(
            f"Missing fields: "
            f"{len(missing_fields)} (KEPT)"
        )

        for field in sorted(missing_fields):

            print(f"  - {field}")

    else:

        print("Missing fields: None")


    # ==========================================
    # CREATE DATAFRAME
    # ==========================================

    df = pd.DataFrame(
        all_rows
    )


    # ==========================================
    # SQL SERVER
    # ==========================================

    print("\nSQL:")
    print("Table: products")


    try:

        # Create only if table doesn't exist
        sql_manager.create_table(
            df,
            "products"
        )


        # Add new columns without
        # dropping existing columns
        sql_manager.add_new_columns(
            df,
            "products"
        )


        # Insert / update all records
        sql_manager.upsert_data(
            df,
            "products"
        )


        print("Data saved: SUCCESS")
        print(
            f"Records saved: {total_records}"
        )


    except Exception as error:

        print("Data saved: FAILED")
        print(f"Error: {error}")

        raise


    # ==========================================
    # COMPLETE
    # ==========================================

    print("\n==============================")
    print("Pipeline completed: SUCCESS")
    print("==============================")


# ==============================================
# RUN EVERY 24 HOURS
# ==============================================

if __name__ == "__main__":

    while True:

        try:

            main()

        except Exception as error:

            print(
                "\nPipeline completed: FAILED"
            )

            print(
                f"Error: {error}"
            )


        print(
            "\nNext refresh in 24 hours..."
        )

        time.sleep(
            24 * 60 * 60
        )