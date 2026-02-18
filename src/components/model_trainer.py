import sys
import os
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

from dataclasses import dataclass

from src.constant import *
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils
from sklearn.metrics import classification_report, confusion_matrix

#print(confusion_matrix(y_test, y_pred))
#print(classification_report(y_test, y_pred))

# ===============================
# CONFIG CLASS
# ===============================

@dataclass
class ModelTrainerConfig:
    model_trainer_dir = os.path.join(artifact_folder, "model_trainer")
    trained_model_path = os.path.join(
        model_trainer_dir, "trained_model", "model.pkl"
    )
    expected_accuracy = 0.5
    model_config_file_path = os.path.join("config", "model.yaml")


# ===============================
# CUSTOM WRAPPER MODEL
# ===============================

class VisibilityModel:
    def __init__(self, preprocessing_object: ColumnTransformer, trained_model_object):
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, X: pd.DataFrame):
        try:
            transformed_feature = self.preprocessing_object.transform(X)
            return self.trained_model_object.predict(transformed_feature)
        except Exception as e:
            raise CustomException(e, sys)

    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__}()"


# ===============================
# MODEL TRAINER
# ===============================

class ModelTrainer:

    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.utils = MainUtils()

        self.models = {
            "GaussianNB": GaussianNB(),
            "XGBClassifier": XGBClassifier(objective="binary:logistic"),
            "LogisticRegression": LogisticRegression()
        }

    # --------------------------------
    # Evaluate Multiple Models
    # --------------------------------
    def evaluate_models(
        self,
        X_train,
        X_test,
        y_train,
        y_test,
        models
    ):
        try:
            report = {}

            for model_name, model in models.items():
                model.fit(X_train, y_train)
                y_test_pred = model.predict(X_test)
                test_score = accuracy_score(y_test, y_test_pred)
                report[model_name] = test_score

            return report

        except Exception as e:
            raise CustomException(e, sys)

    # --------------------------------
    # Hyperparameter Tuning
    # --------------------------------
    def finetune_best_model(
        self,
        best_model_object,
        best_model_name,
        X_train,
        y_train,
    ):
        try:
            model_config = self.utils.read_yaml_file(
                self.model_trainer_config.model_config_file_path
            )

            param_grid = model_config["model_selection"]["model"][
                best_model_name
            ]["search_param_grid"]

            grid_search = GridSearchCV(
                best_model_object,
                param_grid=param_grid,
                cv=5,
                n_jobs=-1,
                verbose=1
            )

            grid_search.fit(X_train, y_train)

            best_params = grid_search.best_params_

            finetuned_model = best_model_object.set_params(**best_params)

            return finetuned_model

        except Exception as e:
            raise CustomException(e, sys)

    # --------------------------------
    # Main Trainer Method
    # --------------------------------
    def initiate_model_trainer(
        self,
        x_train,
        y_train,
        x_test,
        y_test,
        preprocessor_path
    ):
        try:
            logging.info("Loading preprocessor object")
            preprocessor = self.utils.load_object(preprocessor_path)

            logging.info("Evaluating models")

            model_report = self.evaluate_models(
                X_train=x_train,
                X_test=x_test,
                y_train=y_train,
                y_test=y_test,
                models=self.models
            )

            best_model_name = max(model_report, key=model_report.get)
            best_model = self.models[best_model_name]

            logging.info(f"Best model before tuning: {best_model_name}")

            # Hyperparameter tuning
            best_model = self.finetune_best_model(
                best_model_object=best_model,
                best_model_name=best_model_name,
                X_train=x_train,
                y_train=y_train
            )

            # Final training
            best_model.fit(x_train, y_train)
            y_pred = best_model.predict(x_test)

            best_model_score = accuracy_score(y_test, y_pred)

            print(f"Best model: {best_model_name}")
            print(f"Best accuracy: {best_model_score}")

            if best_model_score < self.model_trainer_config.expected_accuracy:
                raise Exception(
                    f"No model found with accuracy greater than {self.model_trainer_config.expected_accuracy}"
                )

            # Wrap model with preprocessor
            final_model = VisibilityModel(
                preprocessing_object=preprocessor,
                trained_model_object=best_model
            )

            # Save locally
            os.makedirs(
                os.path.dirname(self.model_trainer_config.trained_model_path),
                exist_ok=True
            )

            self.utils.save_object(
                file_path=self.model_trainer_config.trained_model_path,
                obj=final_model
            )

            logging.info("Model saved locally")

            # Upload (currently disabled in MainUtils)
            self.utils.upload_file(
                from_filename=self.model_trainer_config.trained_model_path,
                to_filename="model.pkl",
                bucket_name=AWS_S3_BUCKET_NAME
            )

            logging.info("Model upload step completed")

            return best_model_score

        except Exception as e:
            raise CustomException(e, sys)