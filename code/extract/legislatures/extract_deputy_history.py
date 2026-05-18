# IMPORTS
import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine,text


# LOAD VARIABLES
load_dotenv()


# CONFIG
INITIAL_LEGISLATURE = 54
FINAL_LEGISLATURE = 57
TABLE_NAME = "deputy_history"
BASE_URL = ("https://dadosabertos.camara.leg.br/api/v2/deputados")


#  FUNCTIONS

# GET LEGISLATURES
def get_deputy_history(deputy_id):

    print(f"Collecting deputy history for deputy {deputy_id}")

    url = f"{BASE_URL}/{deputy_id}/historico"

    max_retries = 10

    for attempt in range(max_retries):

        try:

            response = requests.get(
                url,
                timeout=600
            )

            if response.status_code == 504:
                raise Exception("Gateway Timeout")

            response.raise_for_status()

            data = response.json()

            page_data = data.get("dados", [])

            if not page_data:
                return pd.DataFrame()

            return pd.DataFrame(page_data)

        except Exception as e:

            print(
                f"Attempt {attempt + 1} failed "
                f"for deputy {deputy_id}: {e}"
            )

            time.sleep(2)

    return pd.DataFrame()


# SAVE PARQUET FUNCTION
def save_parquet(df, table_name):

    # Create directory
    path = f"data/raw/{table_name}"

    os.makedirs(path, exist_ok=True)

    # File path
    file_path = (
        f"{path}/{table_name}.parquet"
    )

    # Save parquet
    df.to_parquet(file_path,index=False)

    print(f"Parquet saved at: {file_path}")


def get_deputy_ids(engine):

    query = text("""
        SELECT DISTINCT id
        FROM bronze.legislatures
        WHERE 1=1
        LIMIT 10000000
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        return [row[0] for row in result]


# =========================
# MAIN
# =========================
def main():

    engine = create_engine(os.getenv("DATABASE_CONNECTION"))

    deputy_list = get_deputy_ids(engine)

    rows = []

    for deputy_id in deputy_list:

        data = get_deputy_history(deputy_id)

        if not data.empty:
            rows.append(data)

    if not rows:
        print("No data collected.")
        
    # Concatenating dataframes
    final_df = pd.concat(rows, ignore_index=True)

    print(f"Total rows collected: {len(final_df)}")

    save_parquet(final_df, TABLE_NAME)


# EXECUTION

if __name__ == "__main__":
    main()