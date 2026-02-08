# Feature Engineering Documentation

This document explicitly details the feature engineering process undertaken to transform raw traffic data into interaction-ready features for our machine learning models.

## 1. Data Cleaning & Preprocessing
**Script:** `src/preprocessing/data_preprocessing.py`

### Handling Missing Values
- **Lag Features**: Initial rows for each route naturally have missing lag values (e.g., `lag_1h` is NaN for the first hour). These distinct initial rows were dropped to ensure model stability.
- **Interpolation**: Minor gaps in `traffic_volume` or `average_speed` were filled using linear interpolation based on time.

### Datetime Conversion
- The `timestamp` column was converted to datetime objects.
- Data was sorted by `route_id` and `timestamp` to ensure correct temporal feature generation.

## 2. Feature Generation (General Models)
**Script:** `src/preprocessing/feature_engineering.py`

These features were used for Classification and General Regression (Congestion Index, Travel Time).

### Temporal Features
Extracted from timestamp to capture cyclical patterns:
- `hour`: Hour of day (0-23).
- `day_of_week`: Monday (0) to Sunday (6).
- `is_weekend`: Binary flag (1 if Sat/Sun, else 0).
- `is_rush_hour`: Flag for peak traffic times (08:00-11:00 and 17:00-20:00).

### Lag & Rolling Features
To capture temporal dependencies (autocorrelation):
- **Lags**: `congestion_index` lagged by 15min, 30min, 1h, 24h.
- **Rolling Stats**: Moving averages of `congestion_index` and `traffic_volume` over 1h and 3h windows.

### Interaction Features
- `volume_per_lane`: `traffic_volume` / `lane_count`.
- `congestion_severity_index`: A composite score combining `congestion_index` and `weather_severity`.

## 3. Advanced Feature Engineering (Duration Modeling)
**Script:** `src/preprocessing/data_preprocessing_duration.py`

Specialized features were created specifically for predicting **Block Duration** at the moment a congestion event starts (`is_congested` 0 -> 1).

### The "Block-Start" Logic
We identified discrete "Congestion Blocks" and engineered features *only* available at the start time $t_{start}$:
1.  **Strictly Prior Info**: We restricted features to $t \le t_{start}$ to prevent data leakage (i.e., we cannot know the future speed when predicting duration).

### Key Predictors
1.  **Momentum (Deltas)**:
    - `congestion_delta_1h`: Change in congestion over the last hour.
    - `volume_delta_1h`: Change in volume.
    - *Logic*: Is traffic rapidly worsening or stabilizing?

2.  **Historical Route Stats**:
    - `avg_duration_prior`: The average duration of *past* congestion events on this specific route.
    - *Leakage Prevention*: Calculated using only the training set.

3.  **Environmental Context**:
    - `weather_severity`: Numerical score of weather conditions.
    - `event_intensity`: Impact of nearby events.
    - `lane_closure_ratio`: Percentage of lanes closed.

## 4. Encoding
- **Categorical Variables**: `route_id`, `congestion_category` (Target).
- **Method**: Label Encoding was used to convert these string identifiers into numerical sequences.

## 5. Scaling
- **Scaler**: `StandardScaler` (Z-score normalization).
- **Applied To**: All numerical features (e.g., `traffic_volume`, `average_speed`, `lags`).
- **Why**: Essential for models like Logistic Regression and Neural Networks (LSTM/GRU) to converge faster and avoid bias toward larger magnitude features. Tree-based models (RF/XGB) are less sensitive but still benefit.

## 6. Dataset Breakdown
Here is exactly what each file in `data/processed/` is used for:

| Dataset File | Purpose | Scope | Key Features |
| :--- | :--- | :--- | :--- |
| `train_encoded.csv` <br> `test_encoded.csv` | **General Tasks**:<br>- Classification (Category)<br>- Regression (Congestion Index, Travel Time) | **All Rows**:<br>Contains every timestamp, both congested and free-flow. | `hour`, `day_of_week`, `lag_1h`, `rolling_mean_3h`, `weather_severity`. |
| `train_duration.csv` <br> `test_duration.csv` | **Duration (Baseline)**:<br>- Predicting `block_duration_hours`. | **Block-Start Only**:<br>Filtered to only include the *start* time of a congestion event (0 -> 1 transition). | `congestion_delta_1h`, `avg_duration_prior`, `event_intensity`. |
| `train_duration_refined.csv` <br> `test_duration_refined.csv` | **Duration (Log)**:<br>- Predicting `log(1+duration)`. | **Block-Start Only**:<br>Same as above, but target is transformed. | Same as above. |
| `train.csv` <br> `test.csv` | **Intermediate**:<br>- Base split before encoding. | All Rows. | Raw features + basic cleaning. |
