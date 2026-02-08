import pandas as pd
import json
import os

REPORTS_DIR = r'reports'

def generate_comparison_table():
    print("Generating comparison tables...")
    
    # 1. Classification Metrics
    try:
        with open(os.path.join(REPORTS_DIR, 'classification_metrics.json'), 'r') as f:
            class_metrics = json.load(f)
            
        rows = []
        for model_name, metrics in class_metrics.items():
            row = {
                'Task': 'Congestion Category',
                'Model': model_name,
                'Accuracy': metrics['Accuracy'],
                'Precision': metrics['Precision'],
                'Recall': metrics['Recall'],
                'F1 Score': metrics['F1 Score']
            }
            rows.append(row)
            
        class_df = pd.DataFrame(rows)
        print("\nClassification Model Comparison:")
        print(class_df.to_string(index=False))
        class_df.to_csv(os.path.join(REPORTS_DIR, 'model_comparison_classification.csv'), index=False)
        
    except FileNotFoundError:
        print("Classification metrics not found.")

    # 2. Regression Metrics
    try:
        with open(os.path.join(REPORTS_DIR, 'regression_metrics.json'), 'r') as f:
            reg_metrics = json.load(f)
            
        rows = []
        for target, models in reg_metrics.items():
            for model_name, metrics in models.items():
                row = {
                    'Task': target,
                    'Model': model_name,
                    'MAE': metrics['MAE'],
                    'RMSE': metrics['RMSE'],
                    'R2': metrics['R2'],
                    'MAPE': metrics['MAPE']
                }
                rows.append(row)
                
        reg_df = pd.DataFrame(rows)
        print("\nRegression Model Comparison:")
        print(reg_df.to_string(index=False))
        reg_df.to_csv(os.path.join(REPORTS_DIR, 'model_comparison_regression.csv'), index=False)
        
    except FileNotFoundError:
        print("Regression metrics not found.")
        
    print("\nComparison tables generated in 'reports/'.")

if __name__ == "__main__":
    generate_comparison_table()
