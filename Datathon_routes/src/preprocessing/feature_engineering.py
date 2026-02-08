import pandas as pd # turbo
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler, OrdinalEncoder

# Paths
PROCESSED_DATA_DIR = r'data/processed'
MODELS_DIR = r'models' # To save encoders/scalers

def feature_engineering():
    print("Loading split data...")
    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'train.csv'))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'test.csv'))
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # ... (rest of the code is unchanged until saving) ...
    
    # 1. Encode Congestion Category (Target/Feature)
    # Order: Low -> 0, Medium -> 1, High -> 2
    print("Encoding congestion_category...")
    category_order = [['Low', 'Medium', 'High']]
    ord_enc = OrdinalEncoder(categories=category_order)
    
    # Fit on known categories (we know them)
    train_df['congestion_category_encoded'] = ord_enc.fit_transform(train_df[['congestion_category']])
    test_df['congestion_category_encoded'] = ord_enc.transform(test_df[['congestion_category']])
    
    joblib.dump(ord_enc, os.path.join(MODELS_DIR, 'congestion_encoder.pkl'))
    
    # 2. Encode Categoricals
    cat_cols = ['origin', 'destination', 'route_id']
    # Use LabelEncoder using combined classes to handle unseen labels in test if any (though time split might catch all routes if data is dense enough)
    # Actually, if new route appears in test (time split), LE will fail.
    # Safe approach: Fit on concatenated unique values.
    
    for col in cat_cols:
        print(f"Encoding {col}...")
        le = LabelEncoder()
        # Fit on all unique values from both train and test to avoid error
        all_values = pd.concat([train_df[col], test_df[col]]).unique()
        le.fit(all_values)
        
        train_df[f'{col}_encoded'] = le.transform(train_df[col])
        test_df[f'{col}_encoded'] = le.transform(test_df[col])
        
        joblib.dump(le, os.path.join(MODELS_DIR, f'{col}_encoder.pkl'))
        
    # 3. Scale Numericals
    # Identify numerical columns for scaling.
    # We should exclude targets and encoded columns and timestamp.
    # Candidates:
    feature_cols = [
        'route_distance_km', 'wind_speed_kmph', 'temperature_celsius', 
        'precipitation_mm', 'visibility_km', 'humidity_percent', 'aqi',
        'traffic_volume', 'lag_congestion_1h', 'lag_volume_1h', 
        'lag_travel_time_1h', 'rolling_congestion_3h'
    ]
    
    # Verify cols exist
    available_cols = [c for c in feature_cols if c in train_df.columns]
    print(f"Scaling columns: {available_cols}")
    
    scaler = StandardScaler()
    train_df[available_cols] = scaler.fit_transform(train_df[available_cols])
    test_df[available_cols] = scaler.transform(test_df[available_cols])
    
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    
    # Save encoded data
    print("Saving encoded data...")
    train_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'train_encoded.csv'), index=False)
    test_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'General', 'test_encoded.csv'), index=False)
    print("Done.")

if __name__ == "__main__":
    feature_engineering()
