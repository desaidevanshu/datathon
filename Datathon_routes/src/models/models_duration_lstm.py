import pandas as pd
import numpy as np
import os
import joblib
import json
import time
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Paths
RAW_DATA_PATH = r'data/raw/mumbai_multi_route_traffic_INTELLIGENCE_READY.csv'
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

# Parameters
SEQUENCE_LENGTH = 6 # 6 hours history
FEATURES_TO_USE = [
    'congestion_index', 'traffic_volume', 'avg_speed_kmph', 
    'weather_severity', 'event_intensity'
]
TARGET = 'block_duration_hours'

def create_sequences(df, seq_length, features):
    X = []
    y = []
    indices = []
    
    # Group by route to ensure sequences don't cross routes
    # We only want sequences where the LAST step is a Block Start
    
    # First, identify block starts in the full DF
    df['prev_is_congested'] = df.groupby('route_id')['is_congested'].shift(1).fillna(0)
    df['is_block_start'] = ((df['is_congested'] == 1) & (df['prev_is_congested'] == 0)).astype(int)
    
    feature_data = df[features].values
    target_data = df[TARGET].values
    block_start_mask = df['is_block_start'].values
    route_ids = df['route_id'].values
    
    # Iterate through data
    # We need to be careful with route boundaries.
    # Faster way: Iterate per route
    
    print(f"Creating sequences of length {seq_length} for block starts...")
    
    for route in df['route_id'].unique():
        route_mask = (route_ids == route)
        route_data = feature_data[route_mask]
        route_target = target_data[route_mask]
        route_starts = block_start_mask[route_mask]
        
        if len(route_data) < seq_length:
            continue
            
        # We only take windows where the END (index i) is a block start
        for i in range(seq_length, len(route_data)):
            if route_starts[i] == 1:
                # Sequence is [i-seq_length : i]
                # Target is at i
                X.append(route_data[i-seq_length:i])
                y.append(route_target[i])
                
    return np.array(X), np.array(y)

def train_lstm_duration_model():
    print("Loading Raw Data for LSTM...")
    df = pd.read_csv(RAW_DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['route_id', 'timestamp']).reset_index(drop=True)
    
    # Feature Engineering (Speed)
    df['avg_speed_kmph'] = df['route_distance_km'] / (df['actual_travel_time_min'] / 60).replace(0, 0.1)
    
    # Scaling Features
    print("Scaling Features...")
    scaler = StandardScaler()
    df[FEATURES_TO_USE] = scaler.fit_transform(df[FEATURES_TO_USE])
    
    # Create Sequences
    X, y = create_sequences(df, SEQUENCE_LENGTH, FEATURES_TO_USE)
    
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    
    if len(X) == 0:
        print("Error: No sequences created. Check data.")
        return

    # Train-Test Split (Time-based logic is harder here with shuffled interactions, 
    # but we can use simple index split if data was sorted strictly by time.
    # However, create_sequences iterates by route.
    # Let's simple split: Last 20%
    
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Model Architecture
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LENGTH, len(FEATURES_TO_USE)))),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(1) # Regression
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    # Callbacks
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
    
    # Train
    print("Training LSTM...")
    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=50,
        batch_size=32,
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )
    
    # Evaluate
    y_pred = model.predict(X_test).flatten()
    
    metrics = evaluate_regression(y_test, y_pred, "LSTM Sequence (6h)")
    
    # Save
    model.save(os.path.join(MODELS_DIR, 'duration_lstm_seq.h5'))
    
    # Save Metrics
    results = {
        "LSTM Sequence (6h)": metrics
    }
    
    # Append to existing tuned metrics if possible
    try:
        with open(os.path.join(REPORTS_DIR, 'duration_tuned_metrics.json'), 'r') as f:
            existing = json.load(f)
            existing.update(results)
            results = existing
    except FileNotFoundError:
        pass
        
    with open(os.path.join(REPORTS_DIR, 'duration_tuned_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)

    # Append Predictions
    try:
        preds_df = pd.read_csv(os.path.join(REPORTS_DIR, 'duration_tuned_predictions.csv'))
        # Length might mismatch due to different split strategy (Sequence creation filters data differently)
        # So we save separate prediction file for LSTM to avoid alignment issues
        pd.DataFrame({'Actual': y_test, 'LSTM Sequence (6h)': y_pred}).to_csv(os.path.join(REPORTS_DIR, 'duration_lstm_predictions.csv'), index=False)
    except:
        pd.DataFrame({'Actual': y_test, 'LSTM Sequence (6h)': y_pred}).to_csv(os.path.join(REPORTS_DIR, 'duration_lstm_predictions.csv'), index=False)

    print("LSTM training completed.")

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    if mask.sum() > 0:
        mape = (np.abs((y_true - y_pred) / y_true)[mask]).mean() * 100
    else:
        mape = np.nan
    
    print(f"[{model_name}] MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}, MAPE: {mape:.2f}%")
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

if __name__ == "__main__":
    train_lstm_duration_model()
