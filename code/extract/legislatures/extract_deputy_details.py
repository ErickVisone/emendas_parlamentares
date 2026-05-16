# IMPORTS
import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import text, create_engine


# LOAD VARIABLES
load_dotenv()


# CONFIG
TABLE_NAME = "deputy_details"
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados/"


# =========================
# HELPERS
# =========================

def flatten_dict(d, parent_key="", sep="_"):
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())

        elif isinstance(v, list):
            # lista vira string (compatível com SQL)
            items.append((new_key, "|".join(map(str, v)) if v else None))

        else:
            items.append((new_key, v))

    return dict(items)


def sanitize_df(df):

    def clean(x):
        if isinstance(x, np.ndarray):
            return x.tolist() if x.size > 0 else None

        if isinstance(x, list):
            return "|".join(map(str, x)) if len(x) > 0 else None

        if isinstance(x, dict):
            return str(x)

        return x

    return df.apply(lambda col: col.map(clean))


# =========================
# DB
# =========================

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
# API
# =========================

def get_deputy_details(deputy_id):

    print(f"Collecting deputy {deputy_id}")

    url = f"{BASE_URL}{deputy_id}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data.get("dados", {})

    except Exception as e:
        print(f"Error deputy {deputy_id}: {e}")
        return {}


# =========================
# SAVE
# =========================

def save_parquet(df, table_name):

    path = f"data/raw/{table_name}"
    os.makedirs(path, exist_ok=True)

    file_path = f"{path}/{table_name}.parquet"

    df.to_parquet(file_path, index=False)

    print(f"Parquet saved at: {file_path}")


# =========================
# MAIN
# =========================

def main():

    engine = create_engine(os.getenv("DATABASE_CONNECTION"))

    deputy_list = get_deputy_ids(engine)

    print(f"Total deputies to process: {len(deputy_list)}")

    rows = []

    for deputy_id in deputy_list:

        data = get_deputy_details(deputy_id)

        if data:

            flat = flatten_dict(data)
            rows.append(flat)

    if not rows:
        print("No data collected.")
        return

    # DataFrame final (2D correto)
    final_df = pd.DataFrame(rows)

    # limpeza final (remove numpy/list/dict)
    final_df = sanitize_df(final_df)

    print(f"Total rows collected: {len(final_df)}")

    save_parquet(final_df, TABLE_NAME)


# =========================
# EXECUTION
# =========================

if __name__ == "__main__":
    main()