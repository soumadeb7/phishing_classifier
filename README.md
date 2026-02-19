# 🚨 Phishing URL Classifier

A production-ready Machine Learning web application that detects whether a URL is **phishing** or **legitimate** using a trained classification model.

🌐 **Live Demo:**  
https://phishing-classifier-2-61uy.onrender.com/

---

## 📌 Project Overview

Phishing attacks are one of the most common cybersecurity threats.  
This project builds an end-to-end ML pipeline to:

- Data ingestion  
- Data transformation  
- Model training  
- Model evaluation  
- REST API deployment using Flask  
- Production deployment using Docker + Gunicorn  

---

## 🏗️ Tech Stack

### Backend
- Flask
- Gunicorn
- Python 3.10

### Machine Learning
- Scikit-Learn
- XGBoost
- Imbalanced-Learn
- Pandas
- NumPy

### Database
- MongoDB (PyMongo)

### Deployment
- Docker
- Render

---

## 📂 Project Structure

```
phishing-classifier/
│
├── app.py
├── requirements.txt
├── Dockerfile
│
├── src/
│   ├── components/
│   ├── pipeline/
│   ├── exception.py
│   └── logger.py
│
├── templates/
│   └── prediction.html
│
└── artifacts/
```

---

## 🚀 API Endpoints

### 🔹 Home

```
GET /
```

Response:

```json
{
  "message": "home"
}
```

---

### 🔹 Health Check

```
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

### 🔹 Train Model

```
GET /train
```

Triggers full ML training pipeline and returns model accuracy.

---

### 🔹 Predict

```
POST /predict
```

Accepts input data and returns prediction results file.

---

## 🐳 Running Locally with Docker

### 1️⃣ Build the Docker Image

```bash
docker build -t phishing-app .
```

### 2️⃣ Run the Container

```bash
docker run -p 10000:10000 phishing-app
```

### 3️⃣ Access Application

Open in browser:

```
http://localhost:10000/health
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```
MONGO_URI=your_mongodb_connection_string
```

On Render, configure environment variables inside the dashboard.

---

## 🧠 Machine Learning Pipeline

1. Data Ingestion  
2. Data Validation  
3. Data Transformation  
4. Class Imbalance Handling (RandomOverSampler)  
5. Model Training (XGBoost / Scikit-Learn)  
6. Model Evaluation  
7. Model Artifact Saving  

---

## 🔐 Production Features

- Gunicorn WSGI server
- Docker containerization
- Health check endpoint
- Environment variable management
- Structured logging
- Custom exception handling

---

## 📦 Deployment

The application is deployed using:

- Docker container
- Gunicorn WSGI server
- Render Cloud Platform

🔗 Live URL:  
https://phishing-classifier-2-61uy.onrender.com/

---

## 👨‍💻 Author

Soumadeb

---

## ⭐ Future Improvements

- Add authentication
- Add asynchronous training job queue
- Add model versioning
- Add request rate limiting
- CI/CD automation
