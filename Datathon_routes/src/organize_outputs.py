import pandas as pd
import os
import shutil

REPORTS_DIR = r'reports'
OUTPUT_BASE = os.path.join(REPORTS_DIR, 'Final_Outputs')
BEST_DIR = os.path.join(OUTPUT_BASE, 'Best_Predictions')
RAW_DIR = os.path.join(OUTPUT_BASE, 'All_Model_Predictions')

os.makedirs(BEST_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# Define tasks and best models
tasks = [
    {
        'file': 'classification_predictions.csv',
        'best_model': 'Logistic Regression',
        'output_name': 'Best_Classification_Predictions.csv'
    },
    {
        'file': 'regression_predictions_congestion_index.csv',
        'best_model': 'LightGBM',
        'output_name': 'Best_Congestion_Index_Predictions.csv'
    },
    {
        'file': 'regression_predictions_actual_travel_time_min.csv',
        'best_model': 'Random Forest',
        'output_name': 'Best_Travel_Time_Predictions.csv'
    },
    {
        'file': 'duration_v2_predictions.csv',
        'best_model': 'XGBoost',
        'output_name': 'Best_Block_Duration_Predictions.csv'
    }
]

print("Processing Best Models...")
for task in tasks:
    src_path = os.path.join(REPORTS_DIR, task['file'])
    if os.path.exists(src_path):
        try:
            df = pd.read_csv(src_path)
            if task['best_model'] in df.columns:
                # Extract Actual and Best Model
                best_df = df[['Actual', task['best_model']]].copy()
                best_df.columns = ['Actual', 'Predicted'] # Rename for clarity
                
                # Save to Best Folder
                best_df.to_csv(os.path.join(BEST_DIR, task['output_name']), index=False)
                print(f"Created: {task['output_name']}")
            else:
                print(f"Warning: Best model {task['best_model']} not found in {task['file']}")
                
            # Move original to Raw folder
            shutil.move(src_path, os.path.join(RAW_DIR, task['file']))
            
        except Exception as e:
            print(f"Error processing {task['file']}: {e}")

print("\nMoving other prediction files...")
# Move all other CSVs in reports root to Raw folder
for f in os.listdir(REPORTS_DIR):
    if f.endswith('.csv') and os.path.isfile(os.path.join(REPORTS_DIR, f)):
        shutil.move(os.path.join(REPORTS_DIR, f), os.path.join(RAW_DIR, f))
        print(f"Moved: {f}")

print("\nMigration Completed.")
