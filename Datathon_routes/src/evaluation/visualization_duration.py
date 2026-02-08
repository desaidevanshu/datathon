import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

sns.set_style("whitegrid")
REPORTS_DIR = r'reports'
FIGURES_DIR = r'reports/figures'

def generate_duration_plots():
    print("Generating duration plots (Renamed)...")
    subfolder = 'Predict_Block_Duration_Hours'
    save_dir = os.path.join(FIGURES_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Baseline (Block-Start)
    try:
        preds = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_v2_predictions.csv'))
        subset = preds.head(100)
        for col in subset.columns:
            if col == 'Actual': continue
            plt.figure(figsize=(10, 5))
            plt.plot(subset['Actual'], label='Actual', color='black', linewidth=2)
            plt.plot(subset[col], label='Predicted', linestyle='--')
            plt.title(f'Duration (Baseline): Actual vs {col}')
            plt.legend()
            
            # Rename: Duration_Baseline_{Model}.png
            clean_model = col.replace(" ", "").replace("stacking", "Stacking")
            plt.savefig(os.path.join(save_dir, f'Duration_Baseline_{clean_model}.png'))
            plt.close()
    except FileNotFoundError: pass

    # 2. Refined (Log)
    try:
        preds = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_refined_predictions.csv'))
        subset = preds.head(100)
        for col in subset.columns:
            if col == 'Actual': continue
            plt.figure(figsize=(10, 5))
            plt.plot(subset['Actual'], label='Actual', color='black', linewidth=2)
            plt.plot(subset[col], label='Predicted', linestyle='--', color='green')
            plt.title(f'Duration (Log): Actual vs {col}')
            plt.legend()
            
            clean_model = col.replace(" ", "").replace("(Log)", "")
            plt.savefig(os.path.join(save_dir, f'Duration_Log_{clean_model}.png'))
            plt.close()
    except: pass

    # 3. Tuned
    try:
        preds = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_tuned_predictions.csv'))
        subset = preds.head(100)
        for col in subset.columns:
            if col == 'Actual': continue
            plt.figure(figsize=(10, 5))
            plt.plot(subset['Actual'], label='Actual', color='black', linewidth=2)
            plt.plot(subset[col], label='Predicted', linestyle='--', color='purple')
            plt.title(f'Duration (Tuned): Actual vs {col}')
            plt.legend()
            
            clean_model = col.replace(" ", "").replace("(Tuned)", "")
            plt.savefig(os.path.join(save_dir, f'Duration_Tuned_{clean_model}.png'))
            plt.close()
    except: pass

    # 4. LSTM
    try:
        preds = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_lstm_predictions.csv'))
        subset = preds.head(100)
        col = 'LSTM Sequence (6h)'
        if col in subset.columns:
            plt.figure(figsize=(10, 5))
            plt.plot(subset['Actual'], label='Actual', color='black', linewidth=2)
            plt.plot(subset[col], label='Predicted', linestyle='--', color='red')
            plt.title(f'Duration (LSTM): Actual vs {col}')
            plt.legend()
            
            plt.savefig(os.path.join(save_dir, f'Duration_Sequence_LSTM.png'))
            plt.close()
    except: pass
    
    print("Duration plots generated.")

if __name__ == "__main__":
    generate_duration_plots()
