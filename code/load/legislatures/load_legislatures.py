# Importing libraries
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text 

#load dotenv
load_dotenv()


# Functions
def load_supabase(table_name, schema, mode="replace"):
    database_url = os.getenv("DATABASE_CONNECTION")

    # Create Engine
    engine = create_engine(database_url)

    # Create Schema if not exists
    with engine.connect() as conn:
        conn.execute(text("create schema if not exists bronze"))
        conn.commit()

    # Read Parquet file
    df = pd.read_parquet(f"data/raw/{table_name}/{table_name}.parquet")

    # Save to Bronze laywer
    df.to_sql(
        name= table_name,
        con= engine,
        schema= schema,
        if_exists= mode,
        index=False
    )

# MAIN Code
load_supabase("legislatures","bronze","replace")