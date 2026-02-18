import pandas as pd
from pymongo import MongoClient
import os

# ===== CONFIG =====
MONGO_DB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "phishing_db"
COLLECTION_NAME = "phishing"
CSV_PATH = "upload_data_to_db/phising_08012020_120000.csv"

# ===== CONNECT =====
client = MongoClient(MONGO_DB_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# ===== LOAD CSV =====
df = pd.read_csv(CSV_PATH)
print("Rows in CSV:", len(df))

# ===== INSERT =====
records = df.to_dict(orient="records")
if records:
    collection.insert_many(records)
    print("Data inserted into MongoDB successfully")
else:
    print("CSV is empty")