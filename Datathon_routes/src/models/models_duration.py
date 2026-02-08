import pandas as pd
import numpy as np
import os
import joblib
import json
import time
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

# Create directories
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def train_duration_models():
    print("Loading Duration Datasets...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'train_duration.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'test_duration.csv'))
    
    target = 'block_duration_hours'
    
    # Drop non-feature columns
    drop_cols = ['timestamp', 'route_id', 'block_duration_hours'] 
    # Note: route_id_encoded is kept if present
    
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    y_train = train_df[target]
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    y_test = test_df[target]
    
    print(f"Training Features: {X_train.columns.tolist()}")
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Models to train with search spaces
    models_config = {
        'Random Forest': {
            'model': RandomForestRegressor(random_state=42, n_jobs=-1),
            'params': {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        },
        'XGBoost': {
            'model': XGBRegressor(random_state=42, n_jobs=-1),
            'params': {
                'n_estimators': [100, 300, 500],
                'learning_rate': [0.01, 0.05, 0.1],
                'max_depth': [3, 5, 7],
                'subsample': [0.7, 0.9, 1.0],
                'colsample_bytree': [0.7, 0.9, 1.0]
            }
        },
        'LightGBM': {
            'model': LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
            'params': {
                'n_estimators': [100, 300, 500],
                'learning_rate': [0.01, 0.05, 0.1],
                'num_leaves': [31, 50, 100],
                'max_depth': [-1, 10, 20]
            }
        }
    }
    
    results = {}
    best_r2 = -float('inf')
    best_model_name = None
    
    # Store predictions for comparison
    predictions_df = pd.DataFrame({'Actual': y_test})
    
    for name, config in models_config.items():
        print(f"\n--- Tuning {name} ---")
        base_model = config['model']
        param_dist = config['params']
        
        # Randomized Search
        search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=param_dist,
            n_iter=10, # Keep low for demo speed, increase for production
            scoring='neg_mean_squared_error',
            cv=3,
            verbose=1,
            random_state=42,
            n_jobs=-1
        )
        
        start_time = time.time()
        search.fit(X_train, y_train)
        elapsed_time = time.time() - start_time
        
        best_model = search.best_estimator_
        print(f"Best Params: {search.best_params_}")
        print(f"Tuning took: {elapsed_time:.2f}s")
        
        # Evaluate
        y_pred = best_model.predict(X_test)
        metrics = evaluate_regression(y_test, y_pred, name)
        
        results[name] = metrics
        predictions_df[name] = y_pred
        
        # Save model
        joblib.dump(best_model, os.path.join(MODELS_DIR, f'duration_v2_{name.lower().replace(" ", "_")}.pkl'))
        
        if metrics['R2'] > best_r2:
            best_r2 = metrics['R2']
            best_model_name = name

    # Save Metrics
    with open(os.path.join(REPORTS_DIR, 'duration_v2_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    # Save Predictions
    predictions_df.to_csv(os.path.join(REPORTS_DIR, 'duration_v2_predictions.csv'), index=False)
    
    print(f"\nBest Model: {best_model_name} with R2: {best_r2:.4f}")
    
    # Feature Importance for Best Model (if tree-based)
    if best_model_name:
        model_path = os.path.join(MODELS_DIR, f'duration_v2_{best_model_name.lower().replace(" ", "_")}.pkl')
        model = joblib.load(model_path)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = X_train.columns
            feature_imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
            feature_imp_df = feature_imp_df.sort_values(by='Importance', ascending=False)
            
            print("\nTop 10 Feature Importances:")
            print(feature_imp_df.head(10))
            feature_imp_df.to_csv(os.path.join(REPORTS_DIR, 'duration_v2_feature_importance.csv'), index=False)

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    if mask.sum() > 0:
        mape = (np.abs((y_true - y_pred) / y_true)[mask]).mean() * 100
    else:
        mape = np.nan
    
    print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

if __name__ == "__main__":
    train_duration_models()
