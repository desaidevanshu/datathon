import json
import os

REPORTS_DIR = r'reports'
METRICS_FILE = os.path.join(REPORTS_DIR, 'duration_tuned_metrics.json')

def save_manual_results():
    # Load existing (LSTM)
    try:
        with open(METRICS_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        
    # Add XGBoost (Tuned) from terminal output
    data['XGBoost (Aggressive Tuned)'] = {
        'MAE': 9.0572,
        'RMSE': 16.8570,
        'R2': 0.2205,
        'MAPE': 209.05
    }
    
    # Save
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Manually saved XGBoost results to {METRICS_FILE}")

if __name__ == "__main__":
    save_manual_results()
