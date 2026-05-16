# IMPORTS
import os
import requests
import pandas as pd
from dotenv import load_dotenv


# LOAD VARIABLES
load_dotenv()


# CONFIG
INITIAL_LEGISLATURE = 54
FINAL_LEGISLATURE = 57
TABLE_NAME = "legislature_details"
BASE_URL = ("https://dadosabertos.camara.leg.br/api/v2/legislaturas")


#  FUNCTIONS

# GET LEGISLATURES
def get_legislatures_details(legislature_id, page=1):

    all_dfs = []

    page = 1

    while True:
        print(f"Collecting details for legislature {legislature_id} | Page {page}")

        url = (f"{BASE_URL}?id={legislature_id}&&pagina={page}&ordem=DESC&ordenarPor=id")

        try:
            response = requests.get(url,timeout=30)

            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")

            data = response.json()

            page_data = data.get("dados", [])

            # Stop pagination
            if not page_data:
                print(f"No more details for legislature {legislature_id}")
                break

            # Convert page data into DataFrame
            df_page = pd.DataFrame(page_data)

            # Append page DataFrame
            all_dfs.append(df_page)

            # Next page
            page += 1

        except Exception as e:

            print(f"Error collecting {legislature_id} details: {e}")
            break

    # Return empty DataFrame if no data
    if not all_dfs:
        return pd.DataFrame()

    # Concatenate all pages
    final_df = pd.concat(all_dfs,ignore_index=True)

    return final_df


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


# =========================
# MAIN
# =========================
def main():

    dfs = []

    for legislature in range(INITIAL_LEGISLATURE,FINAL_LEGISLATURE + 1):

        print("\n========================")
        print(f"Starting legislature: {legislature}")
        print("========================")

        # Extract
        data = get_legislatures_details(legislature)

        # Append only if not empty
        if not data.empty:

            dfs.append(data)
            print(f"Legislature details for {legislature} added successfully")

        else:
            print(f"No details for legislature {legislature}")

    # Concatenate all legislatures
    if dfs:

        final_df = pd.concat(dfs,ignore_index=True)
        print(f"\nTotal rows collected: {len(final_df)}")

        # Save parquet
        save_parquet(df=final_df,table_name=TABLE_NAME)

    else:
        print("No data collected.")


# EXECUTION

if __name__ == "__main__":
    main()