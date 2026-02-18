import sys
import os
from pathlib import Path
from dataclasses import dataclass
import pandas as pd

from src.constant import *
from src.exception import CustomException
from src.logger import logging
from src.data_access.phising_data import PhisingData
from src.utils.main_utils import MainUtils


@dataclass
class DataIngestionConfig:
    data_ingestion_dir: str = os.path.join(artifact_folder, "data_ingestion")


class DataIngestion:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.utils = MainUtils()

    def export_data_into_raw_data_dir(self) -> None:
        """
        Reads data from MongoDB, converts all column names and URLs to lowercase,
        and saves each collection as a CSV in artifacts/data_ingestion.
        """
        try:
            logging.info("Exporting data from MongoDB")

            raw_batch_files_path = self.data_ingestion_config.data_ingestion_dir
            os.makedirs(raw_batch_files_path, exist_ok=True)

            phishing_data = PhisingData(database_name=MONGO_DATABASE_NAME)

            for collection_name, dataset in phishing_data.export_collections_as_dataframe():
                if dataset.empty:
                    logging.warning(f"Collection {collection_name} is empty. Skipping.")
                    continue

                logging.info(f"Shape of {collection_name}: {dataset.shape}")

                # Convert column names to lowercase
                dataset.columns = [col.lower() for col in dataset.columns]

                # Convert URLs to lowercase if column exists
                if 'url' in dataset.columns:
                    dataset['url'] = dataset['url'].str.lower()

                # Save CSV
                file_path = os.path.join(raw_batch_files_path, f"{collection_name}.csv")
                dataset.to_csv(file_path, index=False)
                logging.info(f"Saved {collection_name} to {file_path}")

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_ingestion(self) -> Path:
        """
        Initiates data ingestion and returns the folder path containing CSVs.
        """
        try:
            logging.info("Entered initiate_data_ingestion")
            self.export_data_into_raw_data_dir()
            logging.info("Exited initiate_data_ingestion")
            # Return the directory path, not a list of files
            return Path(self.data_ingestion_config.data_ingestion_dir)
        except Exception as e:
            raise CustomException(e, sys)