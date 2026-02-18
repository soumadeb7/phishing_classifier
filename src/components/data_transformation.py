import sys
import os
import pandas as pd
import numpy as np
from dataclasses import dataclass

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import RandomOverSampler

from src.constant import artifact_folder, TARGET_COLUMN
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils


# ===================== CONFIG ===================== #

@dataclass
class DataTransformationConfig:
    data_transformation_dir = os.path.join(artifact_folder, "data_transformation")
    transformed_train_file_path = os.path.join(data_transformation_dir, "train.npy")
    transformed_test_file_path = os.path.join(data_transformation_dir, "test.npy")
    transformed_object_file_path = os.path.join(
        data_transformation_dir, "preprocessing.pkl"
    )


# ===================== TRANSFORMATION ===================== #

class DataTransformation:

    def __init__(self, valid_data_dir: str):
        self.valid_data_dir = valid_data_dir
        self.config = DataTransformationConfig()
        self.utils = MainUtils()

    # -------------------------------------------------- #

    @staticmethod
    def get_merged_batch_data(valid_data_dir: str) -> pd.DataFrame:
        try:
            csv_files = os.listdir(valid_data_dir)
            dataframes = []

            for file in csv_files:
                df = pd.read_csv(os.path.join(valid_data_dir, file))
                dataframes.append(df)

            return pd.concat(dataframes, ignore_index=True)

        except Exception as e:
            raise CustomException(e, sys)

    # -------------------------------------------------- #

    def initiate_data_transformation(self):
        try:
            logging.info("Starting data transformation")

            df = self.get_merged_batch_data(self.valid_data_dir)

            df = self.utils.remove_unwanted_spaces(df)

            # ✅ NumPy 2.0 compatible
            df.replace("?", np.nan, inplace=True)

            X = df.drop(columns=[TARGET_COLUMN])
            y = np.where(df[TARGET_COLUMN] == -1, 0, 1)

            sampler = RandomOverSampler()
            X_resampled, y_resampled = sampler.fit_resample(X, y)

            X_train, X_test, y_train, y_test = train_test_split(
                X_resampled, y_resampled, test_size=0.2, random_state=42
            )

            imputer = SimpleImputer(strategy="most_frequent")

            X_train_transformed = imputer.fit_transform(X_train)
            X_test_transformed = imputer.transform(X_test)

            os.makedirs(self.config.data_transformation_dir, exist_ok=True)

            self.utils.save_object(
                self.config.transformed_object_file_path, imputer
            )

            return (
                X_train_transformed,
                y_train,
                X_test_transformed,
                y_test,
                self.config.transformed_object_file_path,
            )

        except Exception as e:
            raise CustomException(e, sys) from e