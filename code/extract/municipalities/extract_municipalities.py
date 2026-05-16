import pandas as pd
import requests

# URL of minicipalities in Brazil
url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"

# Get the minicipalities
try:
    response = requests.get(
        url=url
    )
    
    if response.status_code != 200:
        raise Exception
    else:
        data = response.json()

        #Pandas to flatten 
        df = pd.json_normalize(data)
        df.to_parquet(
            f"data/raw/municipalities/municipalities.parquet",
            index=False
        )

except Exception as e:
    print("Error:", e)