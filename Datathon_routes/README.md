# Urban Traffic Forecasting & Route Recommendation System

An advanced Machine Learning system for route-level traffic forecasting in Mumbai. This project utilizes historical traffic data to predict congestion levels, travel times, and duration of traffic blocks, enabling intelligent route recommendations.

## Project Structure

- **`data/`**: Processed datasets (train/test splits, block-start data).
- **`src/`**: Source code for data pipelines, model training, and reporting.
- **`models/`**: Saved trained model artifacts (PKL, H5).
- **`reports/`**: Generated metrics, predictions, and visualization figures.

## Key Features

1.  **Multi-Task Forecasting**:
    *   **Classification**: Predicts Congestion Category (Low/Medium/High).
    *   **Regression**: Predicts Congestion Index, Event Duration, and Actual Travel Time.
2.  **Advanced Modeling**:
    *   Utilizes Random Forest, XGBoost, and LightGBM.
    *   Deploys Deep Learning models: LSTM, GRU, TCN.
    *   Specialized "Block-Start" modeling for accurate congestion duration## 📂 Project Structure
```
data/
├── raw/            # Original dataset
├── processed/      # Cleaned & Featured data
models/             # Saved .pkl and .h5 models
reports/            # Metrics, predictions, figures
├── figures/        # Visualizations (PNG)
src/
├── preprocessing/  # Data cleaning & Feature engineering
│   ├── data_preprocessing.py
│   ├── data_preprocessing_duration.py
├── models/         # Model training scripts
│   ├── models_regression.py
│   ├── models_classification.py
│   ├── models_duration.py
│   ├── models_duration_tuned.py
│   ├── models_duration_lstm.py
│   ├── models_stacking.py
├── evaluation/     # Reporting & Visualization
│   ├── generate_comparison_md.py
│   ├── visualization.py
│   ├── visualization_duration.py
├── utils/          # Helper scripts
```

## 🚀 How to Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Pipeline**
   ```bash
   # 1. Data Processing
   python src/preprocessing/data_preprocessing.py
   python src/preprocessing/data_preprocessing_duration.py

   # 2. Train Models
   python src/models/models_classification.py
   python src/models/models_regression.py
   python src/models/models_duration_tuned.py  # Best Duration Model

   # 3. Generate Reports & Visualizations
   python src/evaluation/visualization.py
   python src/evaluation/visualization_duration.py
   python src/evaluation/generate_comparison_md.py
   ```

3. **View Results**
   - Check `reports/model_comparison.md` for a consolidated performance report.
   - Best models are highlighted with 🏆.
   - 📘 **Feature Engineering Details**: See `reports/feature_engineering.md`.
   - 📖 **Complete Project Guide**: See `reports/Project_Comprehensive_Guide.md` for a detailed end-to-end explanation.
