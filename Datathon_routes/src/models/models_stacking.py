import pandas as pd
import numpy as np
import os
import joblib
import json
import time
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

def train_stacking_ensemble():
    print("Loading Duration Data for Stacking...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'train_duration.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'test_duration.csv'))
    
    target = 'block_duration_hours'
    drop_cols = ['timestamp', 'route_id', 'block_duration_hours']
    
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    y_train = train_df[target]
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    y_test = test_df[target]
    
    print(f"Training Stacking Ensemble on {len(X_train)} samples...")
    
    # Define Base Learners (using reasonable defaults/light tuning)
    estimators = [
        ('rf', RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)),
        ('xgb', XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42, n_jobs=-1)),
        ('lgbm', LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, random_state=42, n_jobs=-1, verbose=-1))
    ]
    
    # Meta Learner
    final_estimator = Ridge(alpha=1.0)
    
    # Stacking Regressor
    stacking_reg = StackingRegressor(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=5,
        n_jobs=-1,
        passthrough=False # Meta-learner only sees predictions of base learners
    )
    
    # Train
    t0 = time.time()
    stacking_reg.fit(X_train, y_train)
    print(f"Stacking Training took: {time.time() - t0:.2f}s")
    
    # Predict
    y_pred = stacking_reg.predict(X_test)
    
    # Evaluate
    metrics = evaluate_regression(y_test, y_pred, "Stacking Ensemble")
    
    # Save Model
    joblib.dump(stacking_reg, os.path.join(MODELS_DIR, 'duration_stacking_model.pkl'))
    
    # Load existing metrics to append
    metrics_path = os.path.join(REPORTS_DIR, 'duration_v2_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            existing_metrics = json.load(f)
    else:
        existing_metrics = {}
        
    existing_metrics['Stacking Ensemble'] = metrics
    
    with open(metrics_path, 'w') as f:
        json.dump(existing_metrics, f, indent=4)
        
    # Append predictions
    preds_path = os.path.join(REPORTS_DIR, 'duration_v2_predictions.csv')
    if os.path.exists(preds_path):
        preds_df = pd.read_csv(preds_path)
        preds_df['Stacking Ensemble'] = y_pred
        preds_df.to_csv(preds_path, index=False)
        
    print("Stacking metrics and predictions saved.")

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    if mask.sum() > 0:
        mape = (np.abs((y_true - y_pred) / y_true)[mask]).mean() * 100
    else:
        mape = np.nan
    
    print(f"[{model_name}] MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}, MAPE: {mape:.2f}%")
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

if __name__ == "__main__":
    train_stacking_ensemble()
