# Urban Traffic Forecasting - Final Model Comparison

## 1. Classification (Congestion Category)
| Model | Accuracy | F1 Score |
| --- | --- | --- |
| **Logistic Regression (Best)** 🏆 | 0.9959 | 0.9959 |
| Random Forest | 0.9891 | 0.9891 |
| XGBoost | 0.9946 | 0.9946 |


## 2. Regression Tasks (General)
### Predict: `congestion_index`
| Model | R2 | MAE |
| --- | --- | --- |
| Random Forest | 0.9974 | 0.0048 |
| XGBoost | 0.9767 | 0.0175 |
| **LightGBM (Best)** 🏆 | 0.9979 | 0.0045 |
| LSTM | 0.8822 | 0.0382 |
| GRU | 0.8910 | 0.0363 |
| TCN | 0.5587 | 0.0694 |


### Predict: `actual_travel_time_min`
| Model | R2 | MAE |
| --- | --- | --- |
| **Random Forest (Best)** 🏆 | 0.9998 | 0.3495 |
| XGBoost | 0.9654 | 4.2610 |
| LightGBM | 0.9995 | 0.5104 |
| LSTM | 0.5969 | 17.0550 |
| GRU | 0.5649 | 17.8962 |
| TCN | 0.6474 | 16.3004 |


## 3. Congestion Duration Modeling (Focus Area)
| Category | Model | R2 | MAE |
| --- | --- | --- | --- |
| Advanced (Tuned/LSTM) | **XGBoost (Aggressive Tuned) (Best)** 🏆 | 0.2205 | 9.0572 |
| Baseline (Block-Start) | XGBoost | 0.2111 | 9.3311 |
| Baseline (Block-Start) | LightGBM | 0.2080 | 9.2436 |
| Baseline (Block-Start) | Random Forest | 0.2041 | 9.1981 |
| Refined (Log) | LightGBM (Log) | 0.1435 | 8.1299 |
| Refined (Log) | XGBoost (Log) | 0.1414 | 8.1029 |
| Refined (Log) | Stacking Ensemble (Log) | 0.1354 | 8.1295 |
| Advanced (Tuned/LSTM) | LSTM Sequence (6h) | 0.1352 | 8.8899 |
| Refined (Log) | Random Forest (Log) | 0.1140 | 8.3705 |


