import pandas as pd
import time
from google.cloud import storage

path_to_private_key = './defaust-343537e24181.json'
client = storage.Client.from_service_account_json(json_credentials_path=path_to_private_key)

# The NEW bucket on GCS in which to write the CSV file
bucket = client.bucket('hedging-bot-statistics')

def save_on_cloud():
    df = pd.read_csv('stat.csv')
    blob = bucket.blob('stat.csv')
    blob.upload_from_string(df.to_csv(), 'text/csv')

while True:
    try: save_on_cloud()
    except pd.errors.EmptyDataError:
        pass
    time.sleep(5)