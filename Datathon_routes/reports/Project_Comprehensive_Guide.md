# 📘 Comprehensive Project Guide: Urban Traffic Forecasting

This document provides a complete, detailed walkthrough of the entire machine learning pipeline developed for the Urban Traffic Forecasting project. It covers every step from raw data ingestion to final model selection.

---

## 🏗️ Phase 1: Data Preprocessing
**Goal**: Transform the raw, messy traffic logs into clean, structured datasets.

### 1. Raw Data Ingestion
- **Source**: `data/raw/mumbai_multi_route_traffic_INTELLIGENCE_READY.csv`
- **Initial State**: A chronological log of traffic updates (timestamp, route_id, speed, volume, etc.).

### 2. Cleaning & Formatting
- **Timestamp Conversion**: Converted string timestamps to Python `datetime` objects for temporal sorting.
- **Sorting**: Crucial step. Data was sorted by `route_id` then `timestamp`. This ensures that past events (t-1) actually precede current events (t) in the dataframe, which is required for lag generation.
- **Handling Missing Values**:
    - **Dropping**: Rows with `NaN` caused by lag creation (the first few rows of every route) were dropped.
    - **Imputation**: Small gaps in sensor data (`traffic_volume`) were filled using linear interpolation.

---

## ⚙️ Phase 2: Feature Engineering
**Goal**: Create meaningful predictors (features) that help models understand traffic patterns. We created two distinct sets of features.

### A. General Features (Row-wise)
*Used for Classification, Congestion Index, and Travel Time.*

1.  **Temporal Decomposition**:
    - Extracted `hour` (0-23), `day_of_week` (0-6), `month`.
    - **Cyclical Encoding**: To help models understand that hour 23 is close to hour 0, we could use sin/cos transforms, but simple tree models handled the raw numbers well.
    - `is_weekend` & `is_rush_hour`: Boolean flags for peak traffic periods.

2.  **Lag Features (Autocorrelation)**:
    - Traffic is highly autocorrelated (if it's bad now, it was probably bad 10 mins ago).
    - Created `lag_congestion_15m`, `lag_congestion_1h`, `lag_volume_1h`.

3.  **Rolling Statistics (Trends)**:
    - `rolling_mean_3h`: To capture the "mood" of traffic over the last few hours.
    - `congestion_delta`: Difference between current traffic and 1 hour ago. (Is it getting worse or better?)

4.  **Interaction Features**:
    - `volume_per_lane`: Traffic volume divided by number of lanes.
    - `weather_severity`: A weighted score combining rain, visibility, and wind.

### B. Specialized "Block-Start" Features
*Used exclusively for Block Duration prediction.*

*   **The Logic**: Predicting duration at *every minute* is noisy (mostly 0s). We focused on the **Start Event** (when `is_congested` flips from 0 to 1).
*   **Unique Features**:
    - `avg_duration_prior`: Historical average duration for this specific route (calculated only on training data to prevent leakage).
    - `event_intensity`: External events (sports, concerts) that might prolong jams.
    - `congestion_delta_1h`: High momentum (rapidly dropping speed) at `t_start` usually signals a longer jam.

---

## 🤖 Phase 3: Model Training Strategies

### 1. Classification (Congestion Category)
- **Objective**: Predict `Low`, `Medium`, or `High` severity.
- **Models**:
    - **Logistic Regression**: Best performer (~99.5%). Simple, interpretable, and effective because the categories are linearly separable based on `congestion_index`.
    - **Random Forest / XGBoost**: Also high accuracy (~99%) but overkill for this specific mapped task.

### 2. General Regression (Congestion Index & Travel Time)
- **Objective**: Predict continuous values for every 15-minute interval.
- **Models**:
    - **Random Forest**: The champion for `Actual Travel Time` (R² > 0.999). It perfectly learned the non-linear mapping between speed, distance, and time.
    - **LightGBM**: Champion for `Congestion Index` (R² > 0.997). Fast and accurate.
    - **Deep Learning (GRU/LSTM/TCN)**: Tested but performed worse than trees. The tabular nature of the data favors gradient boosting over sequence models here.

### 3. Block Duration (The Main Challenge)
This was the hardest task. We iterated through four strategies:

#### Strategy A: General Regression (Naïve)
*   **Approach**: Predict duration for every row.
*   **Result**: High R² (~0.40) but misleading. The models were great at predicting "0" (no traffic) but terrible at predicting actual jams (MAE ~14 hours).

#### Strategy B: Baseline (Block-Start)
*   **Approach**: Train only on `t_start` rows.
*   **Result**: R² ~0.20, but **MAE dropped to ~9h**. The model learned to distinguish short vs. long jams better.

#### Strategy C: Refined (Log-Transformation)
*   **Approach**: Target = `log(1 + duration)`.
*   **Goal**: Reduce the impact of "Long Tail" outliers (e.g., rare 12-hour jams).
*   **Result**: **Best MAE (~8.1 hours)**. While R² was lower, the errors were the smallest. This is the most "safe" model.

#### Strategy D: Aggressive Tuning & Deep Learning
*   **Approach**: RandomizedSearchCV for XGBoost and LSTM Sequence models.
*   **Result**:
    - **Tuned XGBoost**: Improved R² to ~0.22. Good balance.
    - **LSTM**: Failed to beat simple trees. The sequences (6 hours of history) didn't add enough signal to justify the complexity.

---

## 🏆 Final Summary of "Best" Models

| Task | Best Model | Why? |
| :--- | :--- | :--- |
| **Classification** | **Logistic Regression** | Simple, fast, near-perfect accuracy. |
| **Congestion Index** | **LightGBM** | Fastest inference, highest R². |
| **Travel Time** | **Random Forest** | Perfectly captured the physics of travel time. |
| **Block Duration** | **XGBoost (Block-Start)** | Best balance of predicting raw hours without over-fitting to outliers. |
