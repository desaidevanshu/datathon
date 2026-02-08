import pandas as pd
import json
import os

REPORTS_DIR = r'reports'
OUTPUT_FILE = os.path.join(REPORTS_DIR, 'model_comparison.md')

def generate_comparison_md():
    print("Generating comprehensive model comparison markdown (with highlights)...")
    
    md_content = "# Urban Traffic Forecasting - Final Model Comparison\n\n"
    
    def highlight_best(df, metric, mode='max'):
        # Helper to find best row
        if df.empty: return df
        if mode == 'max':
            best_idx = pd.to_numeric(df[metric].astype(str).str.replace('%',''), errors='coerce').idxmax()
        else:
            best_idx = pd.to_numeric(df[metric].astype(str).str.replace('%',''), errors='coerce').idxmin()
            
        # Create a display copy
        df_display = df.copy()
        df_display.loc[best_idx, 'Model'] = f"**{df_display.loc[best_idx, 'Model']} (Best)** 🏆"
        return df_display

    def df_to_md(df):
        if df.empty: return ""
        cols = df.columns.tolist()
        md = "| " + " | ".join(cols) + " |\n"
        md += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for _, row in df.iterrows():
            md += "| " + " | ".join(str(val) for val in row) + " |\n"
        return md

    # 1. Classification
    md_content += "## 1. Classification (Congestion Category)\n"
    try:
        with open(os.path.join(REPORTS_DIR, 'classification_metrics.json'), 'r') as f:
            metrics = json.load(f)
        rows = [{'Model': m, 'Accuracy': f"{v['Accuracy']:.4f}", 'F1 Score': f"{v['F1 Score']:.4f}"} for m, v in metrics.items()]
        df_cls = pd.DataFrame(rows)
        if not df_cls.empty:
            df_cls = highlight_best(df_cls, 'Accuracy', 'max')
            md_content += df_to_md(df_cls) + "\n\n"
    except: pass

    # 2. Regression (Standard)
    md_content += "## 2. Regression Tasks (General)\n"
    try:
        with open(os.path.join(REPORTS_DIR, 'regression_metrics.json'), 'r') as f:
            reg_metrics = json.load(f)
        for target, models in reg_metrics.items():
            if target == 'block_duration_hours': continue 
            md_content += f"### Predict: `{target}`\n"
            rows = [{'Model': m, 'R2': f"{v['R2']:.4f}", 'MAE': f"{v['MAE']:.4f}"} for m, v in models.items()]
            df_reg = pd.DataFrame(rows)
            if not df_reg.empty:
                df_reg = highlight_best(df_reg, 'R2', 'max')
                md_content += df_to_md(df_reg) + "\n\n"
    except: pass

    # 3. Congestion Duration Comparison
    md_content += "## 3. Congestion Duration Modeling (Focus Area)\n"
    
    all_duration_rows = []
    
    # helper
    def extract_rows(filename, tag):
        try:
            with open(os.path.join(REPORTS_DIR, filename), 'r') as f:
                data = json.load(f)
            for m, v in data.items():
                all_duration_rows.append({
                    'Category': tag,
                    'Model': m,
                    'R2': v.get('R2', -1),
                    'MAE': v.get('MAE', 999)
                })
        except: pass

    extract_rows('duration_v2_metrics.json', 'Baseline (Block-Start)')
    extract_rows('duration_refined_metrics.json', 'Refined (Log)')
    extract_rows('duration_tuned_metrics.json', 'Advanced (Tuned/LSTM)')
    
    if all_duration_rows:
        df_dur = pd.DataFrame(all_duration_rows)
        # Sort by R2 descending
        df_dur = df_dur.sort_values(by='R2', ascending=False)
        
        # Highlight best
        best_idx = df_dur['R2'].idxmax()
        df_dur.loc[best_idx, 'Model'] = f"**{df_dur.loc[best_idx, 'Model']} (Best)** 🏆"
        
        # Format for display
        df_dur['R2'] = df_dur['R2'].apply(lambda x: f"{x:.4f}")
        df_dur['MAE'] = df_dur['MAE'].apply(lambda x: f"{x:.4f}")
        
        md_content += df_to_md(df_dur[['Category', 'Model', 'R2', 'MAE']]) + "\n\n"
    else:
        md_content += "_No duration metrics found._\n"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_comparison_md()
