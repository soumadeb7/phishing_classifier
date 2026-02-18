import os
import sys
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv   # ✅ ADD THIS

from src.exception import CustomException


# ✅ LOAD ENVIRONMENT VARIABLES AT IMPORT TIME
load_dotenv()


class PhisingData:
    """
    Export MongoDB collections as pandas DataFrames
    """

    def __init__(self, database_name: str):
        try:
            self.database_name = database_name

            self.mongo_url = os.getenv("MONGO_DB_URL")
            if not self.mongo_url:
                raise Exception("MONGO_DB_URL environment variable is not set")

            # ✅ SINGLE SOURCE OF TRUTH
            self.client = MongoClient(self.mongo_url)

        except Exception as e:
            raise CustomException(e, sys)

    def export_collections_as_dataframe(self):
        print("DEBUG: export_collections_as_dataframe CALLED")

        db = self.client[self.database_name]
        collections = db.list_collection_names()

        print("DEBUG: collections found =", collections)

        for collection_name in collections:
            data = list(db[collection_name].find())
            print(f"DEBUG: {collection_name} document count =", len(data))

            if len(data) == 0:
                continue

            df = pd.DataFrame(data)

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            yield collection_name, df