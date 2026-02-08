import pandas as pd
import numpy as np
import os
import joblib
import xgboost as xgb
import lightgbm as lgb
import json

# ==========================================
# Configuration
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # src/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # c:/Datathon_routes/

# Inputs
DATA_GENERAL = os.path.join(PROJECT_ROOT, 'data', 'processed', 'General', 'test_encoded.csv')
DATA_DURATION = os.path.join(PROJECT_ROOT, 'data', 'processed', 'Duration', 'test_duration.csv')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models', 'best_models')

# Outputs
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'reports', 'Final_Outputs', 'Best_Predictions')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Model Filenames
MODEL_FILES = {
    'classification': 'lr_model.pkl',
    'congestion': 'lgbm_congestion_index.pkl',
    'travel_time': 'rf_actual_travel_time_min.pkl',
    'duration': 'duration_v2_xgboost.pkl'
}

# Feature Columns to Exclude (Must match training!)
EXCLUDE_COLS_GENERAL = [
    'timestamp', 'congestion_category', 'congestion_category_encoded', 
    'origin', 'destination', 'route_id', 'congestion_index', 'block_duration_hours', 
    'actual_travel_time_min', 'delay_minutes', 'is_congested', 'congestion_block', 
    'route_score', 'free_flow_time_min'
]

EXCLUDE_COLS_DURATION = [
    'timestamp', 'route_id', 'block_duration_hours'
]

def load_data(path):
    print(f"Loading data from {path}...")
    return pd.read_csv(path)

def get_features(df, exclude_cols):
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    return df[feature_cols]

def run_inference():
    print("Starting Inference Pipeline...")
    
    # ---------------------------
    # 1. Load Data
    # ---------------------------
    df_general = load_data(DATA_GENERAL)
    df_duration = load_data(DATA_DURATION)
    
    # ---------------------------
    # 2. General Tasks
    # ---------------------------
    X_gen = get_features(df_general, EXCLUDE_COLS_GENERAL)
    print(f"General Features: {len(X_gen.columns)}")
    
    # A. Classification (Congestion Category)
    print("Running Classification (Logistic Regression)...")
    clf_model = joblib.load(os.path.join(MODELS_DIR, MODEL_FILES['classification']))
    pred_class = clf_model.predict(X_gen)
    
    # Save Classification
    res_clf = pd.DataFrame({
        'Actual_Encoded': df_general['congestion_category_encoded'],
        'Predicted_Encoded': pred_class
    })
    # Map back if needed (0=Low, 1=Medium, 2=High based on OrdinalEncoder logic)
    mapping = {0: 'Low', 1: 'Medium', 2: 'High'}
    res_clf['Predicted_Label'] = res_clf['Predicted_Encoded'].map(mapping)
    res_clf.to_csv(os.path.join(OUTPUT_DIR, 'Best_Classification_Predictions.csv'), index=False)
    
    # B. Congestion Index
    print("Running Congestion Index (LightGBM)...")
    try:
        reg_cong_model = joblib.load(os.path.join(MODELS_DIR, MODEL_FILES['congestion']))
        pred_cong = reg_cong_model.predict(X_gen)
        
        res_cong = pd.DataFrame({
            'Actual': df_general['congestion_index'],
            'Predicted': pred_cong
        })
        res_cong.to_csv(os.path.join(OUTPUT_DIR, 'Best_Congestion_Index_Predictions.csv'), index=False)
    except Exception as e:
        print(f"Error predicting Congestion Index: {e}")

    # C. Travel Time
    print("Running Travel Time (Random Forest)...")
    try:
        reg_time_model = joblib.load(os.path.join(MODELS_DIR, MODEL_FILES['travel_time']))
        pred_time = reg_time_model.predict(X_gen)
        
        res_time = pd.DataFrame({
            'Actual': df_general['actual_travel_time_min'],
            'Predicted': pred_time
        })
        res_time.to_csv(os.path.join(OUTPUT_DIR, 'Best_Travel_Time_Predictions.csv'), index=False)
    except Exception as e:
        print(f"Error predicting Travel Time: {e}")

    # ---------------------------
    # 3. Duration Task
    # ---------------------------
    print("Running Block Duration (XGBoost)...")
    X_dur = get_features(df_duration, EXCLUDE_COLS_DURATION)
    print(f"Duration Features: {len(X_dur.columns)}")
    
    try:
        dur_model = joblib.load(os.path.join(MODELS_DIR, MODEL_FILES['duration']))
        pred_dur = dur_model.predict(X_dur)
        
        res_dur = pd.DataFrame({
            'Actual': df_duration['block_duration_hours'],
            'Predicted': pred_dur
        })
        res_dur.to_csv(os.path.join(OUTPUT_DIR, 'Best_Block_Duration_Predictions.csv'), index=False)
    except Exception as e:
        print(f"Error predicting Duration: {e}")

    print(f"\n✅ All predictions saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    run_inference()
