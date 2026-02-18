import sys
import os
import numpy as np
import pandas as pd
import pickle
import yaml
import boto3

from src.constant import *
from src.exception import CustomException
from src.logger import logging


class MainUtils:
    def __init__(self) -> None:
        print(">>> MainUtils INIT CALLED")
        pass

    def read_yaml_file(self, filename: str) -> dict:
        try:
            with open(filename, "r") as yaml_file:
                return yaml.safe_load(yaml_file)
        except Exception as e:
            raise CustomException(e, sys) from e

    def read_schema_config_file(self) -> dict:
        try:
            schema_config = self.read_yaml_file(
                os.path.join("config", "schema.yaml")
            )
            return schema_config
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def save_object(file_path: str, obj: object) -> None:
        try:
            with open(file_path, "wb") as file_obj:
                pickle.dump(obj, file_obj)
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def load_object(file_path: str) -> object:
        try:
            with open(file_path, "rb") as file_obj:
                obj = pickle.load(file_obj)
            return obj
        except Exception as e:
            raise CustomException(e, sys) from e

    # 🔥 MUST BE INSTANCE METHOD
    def upload_file(self, from_filename: str, bucket_name: str, to_filename: str):
        print(">>> upload_file CALLED")
        print(">>> TYPE:", type(self))
        print(">>> FROM:", from_filename)
        print(">>> BUCKET:", bucket_name)
        print(">>> TO:", to_filename)

        logging.info("Skipping S3 upload (local dev)")
        return

    @staticmethod
    def download_model(bucket_name: str, bucket_file_name: str, dest_file_name: str):
        try:
            s3_client = boto3.client("s3")
            s3_client.download_file(bucket_name, bucket_file_name, dest_file_name)
            return dest_file_name
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def remove_unwanted_spaces(data: pd.DataFrame) -> pd.DataFrame:
        try:
            df_without_spaces = data.apply(
                lambda x: x.str.strip() if x.dtype == "object" else x
            )
            return df_without_spaces
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def identify_feature_types(dataframe: pd.DataFrame):
        data_types = dataframe.dtypes

        categorical_features = []
        continuous_features = []
        discrete_features = []

        for column, dtype in dict(data_types).items():
            unique_values = dataframe[column].nunique()

            if dtype == "object" or unique_values < 10:
                categorical_features.append(column)
            elif dtype in [np.int64, np.float64]:
                if unique_values > 20:
                    continuous_features.append(column)
                else:
                    discrete_features.append(column)

        return categorical_features, continuous_features, discrete_features