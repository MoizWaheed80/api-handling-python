import pandas as pd
import time

from api_client import APIClient
from extractor import extract_products
from schema_manager import SchemaManager
from normalizer import normalize_product
from sql_data_push import SQLManager


def main():

    # ======================================
    # SETUP
    # ======================================

    client = APIClient()

    schema_manager = SchemaManager()

    sql_manager = SQLManager()


    # ======================================
    # AUTHENTICATION
    # ======================================

    try:

        client.authenticate()

        print("Authentication: SUCCESS")

    except Exception:

        print("Authentication: FAILED")

        return


    # ======================================
    # EXTRACTION
    # ======================================

    print("Extracting data...")

    normalized_rows = []

    new_fields = set()

    missing_fields = set()

    total_records = 0


    try:

        for products in extract_products(client):

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


        print("Extraction: SUCCESS")

        print(
            f"Records extracted: {total_records}"
        )


    except Exception:

        print("Extraction: FAILED")

        return


    # ======================================
    # SCHEMA STATUS
    # ======================================

    print("\nSchema:")


    if new_fields:

        print(
            f"New fields added: {len(new_fields)}"
        )

        for field in sorted(new_fields):

            print(
                f"  - {field}"
            )

    else:

        print("New fields added: None")


    if missing_fields:

        print(
            f"Missing fields: {len(missing_fields)} "
            f"(KEPT)"
        )

        for field in sorted(missing_fields):

            print(
                f"  - {field}"
            )

    else:

        print(
            "Missing fields: None"
        )


    # ======================================
    # DATAFRAME
    # ======================================

    df = pd.DataFrame(
        normalized_rows
    )


    # ======================================
    # SQL SERVER
    # ======================================

    table_name = "products"

    print("\nSQL:")

    print(
        f"Table: {table_name}"
    )


    # ======================================
    # RECREATE TABLE
    # ======================================

    try:

        sql_manager.create_table(
            df,
            table_name
        )

        print(
            "Table recreated: SUCCESS"
        )


    except Exception:

        print(
            "Table recreated: FAILED"
        )

        print(
            "Error: Could not create SQL table."
        )

        return


    # ======================================
    # INSERT DATA
    # ======================================

    try:

        sql_manager.upsert_data(
            df,
            table_name
        )

        print(
            "Data inserted: SUCCESS"
        )

        print(
            f"Records inserted: {total_records}"
        )


    except Exception:

        print(
            "Data inserted: FAILED"
        )

        print(
            "Error: Could not insert data into SQL Server."
        )

        return


    # ======================================
    # FINAL STATUS
    # ======================================

    print("\n==============================")

    print(
        "Pipeline completed: SUCCESS"
    )

    print("==============================")


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
            "==============================\n"
        )


        try:

            main()

        except Exception:

            print(
                "\nPipeline completed: FAILED"
            )


        print(
            "\nNext refresh in 24 hours..."
        )


        time.sleep(
            24 * 60 * 60
        )