# 🚀 Model Deployment Guide (FastAPI)

This folder contains the **Inference Pipeline** (`inference_pipeline.py`) designed to be the core engine of your FastAPI application.

## 📂 Files
*   `inference_pipeline.py`: A self-contained script that loads the **4 Best Models** and generates predictions from new data.

## 🛠️ How to Integrate with FastAPI

You can copy the logic from `inference_pipeline.py` directly into your FastAPI app. Here is a blueprint:

### 1. Load Models at Startup
Load the models once when the app starts to save time.
```python
# main.py
from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

# Global variables to store models
models = {}

@app.on_event("startup")
def load_models():
    models['classification'] = joblib.load("models/best_models/lr_model.pkl")
    models['congestion'] = joblib.load("models/best_models/lgbm_congestion_index.pkl")
    models['travel_time'] = joblib.load("models/best_models/rf_actual_travel_time_min.pkl")
    models['duration'] = joblib.load("models/best_models/duration_v2_xgboost.pkl")
    print("✅ Models Loaded")
```

### 2. Define Prediction Endpoint
Create an endpoint that accepts JSON data, converts it to a DataFrame, and feeds it to the models.
```python
@app.post("/predict")
def predict(data: dict):
    # 1. Convert Input to DataFrame
    df = pd.DataFrame([data])
    
    # 2. Select Features (Ensure columns match training!)
    # See inference_pipeline.py for the exact exclusion lists
    
    # 3. Predict
    cong_cat = models['classification'].predict(df)
    cong_idx = models['congestion'].predict(df)
    travel_time = models['travel_time'].predict(df)
    
    return {
        "congestion_category": int(cong_cat[0]),
        "congestion_index": float(cong_idx[0]),
        "travel_time_min": float(travel_time[0])
    }
```

## ⚠️ Important: Feature Consistency
The most common error in deployment is **Feature Mismatch**. 
*   Your API input **MUST** provide exactly the same features (columns) that the models were trained on.
*   Refer to `inference_pipeline.py` lines `EXCLUDE_COLS_GENERAL` to see which columns to *drop* or *keep*.
*   If your raw input is just `timestamp` and `route_id`, you must run the **Feature Engineering** steps (lags, rolling stats) *inside* your API before passing data to the model.
