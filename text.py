from sqlalchemy import create_engine, text
import urllib.parse

server = r"Abdul_Moiz\SQLEXPRESS"
database = "Api_data"
driver = "ODBC Driver 18 for SQL Server"

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

params = urllib.parse.quote_plus(connection_string)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}"
)

with engine.connect() as connection:

    result = connection.execute(
        text("SELECT @@SERVERNAME")
    )

    print("SQL Server connection successful!")
    print("Server:", result.scalar())