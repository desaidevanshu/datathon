# 🏆 Final Comprehensive Model Comparison

This report provides a detailed performance comparison of all models trained during this project, covering Classification (`congestion_category`), General Regression (`congestion_index`, `actual_travel_time_min`), and the specialized `block_duration_hours` experiments.

## 1. Classification (Congestion Category)
**Task**: Predict `Low`, `Medium`, or `High` congestion based on traffic features.

| Model | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** 🏆 | **99.59%** | **0.9959** | **0.9959** | **0.9959** |
| XGBoost | 99.46% | 0.9946 | 0.9946 | 0.9946 |
| Random Forest | 98.91% | 0.9891 | 0.9891 | 0.9891 |

---

## 2. General Regression Tasks
**Task**: Predict continuous traffic metrics for every timestamp.

### A. Congestion Index (0-100)
| Model | MAE | RMSE | R² Score | MAPE |
| :--- | :--- | :--- | :--- | :--- |
| **LightGBM** 🏆 | **0.0045** | **0.0064** | **0.9979** | **0.70%** |
| Random Forest | 0.0048 | 0.0071 | 0.9974 | 0.75% |
| XGBoost | 0.0175 | 0.0210 | 0.9767 | 2.62% |
| GRU (DL) | 0.0363 | 0.0455 | 0.8910 | 5.63% |
| LSTM (DL) | 0.0382 | 0.0473 | 0.8822 | 5.82% |
| TCN (DL) | 0.0694 | 0.0915 | 0.5587 | 10.38% |

### B. Actual Travel Time (Minutes)
| Model | MAE | RMSE | R² Score | MAPE |
| :--- | :--- | :--- | :--- | :--- |
| **Random Forest** 🏆 | **0.35 min** | **0.55** | **0.9998** | **0.78%** |
| LightGBM | 0.51 min | 0.85 | 0.9995 | 1.06% |
| XGBoost | 4.26 min | 7.29 | 0.9654 | 8.00% |
| TCN (DL) | 16.30 min | 23.25 | 0.6474 | 31.53% |
| LSTM (DL) | 17.06 min | 24.86 | 0.5969 | 32.22% |
| GRU (DL) | 17.90 min | 25.83 | 0.5649 | 35.60% |

---

## 3. Block Duration Deep Dive (Specialized)
**Task**: Predict how long a traffic jam will last (in hours). We tested multiple strategies.

### 📉 Why different R² values?
*   **General Models** predict *every* row (including non-congested 0s). High R² (~0.43) is inflated by easier "0" predictions but they have **High Error (MAE ~14h)** when traffic actually happens.
*   **Block-Start Models** predict *only* when congestion starts. R² is lower (harder task), but **MAE is much better (~9h)**.
*   **Log-Models** attempt to squash outliers. They achieved the **Best MAE (~8.1h)** but lower R².

### Comprehensive Comparison Table

| Strategy | Model | MAE (Hours) | RMSE | R² Score | Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Refined (Log)** | **XGBoost** 🏆 | **8.10** | 17.69 | 0.1414 | **Best Error (Lowest MAE)**. |
| **Refined (Log)** | Stacking Ensemble | 8.13 | 17.75 | 0.1354 | |
| **Refined (Log)** | LightGBM | 8.13 | 17.67 | 0.1435 | |
| **Refined (Log)** | Random Forest | 8.37 | 17.97 | 0.1140 | |
| | | | | | |
| **Tuned** | **XGBoost (Aggressive)** | 9.06 | 16.86 | **0.2205** | **Best Balance** of R² and MAE for Block-Start. |
| **Tuned** | LSTM Sequence (6h) | 8.89 | 17.37 | 0.1352 | Deep Learning approach. |
| | | | | | |
| **Baseline (Block-Start)** | Random Forest | 9.20 | 17.03 | 0.2041 | |
| **Baseline (Block-Start)** | LightGBM | 9.24 | 16.99 | 0.2080 | |
| **Baseline (Block-Start)** | XGBoost | 9.33 | 16.96 | 0.2111 | |
| | | | | | |
| **General (All Rows)** | LightGBM | 13.60 | 23.55 | *0.4062* | High R² but **High MAE** (Poor practical utility). |
| **General (All Rows)** | Random Forest | 13.77 | 23.84 | *0.3913* | |
| **General (All Rows)** | XGBoost | 14.05 | 23.42 | *0.4124* | |
| **General (All Rows)** | GRU | 15.11 | 22.90 | *0.4385* | |
| **General (All Rows)** | LSTM | 15.23 | 23.01 | *0.4331* | |
| **General (All Rows)** | TCN | 17.40 | 26.59 | 0.2429 | |

### ✅ Recommendation
For **Block Duration**, we recommend using the **Tuned XGBoost** or **Refined Log-XGBoost** models. Even though their R² appears lower than the General models, their **Mean Absolute Error (MAE)** is nearly **40-50% lower** (8-9 hours vs 14-15 hours), making them much more useful for real-world prediction.
