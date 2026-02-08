import pandas as pd
import os
from datetime import datetime

# Paths
RAW_DATA_PATH = r'data/raw/mumbai_multi_route_traffic_INTELLIGENCE_READY.csv'
PROCESSED_DATA_DIR = r'data/processed'

def preprocess_data():
    print("Loading data...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 1. Convert timestamp
    print("Converting timestamp...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 2. Sort data
    print("Sorting data...")
    if 'route_id' in df.columns:
        df = df.sort_values(by=['route_id', 'timestamp'])
    else:
        print("Warning: route_id not found, sorting by timestamp only")
        df = df.sort_values(by=['timestamp'])
        
    # 3. Handle NaNs
    print("Handling NaNs...")
    initial_shape = df.shape
    # Drop NaNs from lag/rolling features specifically or all NaNs?
    # User said: "Drop rows with NaNs created by lag features."
    # Let's drop all na rows for now to be safe as ML models don't like them usually
    df = df.dropna()
    final_shape = df.shape
    print(f"Dropped {initial_shape[0] - final_shape[0]} rows. Final shape: {final_shape}")
    
    # 4. Train-Test Split (Time-based)
    print("Splitting data...")
    # We want to split based on time, maintaining the order.
    # Simple approach: Cutoff at 80% mark of sorted unique timestamps or just per route?
    # To respect the "time-series" nature per route, we might want to split per route or globally if all routes share timeframe.
    # Let's split globally by time to simulate "future" prediction for all routes.
    
    unique_timestamps = df['timestamp'].unique()
    split_idx = int(len(unique_timestamps) * 0.8)
    split_date = unique_timestamps[split_idx]
    
    print(f"Split date: {split_date}")
    
    train_df = df[df['timestamp'] < split_date]
    test_df = df[df['timestamp'] >= split_date]
    
    print(f"Train set shape: {train_df.shape}")
    print(f"Test set shape: {test_df.shape}")
    
    # 5. Save
    print("Saving data...")
    # Save to 'General' subfolder
    general_dir = os.path.join(PROCESSED_DATA_DIR, 'General')
    os.makedirs(general_dir, exist_ok=True)
    
    train_df.to_csv(os.path.join(general_dir, 'train.csv'), index=False)
    test_df.to_csv(os.path.join(general_dir, 'test.csv'), index=False)
    print("Done.")

if __name__ == "__main__":
    preprocess_data()
