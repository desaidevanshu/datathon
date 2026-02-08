import pandas as pd
import numpy as np
import os
import joblib
import json
import time
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

def train_tuned_duration_models():
    print("Loading Duration Data (Block-Start)...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'train_duration.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'test_duration.csv'))
    
    target = 'block_duration_hours'
    drop_cols = ['timestamp', 'route_id', 'block_duration_hours']
    
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    y_train = train_df[target]
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    y_test = test_df[target]
    
    print(f"Training Features: {X_train.columns.tolist()}")
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # 1. XGBoost Aggressive Tuning
    print("\n--- Tuning XGBoost (Aggressive) ---")
    xgb_params = {
        'n_estimators': [300, 500, 800, 1000],
        'learning_rate': [0.005, 0.01, 0.03, 0.05],
        'max_depth': [3, 5, 7, 9],
        'min_child_weight': [1, 3, 5],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'gamma': [0, 0.1, 0.3],
        'reg_alpha': [0, 0.1, 1, 10],
        'reg_lambda': [0.1, 1, 10]
    }
    
    xgb_search = RandomizedSearchCV(
        estimator=XGBRegressor(random_state=42, n_jobs=-1),
        param_distributions=xgb_params,
        n_iter=20, # Higher iterations for better coverage
        scoring='r2',
        cv=4,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    
    t0 = time.time()
    xgb_search.fit(X_train, y_train)
    print(f"XGB Tuning took: {time.time() - t0:.2f}s")
    print(f"Best XGB Params: {xgb_search.best_params_}")
    
    best_xgb = xgb_search.best_estimator_
    y_pred_xgb = best_xgb.predict(X_test)
    metrics_xgb = evaluate_regression(y_test, y_pred_xgb, "XGBoost (Tuned)")
    
    # 2. LightGBM Aggressive Tuning
    print("\n--- Tuning LightGBM (Aggressive) ---")
    lgbm_params = {
        'n_estimators': [300, 500, 800, 1000],
        'learning_rate': [0.005, 0.01, 0.03, 0.05],
        'num_leaves': [20, 31, 50, 80],
        'max_depth': [-1, 7, 10, 15],
        'min_child_samples': [10, 20, 30, 50],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'reg_alpha': [0, 0.1, 1, 5],
        'reg_lambda': [0.1, 1, 5]
    }
    
    lgbm_search = RandomizedSearchCV(
        estimator=LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
        param_distributions=lgbm_params,
        n_iter=20,
        scoring='r2',
        cv=4,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    
    t0 = time.time()
    lgbm_search.fit(X_train, y_train)
    print(f"LGBM Tuning took: {time.time() - t0:.2f}s")
    print(f"Best LGBM Params: {lgbm_search.best_params_}")
    
    best_lgbm = lgbm_search.best_estimator_
    y_pred_lgbm = best_lgbm.predict(X_test)
    metrics_lgbm = evaluate_regression(y_test, y_pred_lgbm, "LightGBM (Tuned)")
    
    # Save Results
    results = {
        "XGBoost (Tuned)": metrics_xgb,
        "LightGBM (Tuned)": metrics_lgbm
    }
    
    joblib.dump(best_xgb, os.path.join(MODELS_DIR, 'duration_tuned_xgb.pkl'))
    joblib.dump(best_lgbm, os.path.join(MODELS_DIR, 'duration_tuned_lgbm.pkl'))
    
    with open(os.path.join(REPORTS_DIR, 'duration_tuned_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    predictions_df = pd.DataFrame({
        'Actual': y_test,
        'XGBoost (Tuned)': y_pred_xgb,
        'LightGBM (Tuned)': y_pred_lgbm
    })
    predictions_df.to_csv(os.path.join(REPORTS_DIR, 'duration_tuned_predictions.csv'), index=False)
    
    print("Tuned modeling completed.")

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
    train_tuned_duration_models()
