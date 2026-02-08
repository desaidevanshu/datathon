import pandas as pd
import json
import os

REPORTS_DIR = r'reports'
OUTPUT_FILE = os.path.join(REPORTS_DIR, 'model_comparison_duration.md')

def generate_duration_report():
    print("Generating duration comparison report...")
    
    md_content = "# Advanced Congestion Duration Modeling Results\n\n"
    md_content += "This report compares the performance of models predicting congestion duration at the **start of a block**.\n\n"
    
    # 1. Metrics Table
    md_content += "## Model Performance (Block-Start Approach)\n"
    try:
        with open(os.path.join(REPORTS_DIR, 'duration_v2_metrics.json'), 'r') as f:
            metrics = json.load(f)
            
        rows = []
        for model, res in metrics.items():
            row = {
                'Model': model,
                'MAE': f"{res['MAE']:.4f}",
                'RMSE': f"{res['RMSE']:.4f}",
                'R2': f"{res['R2']:.4f}"
            }
            rows.append(row)
            
        df = pd.DataFrame(rows)
        # Markdown table manual generation
        md_content += "| " + " | ".join(df.columns) + " |\n"
        md_content += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
        for _, r in df.iterrows():
            md_content += "| " + " | ".join(r.values) + " |\n"
        md_content += "\n"
        
    except FileNotFoundError:
        md_content += "Metrics file not found.\n"

    # 2. Feature Importance
    md_content += "## Top Feature Importance (Best Model)\n"
    try:
        imp_df = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_v2_feature_importance.csv'))
        top_10 = imp_df.head(10)
        
        md_content += "| Feature | Importance |\n"
        md_content += "| --- | --- |\n"
        for _, r in top_10.iterrows():
            md_content += f"| {r['Feature']} | {r['Importance']:.4f} |\n"
            
        md_content += "\n**Interpretation:**\n"
        top_feat = top_10.iloc[0]['Feature']
        md_content += f"- The most influential feature is `{top_feat}`, indicating that... [agent to complete contextually]\n"
        
    except FileNotFoundError:
        md_content += "Feature importance file not found.\n"
        
    with open(OUTPUT_FILE, 'w') as f:
        f.write(md_content)
        
    print(f"Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_duration_report()
