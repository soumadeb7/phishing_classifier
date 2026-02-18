import sys
import json
import pandas as pd
import os
import shutil
from pathlib import Path
from dataclasses import dataclass

from src.constant import artifact_folder
from src.exception import CustomException
from src.logger import logging


# ===================== CONFIG ===================== #

@dataclass
class DataValidationConfig:
    data_validation_dir: str = os.path.join(artifact_folder, "data_validation")
    valid_data_dir: str = os.path.join(data_validation_dir, "validated")
    invalid_data_dir: str = os.path.join(data_validation_dir, "invalid")
    schema_config_file_path: str = os.path.join("config", "training_schema.json")


# ===================== VALIDATION ===================== #

class DataValidation:

    def __init__(self, raw_data_store_dir: Path):
        self.raw_data_store_dir = raw_data_store_dir
        self.config = DataValidationConfig()

    # -------------------------------------------------- #

    def load_schema(self) -> dict:
        try:
            with open(self.config.schema_config_file_path, "r") as f:
                schema = json.load(f)

            # ✅ NORMALISE ONLY COLUMN NAMES
            schema["ColName"] = {
                k.strip().lower(): v
                for k, v in schema["ColName"].items()
            }

            schema["label_column"] = "result"

            return schema

        except Exception as e:
            raise CustomException(e, sys)

    # -------------------------------------------------- #

    def load_schema(self):
        with open(self.config.schema_config_file_path, "r") as f:
            schema = json.load(f)

        # ✅ normalize ONLY ColName
        schema["ColName"] = {
            k.strip().lower(): v
            for k, v in schema["ColName"].items()
        }

        schema["label_column"] = "result"
        return schema

    # -------------------------------------------------- #

    def validate_dataset_schema(self, df: pd.DataFrame) -> bool:
        required_columns = [
            "url",
            "having_ip_address",
            "url_length",
            "shortining_service",
            "having_at_symbol",
            "double_slash_redirecting",
            "prefix_suffix",
            "having_sub_domain",
            "sslfinal_state",
            "domain_registeration_length",
            "favicon",
            "port",
            "https_token",
            "request_url",
            "url_of_anchor",
            "links_in_tags",
            "sfh",
            "submitting_to_email",
            "abnormal_url",
            "redirect",
            "on_mouseover",
            "rightclick",
            "popupwidnow",
            "iframe",
            "age_of_domain",
            "dnsrecord",
            "web_traffic",
            "label"
        ]

        missing = list(set(required_columns) - set(df.columns))

        if missing:
            raise Exception(f"Missing columns: {missing}")

        return True

    def validate_dataframe(self, df: pd.DataFrame, schema: dict):
        issues = []

        # ✅ force lowercase CSV columns
        df.columns = df.columns.str.strip().str.lower()

        # ✅ ONLY feature columns from schema
        feature_columns = set(schema["ColName"].keys())
        label_col = schema["label_column"]

        # 1️⃣ empty dataset
        if df.empty:
            issues.append("Dataset has zero rows")

        # 2️⃣ missing feature columns ONLY
        missing_cols = feature_columns - set(df.columns)
        if missing_cols:
            issues.append(f"Missing columns: {list(missing_cols)}")

        # 3️⃣ label column check
        if label_col not in df.columns:
            issues.append(f"Missing label column: {label_col}")

        # 4️⃣ relaxed numeric coercion
        for col in feature_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return len(issues) == 0, issues, df

    # -------------------------------------------------- #

    def get_raw_files(self):
        os.makedirs(self.raw_data_store_dir, exist_ok=True)
        return [
            os.path.join(self.raw_data_store_dir, f)
            for f in os.listdir(self.raw_data_store_dir)
            if f.lower().endswith(".csv")
        ]

    # -------------------------------------------------- #

    def move_file(self, src: str, dest_dir: str):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(src, os.path.join(dest_dir, os.path.basename(src)))

    # -------------------------------------------------- #

    def validate_raw_files(self):
        schema = self.load_schema()
        raw_files = self.get_raw_files()

        validated = 0
        invalid_reasons = {}

        for file in raw_files:
            df = pd.read_csv(file)

            is_valid, reasons, df = self.validate_dataframe(df, schema)

            if is_valid:
                # 🔹 SAVE WITH LOWERCASE HEADERS
                df.to_csv(file, index=False)
                self.move_file(file, self.config.valid_data_dir)
                validated += 1
            else:
                self.move_file(file, self.config.invalid_data_dir)
                invalid_reasons[os.path.basename(file)] = reasons

        return validated > 0, invalid_reasons

    # -------------------------------------------------- #

    def initiate_data_validation(self):
        try:
            logging.info("Starting data validation")

            status, invalid_reasons = self.validate_raw_files()

            logging.info(f"Validation status: {status}")
            logging.info(f"Invalid files report: {invalid_reasons}")

            print("Invalid files report:", invalid_reasons)

            if not status:
                raise Exception(
                    f"No valid data found. Validation report: {invalid_reasons}"
                )

            return self.config.valid_data_dir

        except Exception as e:
            raise CustomException(e, sys) from e