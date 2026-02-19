from flask import Flask, render_template, jsonify, request, send_file
from dotenv import load_dotenv
import os, sys

from src.exception import CustomException
from src.logger import logging as lg
from src.pipeline.train_pipeline import TrainingPipeline
from src.pipeline.predict_pipeline import PredictionPipeline

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")


@app.route("/")
def home():
    return jsonify({"message": "home"}), 200


# ===================== TRAIN ===================== #

@app.route("/train", methods=["GET"])
def train_route():
    try:
        train_pipeline = TrainingPipeline()
        score = train_pipeline.run_pipeline()

        return jsonify({
            "status": "success",
            "message": "Model training completed successfully",
            "accuracy": score
        }), 200

    except Exception as e:
        lg.exception("Training failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===================== PREDICT ===================== #

@app.route("/predict", methods=["GET", "POST"])
def predict():
    try:
        if request.method == "POST":
            prediction_pipeline = PredictionPipeline(request)
            prediction_file_detail = prediction_pipeline.run_pipeline()

            lg.info("Prediction completed. Sending file to user.")

            return send_file(
                prediction_file_detail.prediction_file_path,
                download_name=prediction_file_detail.prediction_file_name,
                as_attachment=True
            )

        return render_template("prediction.html")

    except Exception as e:
        # ✅ NEVER raise inside Flask
        lg.exception("Prediction failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


#if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 10000))  # Render sets PORT automatically
    #app.run(host="0.0.0.0", port=port, debug=False)