import pandas as pd
import numpy as np
import os

# Paths
RAW_DATA_PATH = r'data/raw/mumbai_multi_route_traffic_INTELLIGENCE_READY.csv'
PROCESSED_DATA_DIR = r'data/processed'

def create_duration_dataset_refined():
    print("Loading raw data...")
    df = pd.read_csv(RAW_DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort carefully
    df = df.sort_values(by=['route_id', 'timestamp']).reset_index(drop=True)
    
    # --- Feature Engineering ---
    print("Engineering Refined Features...")
    
    # 1. Avg Speed
    # speed (km/h) = distance (km) / (time (min) / 60)
    # Avoid division by zero
    df['avg_speed_kmph'] = df['route_distance_km'] / (df['actual_travel_time_min'] / 60).replace(0, 0.1)
    
    def group_shift(col, n):
        return df.groupby('route_id')[col].shift(n)
        
    # 2. Lags (1, 2, 3, 6)
    for lag in [1, 2, 3, 6]:
        df[f'lag_congestion_{lag}h'] = group_shift('congestion_index', lag)
        df[f'lag_volume_{lag}h'] = group_shift('traffic_volume', lag)
    
    df['lag_travel_time_1h'] = group_shift('actual_travel_time_min', 1)
    df['lag_speed_1h'] = group_shift('avg_speed_kmph', 1)
    
    # 3. Trends (Deltas)
    df['congestion_delta_1h'] = df['lag_congestion_1h'] - df['lag_congestion_2h']
    df['congestion_delta_3h'] = df['lag_congestion_1h'] - group_shift('congestion_index', 4)
    
    # 4. Rolling Features (3h, 6h)
    # Using shift(1) to strictly avoid leakage
    for window in [3, 6]:
        df[f'rolling_congestion_{window}h'] = df.groupby('route_id')['congestion_index'].shift(1).rolling(window=window).mean().reset_index(0, drop=True)
        df[f'rolling_volume_{window}h'] = df.groupby('route_id')['traffic_volume'].shift(1).rolling(window=window).mean().reset_index(0, drop=True)
        
    # 5. Identify Block Starts
    df['prev_is_congested'] = group_shift('is_congested', 1).fillna(0)
    df['is_block_start'] = ((df['is_congested'] == 1) & (df['prev_is_congested'] == 0)).astype(int)
    
    print("Filtering for block start events...")
    duration_df = df[df['is_block_start'] == 1].copy()
    
    # Drop rows missing features due to lags
    initial_len = len(duration_df)
    duration_df = duration_df.dropna()
    print(f"Dropped {initial_len - len(duration_df)} rows. Final samples: {len(duration_df)}")
    
    # --- Target Transformation ---
    duration_df['log_block_duration'] = np.log1p(duration_df['block_duration_hours'])
    
    # Select Columns
    feature_cols = [
        'timestamp', 'route_id', 
        'block_duration_hours', 'log_block_duration', # Targets
        # Context at Start
        'congestion_index', 'traffic_volume', 'avg_speed_kmph',
        'weather_severity', 'event_intensity', 'lane_closure_ratio', 
        'hour', 'is_weekend', 'is_monsoon',
        # Lags
        'lag_congestion_1h', 'lag_congestion_2h', 'lag_congestion_3h', 'lag_congestion_6h',
        'lag_volume_1h', 'lag_volume_2h', 'lag_volume_3h', 'lag_volume_6h',
        'lag_travel_time_1h', 'lag_speed_1h',
        # Trends
        'congestion_delta_1h', 'congestion_delta_3h',
        'rolling_congestion_3h', 'rolling_volume_3h',
        'rolling_congestion_6h', 'rolling_volume_6h'
    ]
    
    duration_df_final = duration_df[feature_cols].copy()
    
    # Encode Route ID
    duration_df_final['route_id_encoded'] = duration_df_final['route_id'].astype('category').cat.codes
    
    # --- Split Data ---
    unique_timestamps = duration_df_final['timestamp'].sort_values().unique()
    split_idx = int(len(unique_timestamps) * 0.8)
    split_date = unique_timestamps[split_idx]
    print(f"Split date: {split_date}")
    
    train_dur = duration_df_final[duration_df_final['timestamp'] < split_date].copy()
    test_dur = duration_df_final[duration_df_final['timestamp'] >= split_date].copy()
    
    # --- Per-Route Stats (Leakage Free) ---
    print("Computing per-route stats on Training Data Only...")
    
    # Calculate stats on TRAIN
    route_stats = train_dur.groupby('route_id').agg({
        'block_duration_hours': 'mean',
        'congestion_index': 'mean'
    }).rename(columns={
        'block_duration_hours': 'avg_duration_prior',
        'congestion_index': 'avg_congestion_prior'
    })
    
    # Map to Train
    train_dur = train_dur.merge(route_stats, on='route_id', how='left')
    
    # Map to Test (using Train stats)
    test_dur = test_dur.merge(route_stats, on='route_id', how='left')
    
    # Fill missing in Test (for new routes not in train, though unlikely here)
    # Fill with global train mean
    global_mean_dur = train_dur['block_duration_hours'].mean()
    global_mean_cong = train_dur['congestion_index'].mean()
    
    test_dur['avg_duration_prior'] = test_dur['avg_duration_prior'].fillna(global_mean_dur)
    test_dur['avg_congestion_prior'] = test_dur['avg_congestion_prior'].fillna(global_mean_cong)
    
    # Save
    # Save to 'Duration' subfolder
    duration_dir = os.path.join(PROCESSED_DATA_DIR, 'Duration')
    os.makedirs(duration_dir, exist_ok=True)
    
    train_dur.to_csv(os.path.join(duration_dir, 'train_duration_refined.csv'), index=False)
    test_dur.to_csv(os.path.join(duration_dir, 'test_duration_refined.csv'), index=False)
    
    print("Refined Duration datasets created.")

if __name__ == "__main__":
    create_duration_dataset_refined()
