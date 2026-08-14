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

        inspector = inspect(self.engine)

        return inspector.has_table(
            table_name
        )


    # ======================================
    # CREATE TABLE
    # ======================================

    def create_table(
        self,
        df,
        table_name
    ):

        if not self.table_exists(
            table_name
        ):

            # Create table structure
            df.head(0).to_sql(
                table_name,
                self.engine,
                if_exists="replace",
                index=False
            )

            # Add primary key
            with self.engine.begin() as connection:

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE [{table_name}]
                        ADD CONSTRAINT PK_{table_name}
                        PRIMARY KEY (product_id)
                        """
                    )
                )

            print(
                f"SQL table created: {table_name}"
            )


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


    # ======================================
    # UPSERT DATA
    # ======================================

    def upsert_data(
        self,
        df,
        table_name
    ):

        if df.empty:

            return


        # ==================================
        # GET SQL COLUMNS
        # ==================================

        sql_columns = self.get_columns(
            table_name
        )


        # Keep only columns that
        # currently exist in SQL

        df = df[
            [
                column
                for column in df.columns
                if column in sql_columns
            ]
        ]


        # ==================================
        # PROCESS EACH PRODUCT
        # ==================================

        with self.engine.begin() as connection:

            for _, row in df.iterrows():

                product_id = row[
                    "product_id"
                ]


                # --------------------------
                # CHECK PRODUCT
                # --------------------------

                result = connection.execute(
                    text(
                        f"""
                        SELECT COUNT(*)
                        FROM [{table_name}]
                        WHERE product_id = :product_id
                        """
                    ),
                    {
                        "product_id": product_id
                    }
                )

                exists = (
                    result.scalar() > 0
                )


                # ==========================
                # UPDATE EXISTING PRODUCT
                # ==========================

                if exists:

                    update_columns = [
                        column
                        for column in df.columns
                        if column != "product_id"
                    ]


                    if update_columns:

                        set_clause = ", ".join(
                            [
                                f"[{column}] = :{column}"
                                for column
                                in update_columns
                            ]
                        )


                        query = f"""
                            UPDATE [{table_name}]
                            SET {set_clause}
                            WHERE product_id = :product_id
                        """


                        values = {
                            column: row[column]
                            for column
                            in update_columns
                        }


                        values[
                            "product_id"
                        ] = product_id


                        connection.execute(
                            text(query),
                            values
                        )


                # ==========================
                # INSERT NEW PRODUCT
                # ==========================

                else:

                    columns = list(
                        df.columns
                    )


                    column_names = ", ".join(
                        f"[{column}]"
                        for column in columns
                    )


                    parameter_names = ", ".join(
                        f":{column}"
                        for column in columns
                    )


                    query = f"""
                        INSERT INTO [{table_name}]
                        ({column_names})
                        VALUES
                        ({parameter_names})
                    """


                    values = {
                        column: row[column]
                        for column in columns
                    }


                    connection.execute(
                        text(query),
                        values
                    )