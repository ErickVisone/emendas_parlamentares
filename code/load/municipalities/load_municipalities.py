# Importing libraries
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text 

# Load dotenv and getting credentials
load_dotenv()
database_url = os.getenv("DATABASE_CONNECTION")

# Creating engine
engine = create_engine(database_url)

# Creating schema bronze if not exists
with engine.connect() as conn:
    conn.execute(text("create schema if not exists bronze"))
    conn.commit()

# Reading parque file
df = pd.read_parquet("data/raw/municipalities/municipalities.parquet")

# Salve into bronze
df.to_sql(
    name= "municipalities",
    con= engine,
    schema= "bronze",
    if_exists= "replace",
    index= False
)