from src.components.data_ingestion import DataIngestion
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    di = DataIngestion()
    artifact_path = di.initiate_data_ingestion()
    print("Artifacts created at:", artifact_path)