import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json
import time

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

def train_regression_models():
    print("Loading data...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'train_encoded.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'test_encoded.csv'))
    
    targets = ['congestion_index', 'block_duration_hours', 'actual_travel_time_min']
    exclude_cols = ['timestamp', 'congestion_category', 'congestion_category_encoded', 
                    'origin', 'destination', 'route_id', 'is_congested', 'congestion_block', 'route_score', 'free_flow_time_min']
    
    base_features = [c for c in train_df.columns if c not in exclude_cols and c not in targets]
    print(f"Base Features: {base_features}")
    
    results = {}
    preds_dfs = {}
    
    for target in targets:
        print(f"\n--- Predicting {target} ---")
        X_train = train_df[base_features]
        y_train = train_df[target]
        X_test = test_df[base_features]
        y_test = test_df[target]
        
        target_results = {}
        preds_df = pd.DataFrame({'Actual': y_test})
        
        # 1. Random Forest (Reduced complexity for speed)
        print(f"Training RF for {target}...")
        t0 = time.time()
        # Reduced n_estimators to 10 and depth to 10 for quick execution
        rf = RandomForestRegressor(n_estimators=10, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)
        print(f"RF training took {time.time()-t0:.2f}s")
        target_results['Random Forest'] = evaluate_regression(y_test, y_pred_rf, 'Random Forest')
        preds_df['Random Forest'] = y_pred_rf
        
        joblib.dump(rf, os.path.join(MODELS_DIR, f'rf_{target}.pkl'))
        
        # 2. XGBoost
        try:
            from xgboost import XGBRegressor
            print(f"Training XGB for {target}...")
            # Reduced estimators
            xgb = XGBRegressor(n_estimators=20, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
            xgb.fit(X_train, y_train)
            y_pred_xgb = xgb.predict(X_test)
            target_results['XGBoost'] = evaluate_regression(y_test, y_pred_xgb, 'XGBoost')
            preds_df['XGBoost'] = y_pred_xgb
            joblib.dump(xgb, os.path.join(MODELS_DIR, f'xgb_{target}.pkl'))
        except ImportError:
            print("XGBoost not installed.")

        # 3. LightGBM
        try:
            import lightgbm as lgb
            print(f"Training LGBM for {target}...")
            lgbm = lgb.LGBMRegressor(n_estimators=50, random_state=42, n_jobs=-1)
            lgbm.fit(X_train, y_train)
            y_pred_lgbm = lgbm.predict(X_test)
            target_results['LightGBM'] = evaluate_regression(y_test, y_pred_lgbm, 'LightGBM')
            preds_df['LightGBM'] = y_pred_lgbm
            joblib.dump(lgbm, os.path.join(MODELS_DIR, f'lgbm_{target}.pkl'))
        except ImportError:
             print("LightGBM not installed.")
        except Exception as e:
            print(f"LGBM failed: {e}")
             
        results[target] = target_results
        
        # Save predictions immediately
        preds_df.to_csv(os.path.join(REPORTS_DIR, f'regression_predictions_{target}.csv'), index=False)

    # Save metrics
    with open(os.path.join(REPORTS_DIR, 'regression_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nRegression tasks completed.")

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    if mask.sum() > 0:
        mape = (np.abs((y_true - y_pred) / y_true)[mask]).mean() * 100
    else:
        mape = np.nan
    
    print(f"--- {model_name} ---")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

if __name__ == "__main__":
    train_regression_models()
