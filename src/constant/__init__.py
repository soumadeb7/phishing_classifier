from datetime import datetime
import os

artifact_folder = "artifacts"
AWS_S3_BUCKET_NAME = "samplesamplephishingclassifier"
MONGO_DATABASE_NAME = "phishing_db"

TARGET_COLUMN = "result"

MODEL_FILE_NAME = "model"
MODEL_FILE_EXTENSION = ".pkl"

artifact_folder_name = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
artifact_folder = os.path.join("artifacts", artifact_folder_name)
