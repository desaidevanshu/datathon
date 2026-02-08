import pandas as pd
import os
import joblib

PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

def generate_predictions():
    print("Generating predictions from saved tuned model...")
    # Load Data
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'test_duration.csv'))
    target = 'block_duration_hours'
    drop_cols = ['timestamp', 'route_id', 'block_duration_hours']
    
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    y_test = test_df[target]
    
    # Load XGB Model
    model_path = os.path.join(MODELS_DIR, 'duration_tuned_xgb.pkl')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        y_pred = model.predict(X_test)
        
        # Save to CSV
        preds_df = pd.DataFrame({
            'Actual': y_test,
            'XGBoost (Tuned)': y_pred
        })
        preds_df.to_csv(os.path.join(REPORTS_DIR, 'duration_tuned_predictions.csv'), index=False)
        print("Predictions saved to duration_tuned_predictions.csv")
    else:
        print("Tuned model not found.")

if __name__ == "__main__":
    generate_predictions()
