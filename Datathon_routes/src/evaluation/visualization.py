import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import joblib

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Paths
REPORTS_DIR = r'reports'
FIGURES_DIR = r'reports/figures'
MODELS_DIR = r'models'

os.makedirs(FIGURES_DIR, exist_ok=True)

def plot_confusion_matrices():
    print("Generating classification plots...")
    try:
        preds = pd.read_csv(os.path.join(REPORTS_DIR, 'classification_predictions.csv'))
        from sklearn.metrics import confusion_matrix
        
        models = [c for c in preds.columns if c not in ['Actual', 'timestamp']]
        
        for model in models:
            cm = confusion_matrix(preds['Actual'], preds[model])
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'Confusion Matrix: {model}')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            
            # Renamed: Classification_ConfusionMatrix_{Model}.png
            filename = f'Classification_ConfusionMatrix_{model.replace(" ", "")}.png'
            plt.savefig(os.path.join(FIGURES_DIR, 'Classification_Congestion_Category', filename))
            plt.close()
            
    except FileNotFoundError:
        print("Classification predictions not found.")

def plot_regression_actual_vs_pred():
    print("Generating regression plots...")
    # Targets: congestion_index, block_duration_hours, actual_travel_time_min
    targets = ['congestion_index', 'actual_travel_time_min', 'block_duration_hours'] 
    
    for target in targets:
        try:
            preds = pd.read_csv(os.path.join(REPORTS_DIR, f'regression_predictions_{target}.csv'))
            subset = preds.head(100) # Plot first 100 for clarity
            
            # Map target to folder
            if 'congestion_index' in target:
                subfolder = 'Predict_Congestion_Index'
                clean_target = "CongestionIndex"
            elif 'travel_time' in target:
                subfolder = 'Predict_Actual_Travel_Time_Min'
                clean_target = "TravelTime"
            else:
                subfolder = 'Predict_Block_Duration_Hours'
                clean_target = "Duration_General" # Distinguish from specialized models
                
            os.makedirs(os.path.join(FIGURES_DIR, subfolder), exist_ok=True)
            
            # 1. Line Chart for each model
            for model in subset.columns:
                if model == 'Actual': continue
                
                plt.figure()
                plt.plot(subset['Actual'], label='Actual', color='black', linewidth=2, alpha=0.7)
                plt.plot(subset[model], label='Predicted', linestyle='--')
                plt.title(f'{target}: Actual vs {model}')
                plt.legend()
                
                clean_model = model.replace(" ", "")
                plt.savefig(os.path.join(FIGURES_DIR, subfolder, f'{clean_target}_{clean_model}.png'))
                plt.close()
                
        except FileNotFoundError:
            continue

def plot_feature_importance():
    print("Generating feature importance plots...")
    # Load RF and XGB for congestion_index as example
    try:
        rf = joblib.load(os.path.join(MODELS_DIR, 'rf_congestion_index.pkl'))
        # Need feature names... easier if saved with model or known. 
        # Skip complex loading for now, better to do in training script.
        pass
    except:
        pass

if __name__ == "__main__":
    plot_confusion_matrices()
    plot_regression_actual_vs_pred()
