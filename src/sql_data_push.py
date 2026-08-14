import urllib.parse

import pandas as pd

from sqlalchemy import (
    create_engine,
    inspect,
    text
)

from config import (
    SQL_SERVER,
    SQL_DATABASE,
    SQL_DRIVER
)


class SQLManager:

    def __init__(self):

        # ======================================
        # SQL SERVER CONNECTION
        # Windows Authentication
        # ======================================

        connection_string = (
            f"DRIVER={{{SQL_DRIVER}}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        params = urllib.parse.quote_plus(
            connection_string
        )

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}"
        )


    # ======================================
    # CHECK TABLE
    # ======================================

    def table_exists(self, table_name):

        inspector = inspect(
            self.engine
        )

        return inspector.has_table(
            table_name
        )


    # ======================================
    # DROP TABLE IF EXISTS
    # ======================================

    def drop_table_if_exists(
        self,
        table_name
    ):

        try:

            if self.table_exists(
                table_name
            ):

                with self.engine.begin() as connection:

                    connection.execute(
                        text(
                            f"""
                            DROP TABLE [{table_name}]
                            """
                        )
                    )

                print(
                    f"Existing table dropped: {table_name}"
                )

            else:

                print(
                    f"Table does not exist: {table_name}"
                )


        except Exception as error:

            print(
                f"Error dropping table: {error}"
            )

            raise


    # ======================================
    # CREATE TABLE
    # ======================================

    def create_table(
        self,
        df,
        table_name
    ):

        try:

            # ==================================
            # DROP EXISTING TABLE
            # ==================================

            self.drop_table_if_exists(
                table_name
            )


            # ==================================
            # CREATE NEW TABLE
            # ==================================

            df.head(0).to_sql(
                table_name,
                self.engine,
                if_exists="fail",
                index=False
            )


            # ==================================
            # PRODUCT ID NOT NULL
            # ==================================

            with self.engine.begin() as connection:

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE [{table_name}]
                        ALTER COLUMN [product_id] INT NOT NULL
                        """
                    )
                )


            # ==================================
            # PRIMARY KEY
            # ==================================

            with self.engine.begin() as connection:

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE [{table_name}]
                        ADD CONSTRAINT PK_{table_name}
                        PRIMARY KEY ([product_id])
                        """
                    )
                )


            print(
                f"SQL table created: {table_name}"
            )


        except Exception as error:

            print(
                f"Error creating table: {error}"
            )

            raise


    # ======================================
    # GET SQL COLUMNS
    # ======================================

    def get_columns(
        self,
        table_name
    ):

        inspector = inspect(
            self.engine
        )

        columns = inspector.get_columns(
            table_name
        )

        return {
            column["name"]
            for column in columns
        }


    # ======================================
    # ADD NEW COLUMNS
    # ======================================

    def add_new_columns(
        self,
        df,
        table_name
    ):

        try:

            sql_columns = self.get_columns(
                table_name
            )

            python_columns = set(
                df.columns
            )

            new_columns = (
                python_columns - sql_columns
            )


            for column in new_columns:

                # ------------------------------
                # Determine SQL data type
                # ------------------------------

                if pd.api.types.is_integer_dtype(
                    df[column]
                ):

                    sql_type = "INT"

                elif pd.api.types.is_float_dtype(
                    df[column]
                ):

                    sql_type = "FLOAT"

                elif pd.api.types.is_bool_dtype(
                    df[column]
                ):

                    sql_type = "BIT"

                else:

                    sql_type = "NVARCHAR(MAX)"


                # ------------------------------
                # Add column
                # ------------------------------

                query = f"""
                    ALTER TABLE [{table_name}]
                    ADD [{column}] {sql_type}
                """


                with self.engine.begin() as connection:

                    connection.execute(
                        text(query)
                    )


                print(
                    f"SQL column added: {column}"
                )


        except Exception as error:

            print(
                f"Error adding SQL columns: {error}"
            )

            raise


    # ======================================
    # INSERT DATA
    # ======================================

    def upsert_data(
        self,
        df,
        table_name
    ):

        try:

            if df.empty:

                print(
                    "No data to insert."
                )

                return


            # ==================================
            # GET SQL COLUMNS
            # ==================================

            sql_columns = self.get_columns(
                table_name
            )


            # Keep only columns that
            # exist in SQL

            df = df[
                [
                    column
                    for column in df.columns
                    if column in sql_columns
                ]
            ]


            # ==================================
            # INSERT DATA
            # ==================================

            df.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False
            )


            print(
                f"SQL data inserted: {len(df)} records"
            )


        except Exception as error:

            print(
                f"Error inserting data: {error}"
            )

            raise