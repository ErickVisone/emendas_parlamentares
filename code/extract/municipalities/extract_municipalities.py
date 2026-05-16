import os
import pandas as pd
import requests


url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"

output_path = "data/raw/municipalities"

os.makedirs(output_path, exist_ok=True)

try:
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    df = pd.json_normalize(data)

    df.to_parquet(
        f"{output_path}/municipalities.parquet",
        index=False
    )

    print("Municipalities saved successfully")

except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")