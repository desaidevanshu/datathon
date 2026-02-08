import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
FIGURES_DIR = r'reports/figures'
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(os.path.join(FIGURES_DIR, 'Feature_Importance'), exist_ok=True)

def get_feature_names(data_path):
    # Load a sample of data to get column names
    df = pd.read_csv(data_path, nrows=5)
    
    # Logic from training scripts to exclude non-features
    # Common exclusions across scripts
    exclude_cols = ['timestamp', 'congestion_category', 'congestion_category_encoded', 
                    'origin', 'destination', 'route_id', 'congestion_index', 'block_duration_hours', 'actual_travel_time_min', 
                    'delay_minutes', 'is_congested', 'congestion_block', 'route_score', 'free_flow_time_min']
    
    features = [c for c in df.columns if c not in exclude_cols]
    return features

def plot_importance(model, feature_names, title, filename):
    try:
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            print(f"Model {title} does not have feature_importances_")
            return

        # Create DataFrame
        fi_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        fi_df = fi_df.sort_values(by='Importance', ascending=False).head(20) # Top 20
        
        plt.figure(figsize=(10, 8))
        sns.barplot(x='Importance', y='Feature', data=fi_df, palette='viridis')
        plt.title(f'Top 20 Feature Importance: {title}')
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'Feature_Importance', filename))
        plt.close()
        print(f"Saved: {filename}")
        
    except Exception as e:
        print(f"Error plotting {title}: {e}")

def generate_feature_importance_plots():
    print("Generating Feature Importance Plots...")
    
    # 1. Classification (Congestion Category)
    print("\n--- Classification ---")
    features_cls = get_feature_names(os.path.join(PROCESSED_DATA_DIR, 'General', 'train_encoded.csv'))
    
    # RF
    try:
        rf_cls = joblib.load(os.path.join(MODELS_DIR, 'rf_model.pkl'))
        plot_importance(rf_cls, features_cls, 'Classification (Random Forest)', 'Classification_RF_Feature_Importance.png')
    except: print("RF Classification model not found.")
    
    # XGB
    try:
        xgb_cls = joblib.load(os.path.join(MODELS_DIR, 'xgb_model.pkl'))
        plot_importance(xgb_cls, features_cls, 'Classification (XGBoost)', 'Classification_XGB_Feature_Importance.png')
    except: print("XGB Classification model not found.")

    # 2. Regression (Congestion Index)
    print("\n--- Regression (Congestion Index) ---")
    # Features are likely same as classification but let's re-verify or reuse
    features_reg = features_cls 
    
    # RF
    try:
        rf_reg = joblib.load(os.path.join(MODELS_DIR, 'rf_congestion_index.pkl'))
        plot_importance(rf_reg, features_reg, 'Regression: Congestion Index (RF)', 'Regression_CongestionIndex_RF_Importance.png')
    except: print("RF Regression model not found.")
    
    # XGB
    try:
        xgb_reg = joblib.load(os.path.join(MODELS_DIR, 'xgb_congestion_index.pkl'))
        plot_importance(xgb_reg, features_reg, 'Regression: Congestion Index (XGB)', 'Regression_CongestionIndex_XGB_Importance.png')
    except: print("XGB Regression model not found.")
    
    # 3. Regression (Block Duration - Baseline)
    # Different features for duration? 
    # Let's check data/processed/train_duration.csv feature names if possible or assume similar
    # The duration models use a different dataset.
    print("\n--- Regression (Block Duration) ---")
    try:
        df_dur = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'Duration', 'train_duration.csv'), nrows=5)
        # Duration features logic
        drop_cols_dur = ['timestamp', 'route_id', 'block_duration_hours', 'log_block_duration']
        features_dur = [c for c in df_dur.columns if c not in drop_cols_dur]
        
        # Tuned XGB (Best)
        try:
             # Try tuned first
            xgb_dur = joblib.load(os.path.join(MODELS_DIR, 'duration_tuned_xgb.pkl'))
            plot_importance(xgb_dur, features_dur, 'Duration: Block Hours (XGB Tuned)', 'Duration_XGB_Tuned_Importance.png')
        except:
            # Fallback to v2
            try:
                xgb_dur_v2 = joblib.load(os.path.join(MODELS_DIR, 'duration_v2_xgboost.pkl'))
                plot_importance(xgb_dur_v2, features_dur, 'Duration: Block Hours (XGB Baseline)', 'Duration_XGB_Baseline_Importance.png')
            except: print("Duration XGB model not found.")
            
    except FileNotFoundError:
        print("Duration training data not found to extract feature names.")

if __name__ == "__main__":
    generate_feature_importance_plots()
