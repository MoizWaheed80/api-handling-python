import urllib.parse
import json
from typing import Any

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
    """Manage SQL Server table creation, schema changes, and data loading."""

    def __init__(self) -> None:
        """Create the SQL Server database engine."""

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
            "mssql+pyodbc:///"
            f"?odbc_connect={params}",
            pool_pre_ping=True
        )


    # ==================================================
    # CHECK TABLE
    # ==================================================

    def table_exists(
        self,
        table_name: str
    ) -> bool:
        """Return True when the SQL table already exists."""

        inspector = inspect(self.engine)

        return inspector.has_table(
            table_name
        )


    # ==================================================
    # CREATE TABLE
    # ==================================================

    def create_table(
        self,
        df: pd.DataFrame,
        table_name: str
    ) -> None:
        """Create the table only when it does not already exist."""

        if self.table_exists(table_name):
            return


        if df.empty:
            raise ValueError(
                "Cannot create SQL table from an empty DataFrame."
            )


        try:

            # Create table structure only.
            df.head(0).to_sql(
                table_name,
                self.engine,
                if_exists="fail",
                index=False
            )


            # Make product_id NOT NULL and create
            # the primary key.
            with self.engine.begin() as connection:

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE [{table_name}]
                        ALTER COLUMN [product_id] INT NOT NULL
                        """
                    )
                )

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
                "SQL table created: SUCCESS"
            )


        except Exception as error:

            print(
                "SQL table creation: FAILED"
            )

            raise RuntimeError(
                f"Could not create SQL table "
                f"'{table_name}': {error}"
            ) from error


    # ==================================================
    # GET SQL COLUMNS
    # ==================================================

    def get_columns(
        self,
        table_name: str
    ) -> set[str]:
        """Return the existing SQL column names."""

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


    # ==================================================
    # DETECT SQL DATA TYPE
    # ==================================================

    @staticmethod
    def detect_sql_type(
        series: pd.Series
    ) -> str:
        """Determine an appropriate SQL Server data type."""

        if pd.api.types.is_bool_dtype(series):
            return "BIT"


        if pd.api.types.is_integer_dtype(series):
            return "INT"


        if pd.api.types.is_float_dtype(series):
            return "FLOAT"


        return "NVARCHAR(MAX)"


    # ==================================================
    # ADD NEW COLUMNS
    # ==================================================

    def add_new_columns(
        self,
        df: pd.DataFrame,
        table_name: str
    ) -> None:
        """Add API fields that do not yet exist in SQL Server."""

        sql_columns = self.get_columns(
            table_name
        )

        python_columns = set(
            df.columns
        )

        new_columns = (
            python_columns - sql_columns
        )


        if not new_columns:
            return


        try:

            with self.engine.begin() as connection:

                for column in sorted(new_columns):

                    sql_type = self.detect_sql_type(
                        df[column]
                    )

                    connection.execute(
                        text(
                            f"""
                            ALTER TABLE [{table_name}]
                            ADD [{column}] {sql_type}
                            """
                        )
                    )


                    print(
                        f"SQL column added: {column}"
                    )


        except Exception as error:

            print(
                "SQL schema update: FAILED"
            )

            raise RuntimeError(
                f"Could not add new SQL column: "
                f"{error}"
            ) from error


    # ==================================================
    # CONVERT PYTHON VALUES FOR SQL
    # ==================================================

    @staticmethod
    def prepare_value(
        value: Any
    ) -> Any:
        """Convert Python/Pandas values into SQL-compatible values."""

        # Pandas missing value
        if pd.isna(value) and not isinstance(
            value,
            (dict, list)
        ):
            return None


        # Dictionary / list
        if isinstance(
            value,
            (dict, list)
        ):

            return json.dumps(
                value,
                ensure_ascii=False
            )


        # Pandas / NumPy scalar
        if hasattr(value, "item"):

            try:
                return value.item()

            except (ValueError, AttributeError):
                pass


        return value


    # ==================================================
    # UPSERT DATA
    # ==================================================

    def upsert_data(
        self,
        df: pd.DataFrame,
        table_name: str
    ) -> None:
        """
        Insert new records and update existing records
        using product_id as the key.
        """

        if df.empty:

            print(
                "No data to save."
            )

            return


        sql_columns = self.get_columns(
            table_name
        )


        # Keep only columns that exist in SQL.
        df = df[
            [
                column
                for column in df.columns
                if column in sql_columns
            ]
        ]


        if "product_id" not in df.columns:

            raise ValueError(
                "product_id is required for upsert."
            )


        inserted = 0
        updated = 0


        try:

            with self.engine.begin() as connection:

                for _, row in df.iterrows():

                    product_id = self.prepare_value(
                        row["product_id"]
                    )


                    # ----------------------------------
                    # CHECK IF PRODUCT EXISTS
                    # ----------------------------------

                    result = connection.execute(
                        text(
                            f"""
                            SELECT COUNT(*)
                            FROM [{table_name}]
                            WHERE [product_id] = :product_id
                            """
                        ),
                        {
                            "product_id": product_id
                        }
                    )

                    exists = (
                        result.scalar() > 0
                    )


                    # ==================================
                    # UPDATE EXISTING RECORD
                    # ==================================

                    if exists:

                        update_columns = [
                            column
                            for column in df.columns
                            if column != "product_id"
                        ]


                        if update_columns:

                            set_clause = ", ".join(
                                f"[{column}] = :{column}"
                                for column
                                in update_columns
                            )


                            values = {
                                column: self.prepare_value(
                                    row[column]
                                )
                                for column
                                in update_columns
                            }


                            values[
                                "product_id"
                            ] = product_id


                            connection.execute(
                                text(
                                    f"""
                                    UPDATE [{table_name}]
                                    SET {set_clause}
                                    WHERE [product_id] =
                                          :product_id
                                    """
                                ),
                                values
                            )


                        updated += 1


                    # ==================================
                    # INSERT NEW RECORD
                    # ==================================

                    else:

                        columns = list(
                            df.columns
                        )


                        column_names = ", ".join(
                            f"[{column}]"
                            for column
                            in columns
                        )


                        parameter_names = ", ".join(
                            f":{column}"
                            for column
                            in columns
                        )


                        values = {
                            column: self.prepare_value(
                                row[column]
                            )
                            for column
                            in columns
                        }


                        connection.execute(
                            text(
                                f"""
                                INSERT INTO [{table_name}]
                                ({column_names})
                                VALUES
                                ({parameter_names})
                                """
                            ),
                            values
                        )


                        inserted += 1


            # ==================================
            # SUCCESS
            # ==================================

            print(
                "Data saved: SUCCESS"
            )

            print(
                f"Records saved: "
                f"{inserted + updated}"
            )


            print(
                f"  Inserted: {inserted}"
            )

            print(
                f"  Updated: {updated}"
            )


        except Exception as error:

            print(
                "Data saved: FAILED"
            )

            raise RuntimeError(
                f"Could not save data to SQL Server: "
                f"{error}"
            ) from error