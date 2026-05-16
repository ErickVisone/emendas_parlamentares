# Importing libraries
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Load dotenv and getting credentials
load_dotenv()

database_url = os.getenv("DATABASE_CONNECTION")

if not database_url:
    raise ValueError("DATABASE_CONNECTION not found in environment variables")


# Create engine
engine = create_engine(database_url)


# FUNCTIONS

# Load from dataframe
def load_supabase(df, table_name, schema="bronze", mode="replace"):

    # Create schema if not exists
    with engine.connect() as conn:
        conn.execute(
            text(f"create schema if not exists {schema}")
        )
        conn.commit()

    # Load into database
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=mode,
        index=False
    )

    print(f"Loaded {table_name} into {schema}")


# Load from parquet files
def load_supabase_from_parquet(
    table_name,
    schema="bronze",
    mode="replace"
):

    path = f"data/raw/{table_name}/{table_name}.parquet"

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")

    df = pd.read_parquet(path)

    # Create schema if not exists
    with engine.connect() as conn:
        conn.execute(
            text(f"create schema if not exists {schema}")
        )
        conn.commit()

    # Load into database
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=mode,
        index=False
    )

    print(f"Loaded {table_name} from parquet into {schema}")