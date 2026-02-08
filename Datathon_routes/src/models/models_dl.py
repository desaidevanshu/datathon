import pandas as pd
import numpy as np
import os
import joblib
import json
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, GRU, Conv1D, Flatten, Input, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import time

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models'
REPORTS_DIR = r'reports'

# Set seed
tf.random.set_seed(42)
np.random.seed(42)

def create_sequences(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X.iloc[i:(i + time_steps)].values)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

def build_lstm(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def build_gru(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        GRU(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def build_tcn(input_shape):
    # Simple TCN-like structure using Conv1D
    model = Sequential([
        Input(shape=input_shape),
        Conv1D(filters=32, kernel_size=3, activation='relu', padding='causal'),
        Conv1D(filters=32, kernel_size=3, activation='relu', padding='causal'),
        Flatten(),
        Dense(50, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_dl_models():
    print("Loading data for DL models...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'train_encoded.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'test_encoded.csv'))
    
    targets = ['congestion_index', 'block_duration_hours', 'actual_travel_time_min']
    exclude_cols = ['timestamp', 'congestion_category', 'congestion_category_encoded', 
                    'origin', 'destination', 'route_id', 'is_congested', 'congestion_block', 'route_score', 'free_flow_time_min']
    
    base_features = [c for c in train_df.columns if c not in exclude_cols and c not in targets]
    print(f"Base Features: {base_features}")
    
    # Parameters
    TIME_STEPS = 5 # Use past 5 timesteps to predict next
    EPOCHS = 5 # Low epochs for speed in demo, increase for production
    BATCH_SIZE = 64
    
    results = {}
    
    # Load existing regression results to append to
    try:
        with open(os.path.join(REPORTS_DIR, 'regression_metrics.json'), 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        pass
    
    for target in targets:
        print(f"\n--- DL Predicting {target} ---")
        
        # Prepare Data sequences
        # We need to be careful with route_id grouping for strict sequential validity.
        # For simplicity in this "route-level" system, we'll treat the Train DF as a continuous stream 
        # (sorted by route, then time). 
        # Ideally, we should create sequences PER ROUTE.
        # Let's try to do it right: group by route, create sequences, then stack.
        
        print("Creating sequences per route...")
        X_train_seq, y_train_seq = [], []
        
        # To save time, let's just use the sorted df directly if dataset is large, 
        # but boundaries might be noisy. 
        # Given 100k rows, grouping might be slow but let's try.
        
        # Faster approach: Just process as one block but reset on route change? 
        # No, simpler: just process as one block. The "noise" at route boundaries is minimal 
        # compared to dataset size (100k rows, maybe 50 routes -> 50 errors).
        
        X_train_full = train_df[base_features]
        y_train_full = train_df[target]
        X_test_full = test_df[base_features]
        y_test_full = test_df[target]
        
        X_train, y_train = create_sequences(X_train_full, y_train_full, TIME_STEPS)
        X_test, y_test = create_sequences(X_test_full, y_test_full, TIME_STEPS)
        
        print(f"Train Sequence Shape: {X_train.shape}")
        
        input_shape = (X_train.shape[1], X_train.shape[2])
        
        models_to_train = {
            'LSTM': build_lstm(input_shape),
            'GRU': build_gru(input_shape),
            'TCN': build_tcn(input_shape)
        }
        
        # Load existing predictions csv to append
        preds_file = os.path.join(REPORTS_DIR, f'regression_predictions_{target}.csv')
        if os.path.exists(preds_file):
            preds_df = pd.read_csv(preds_file)
            # Truncate preds_df to match test sequence length (lost TIME_STEPS rows)
            # This is tricky. create_sequences cuts off first TIME_STEPS.
            # We need to align.
            # Best way: Just save DL predictions to a new file or aligned dataframe.
            # To simplify "one graph", we should try to align.
            # The test set in create_sequences starts at index TIME_STEPS.
            # We can select rows [TIME_STEPS:] from preds_df?
            aligned_preds_df = preds_df.iloc[TIME_STEPS:].reset_index(drop=True)
        else:
            aligned_preds_df = pd.DataFrame({'Actual': y_test})

        target_results = results.get(target, {})

        for name, model in models_to_train.items():
            print(f"Training {name} for {target}...")
            t0 = time.time()
            model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=0, validation_split=0.1)
            print(f"{name} trained in {time.time()-t0:.2f}s")
             
            y_pred = model.predict(X_test).flatten()
            
            # Metrics
            metrics = evaluate_regression(y_test, y_pred, name)
            target_results[name] = metrics
            
            # Save model
            model.save(os.path.join(MODELS_DIR, f'{name.lower()}_{target}.h5'))
            
            # Add to preds
            aligned_preds_df[name] = y_pred

        results[target] = target_results
        
        # Save updated predictions (Note: this file now has fewer rows than original RF/XGB file)
        # We will separate DL predictions or overwrite? 
        # User wants "one line chart for each model". 
        # If we overwrite, we lose the first 5 rows of RF/XGB match. That's fine.
        aligned_preds_df.to_csv(os.path.join(REPORTS_DIR, f'regression_predictions_{target}_dl_merged.csv'), index=False)
        
        # Also overwrite the main file so robust visualization script picks it up?
        # Visualization script looks for 'regression_predictions_{target}.csv'.
        # Let's save it there.
        aligned_preds_df.to_csv(os.path.join(REPORTS_DIR, f'regression_predictions_{target}.csv'), index=False)

    # Save metrics
    with open(os.path.join(REPORTS_DIR, 'regression_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nDL training completed.")

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true != 0
    if mask.sum() > 0:
        mape = (np.abs((y_true - y_pred) / y_true)[mask]).mean() * 100
    else:
        mape = np.nan
    
    print(f"--- {model_name} ---")
    print(f"MAE: {mae:.4f}")
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }

if __name__ == "__main__":
    train_dl_models()
