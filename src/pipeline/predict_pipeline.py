import os
import sys
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from flask import request

from src.logger import logging
from src.exception import CustomException
from src.constant import *
from src.utils.main_utils import MainUtils


# =====================================
# PROJECT ROOT DIRECTORY
# =====================================

BASE_DIR = Path(__file__).resolve().parents[2]


# =====================================
# CONFIGURATION
# =====================================

@dataclass
class PredictionFileDetail:
    prediction_root_dir: str = str(BASE_DIR / "prediction_artifacts")
    prediction_file_name: str = "predicted_file.csv"

    @property
    def prediction_file_path(self):
        return os.path.join(
            self.prediction_root_dir,
            self.prediction_file_name
        )


# =====================================
# PREDICTION PIPELINE
# =====================================

class PredictionPipeline:
    def __init__(self, request: request):
        self.request = request
        self.utils = MainUtils()
        self.prediction_file_detail = PredictionFileDetail()

        # Ensure directory exists
        os.makedirs(
            self.prediction_file_detail.prediction_root_dir,
            exist_ok=True
        )

    # ---------------------------------
    # Save Uploaded CSV
    # ---------------------------------
    def save_input_files(self) -> str:
        try:
            if "file" not in self.request.files:
                raise ValueError("No file part in request.")

            input_csv_file = self.request.files["file"]

            if input_csv_file.filename == "":
                raise ValueError("No file selected.")

            filename = os.path.basename(input_csv_file.filename)

            input_file_path = os.path.join(
                self.prediction_file_detail.prediction_root_dir,
                filename
            )

            input_csv_file.save(input_file_path)

            return input_file_path

        except Exception as e:
            raise CustomException(e, sys)

    # ---------------------------------
    # Load Model and Predict
    # ---------------------------------
    def predict(self, features: pd.DataFrame):
        try:
            model_local_path = str(BASE_DIR / "model.pkl")

            model_path = self.utils.download_model(
                bucket_name=AWS_S3_BUCKET_NAME,
                bucket_file_name="model.pkl",
                dest_file_name=model_local_path,
            )

            model = self.utils.load_object(file_path=model_path)

            predictions = model.predict(features)

            return predictions

        except Exception as e:
            raise CustomException(e, sys)

    # ---------------------------------
    # Generate Output CSV
    # ---------------------------------
    def get_predicted_dataframe(self, input_dataframe_path: str):
        try:
            input_dataframe = pd.read_csv(input_dataframe_path)

            predictions = self.predict(input_dataframe)

            input_dataframe[TARGET_COLUMN] = predictions

            target_column_mapping = {
                0: "phishing",
                1: "safe"
            }

            input_dataframe["Mapped Result"] = (
                input_dataframe[TARGET_COLUMN]
                .map(target_column_mapping)
            )

            output_path = self.prediction_file_detail.prediction_file_path

            input_dataframe.to_csv(output_path, index=False)

            logging.info("Predictions completed successfully.")

            return self.prediction_file_detail

        except Exception as e:
            raise CustomException(e, sys)

    # ---------------------------------
    # Run Pipeline
    # ---------------------------------
    def run_pipeline(self):
        try:
            input_csv_path = self.save_input_files()
            prediction_file_detail = self.get_predicted_dataframe(input_csv_path)

            return prediction_file_detail

        except Exception as e:
            raise CustomException(e, sys)