# Importing libraries
import pandas as pd
import requests
from dotenv import load_dotenv

#load dotenv
load_dotenv()

# Functions
def get_legislatures(id, initial_page=1): 

    all_dfs = []
    initial_page = 1

    while True:

        # URL for legislatures in Brazil
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura={id}&ordem=ASC&ordenarPor=nome&pagina={initial_page}"

        try:
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception (f"Error: {response.status_code}")
            
            data = response.json()

            # Data per page
            page_data = data["dados"]

            if not page_data:
                break
            print(f"Legislature {id} - Page {initial_page}")

            #Converts to DF
            df_page = pd.DataFrame(page_data)

            #add to list
            all_dfs.append(df_page)

            initial_page +=1


        except Exception as e:
            print("Error:", e)
            break
    
    final_df = pd.concat(all_dfs, ignore_index=True)

    return final_df

# MAIN Code
dfs = []
INITIAL_LEGISLATURE = 54
FINAL_LEGISLATURE = 57

for legislature in range(INITIAL_LEGISLATURE, FINAL_LEGISLATURE + 1):

    print(f"Initiating data collection...")
    print(f"Collecting legislature: {legislature}")
    # Extract Data
    data = get_legislatures(legislature)

    # Append
    print(f"Appending to df...")
    dfs.append(data)

# Concatennate dataframens
df = pd.concat(dfs, ignore_index=True)

# Save Parquet =
df.to_parquet(
    f"data/raw/legislatures/legislatures.parquet",
    index= False
)
