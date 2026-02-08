import pandas as pd
import numpy as np
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import json
import time

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

def train_classification_models():
    print("Loading data...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'train_encoded.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'test_encoded.csv'))
    
    target_col = 'congestion_category_encoded'
    
    # Re-encode target to ensure 0-indexed contiguous integers
    # This handles the case where 'Low' (0) is missing and we only have 1 and 2.
    # LabelEncoder will map {1, 2} to {0, 1}
    print("Re-encoding target variable...")
    le = LabelEncoder()
    y_train = le.fit_transform(train_df[target_col])
    y_test = le.transform(test_df[target_col]) # Use transform to maintain consistency
    
    print(f"Classes mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    print(f"Train classes: {np.unique(y_train)}")
    print(f"Test classes: {np.unique(y_test)}")
    
    exclude_cols = ['timestamp', 'congestion_category', 'congestion_category_encoded', 
                    'origin', 'destination', 'route_id', 'congestion_index', 'block_duration_hours', 'actual_travel_time_min', 
                    'delay_minutes', 'is_congested', 'congestion_block', 'route_score', 'free_flow_time_min']
    
    feature_cols = [c for c in train_df.columns if c not in exclude_cols]
    
    print(f"Features: {feature_cols}")
    
    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]
    
    # Now y_train/y_test are 0,1,...
    unique_classes = np.unique(np.concatenate([y_train, y_test]))
    
    results = {}
    preds_df = pd.DataFrame({'Actual': y_test})
    
    # 1. Logistic Regression
    print("\nTraining Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    results['Logistic Regression'] = evaluate_model(y_test, y_pred_lr, 'Logistic Regression', unique_classes)
    preds_df['Logistic Regression'] = y_pred_lr
    joblib.dump(lr, os.path.join(MODELS_DIR, 'lr_model.pkl'))
    
    # 2. Random Forest
    print("\nTraining Random Forest...")
    rf = RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    results['Random Forest'] = evaluate_model(y_test, y_pred_rf, 'Random Forest', unique_classes)
    preds_df['Random Forest'] = y_pred_rf
    joblib.dump(rf, os.path.join(MODELS_DIR, 'rf_model.pkl'))
    
    # 3. XGBoost
    try:
        from xgboost import XGBClassifier
        print("\nTraining XGBoost...")
        # num_class required if multiclass, but let's see if auto works for binary 0,1
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', n_estimators=50, max_depth=6, random_state=42, n_jobs=-1)
        xgb.fit(X_train, y_train)
        y_pred_xgb = xgb.predict(X_test)
        results['XGBoost'] = evaluate_model(y_test, y_pred_xgb, 'XGBoost', unique_classes)
        preds_df['XGBoost'] = y_pred_xgb
        joblib.dump(xgb, os.path.join(MODELS_DIR, 'xgb_model.pkl'))
    except ImportError:
        print("XGBoost not installed.")

    with open(os.path.join(REPORTS_DIR, 'classification_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    preds_df.to_csv(os.path.join(REPORTS_DIR, 'classification_predictions.csv'), index=False)
    print("\nClassification tasks completed.")

def evaluate_model(y_true, y_pred, model_name, labels):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0, labels=labels)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0, labels=labels)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0, labels=labels)
    
    try:
        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    except Exception as e:
        print(f"Error computing confusion matrix: {e}")
        cm = []
    
    print(f"--- {model_name} ---")
    print(f"Accuracy: {acc:.4f}")
    
    return {
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1 Score': f1,
        'Confusion Matrix': cm
    }

if __name__ == "__main__":
    train_classification_models()
