from pathlib import Path
import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "generated"


conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)


files = {
    "CUSTOMERS": "customers.csv",
    "PRODUCTS": "products.csv",
    "CONTRACTS": "contracts.csv",
    "ORDERS": "orders.csv",
    "PAYMENTS": "payments.csv",
    "TRANSACTIONS": "transactions.csv",
}


for table_name, file_name in files.items():

    file_path = DATA_DIR / file_name

    print(f"Loading {file_name}...")

    df = pd.read_csv(file_path)

    # Snowflake convention
    df.columns = [column.upper() for column in df.columns]

    success, chunks, rows, output = write_pandas(
        conn,
        df,
        table_name,
        auto_create_table=True,
        overwrite=True,
    )

    print(
        f"{table_name}: "
        f"{rows:,} rows loaded"
    )


conn.close()

print()
print("All files loaded successfully.")
