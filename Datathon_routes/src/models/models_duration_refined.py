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

def train_refined_duration_models():
    print("Loading Refined Duration Data...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'train_duration_refined.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'test_duration_refined.csv'))
    
    # Target: log_block_duration (we will inverse transform later for metrics)
    target = 'log_block_duration'
    original_target_col = 'block_duration_hours'
    
    # Feature Selection: Drop non-features and original target
    drop_cols = ['timestamp', 'route_id', 'block_duration_hours', 'log_block_duration']
    
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    y_train = train_df[target]
    
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    y_test_original = test_df[original_target_col] # Keep for evaluation
    
    print(f"Training Features: {X_train.columns.tolist()}")
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Models Config (Lightly tuned base + Stacking)
    models_config = {
        'Random Forest (Log)': RandomForestRegressor(n_estimators=150, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1),
        'XGBoost (Log)': XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1),
        'LightGBM (Log)': LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=31, random_state=42, n_jobs=-1, verbose=-1)
    }
    
    results = {}
    predictions_df = pd.DataFrame({'Actual': y_test_original})
    
    # 1. Train Individual Models
    estimators_for_stacking = []
    
    for name, model in models_config.items():
        print(f"\n--- Training {name} ---")
        t0 = time.time()
        model.fit(X_train, y_train)
        print(f"Training took: {time.time() - t0:.2f}s")
        
        # Predict (Log Scale)
        y_pred_log = model.predict(X_test)
        
        # Inverse Transform (ExpM1)
        y_pred_original = np.expm1(y_pred_log)
        
        # Evaluate
        metrics = evaluate_regression(y_test_original, y_pred_original, name)
        results[name] = metrics
        predictions_df[name] = y_pred_original
        
        # Save Model
        joblib.dump(model, os.path.join(MODELS_DIR, f'duration_refined_{name.lower().replace(" ", "_")}.pkl'))
        
        # Add to stacking list (name, model)
        # Note: StackingRegressor expects 'estimators' list, but it clones them.
        # We can pass the base definitions again or the fitted ones? Stacking normally refits.
        # Let's pass the definition.
        short_name = name.split()[0].lower()
        estimators_for_stacking.append((short_name, model))

    # 2. Train Stacking Ensemble
    print("\n--- Training Stacking Ensemble (Log) ---")
    stacking_reg = StackingRegressor(
        estimators=estimators_for_stacking,
        final_estimator=Ridge(alpha=1.0),
        cv=5,
        n_jobs=-1,
        passthrough=False
    )
    
    t0 = time.time()
    stacking_reg.fit(X_train, y_train)
    print(f"Stacking Training took: {time.time() - t0:.2f}s")
    
    y_pred_stack_log = stacking_reg.predict(X_test)
    y_pred_stack_original = np.expm1(y_pred_stack_log)
    
    metrics_stack = evaluate_regression(y_test_original, y_pred_stack_original, "Stacking Ensemble (Log)")
    results["Stacking Ensemble (Log)"] = metrics_stack
    predictions_df["Stacking Ensemble (Log)"] = y_pred_stack_original
    
    joblib.dump(stacking_reg, os.path.join(MODELS_DIR, 'duration_refined_stacking.pkl'))
    
    # Save Results
    with open(os.path.join(REPORTS_DIR, 'duration_refined_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    predictions_df.to_csv(os.path.join(REPORTS_DIR, 'duration_refined_predictions.csv'), index=False)
    print("Refined modeling completed.")

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
    train_refined_duration_models()
