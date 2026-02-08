import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

try:
    from src.data_loader import load_traffic_data
except ImportError:
    from data_loader import load_traffic_data

def create_sequences(df, target_col, sequence_length=5):
    """
    Creates multivariate time-series sequences.
    Features: VehicleCount, Speed, WeatherCondition, Hour, DayOfWeek, IsWeekend, NoveltyScore
    """
    # Canonical Features (Must match what we generate in train_lstm)
    feature_cols = [
        'VehicleCount', 'Speed', 
        'Hour', 'DayOfWeek', 'IsWeekend', 
        'WeatherCondition', 
        'NoveltyScore'
    ]
    
    # Ensure they exist (fill missing)
    for col in feature_cols:
        if col not in df.columns:
            if col == 'NoveltyScore': df[col] = 0.0
            elif col == 'WeatherCondition': df[col] = 'Clear'
            else: df[col] = 0
            
    # Encode Categorical (WeatherCondition)
    encoders = {}
    if df['WeatherCondition'].dtype == 'object':
        le = LabelEncoder()
        df['WeatherCondition'] = le.fit_transform(df['WeatherCondition'].astype(str))
        encoders['WeatherCondition'] = le
        
    # Scaling
    # Use MinMaxScaler for LSTM inputs usually 0-1 range is better than StdScaler
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    # Encode Target
    if df[target_col].dtype == 'object':
        le_target = LabelEncoder()
        df['target_encoded'] = le_target.fit_transform(df[target_col].astype(str))
        target_encoded_col = 'target_encoded'
        classes = le_target.classes_
        encoders['target'] = le_target
    else:
        target_encoded_col = target_col
        classes = sorted(df[target_col].unique())
        
    # Sliding Window per City
    X, y = [], []
    
    if 'City' in df.columns:
        for city, group in df.groupby('City'):
            group_data = group[feature_cols].values
            group_target = group[target_encoded_col].values
            
            for i in range(sequence_length, len(group_data)):
                X.append(group_data[i-sequence_length:i])
                y.append(group_target[i])
    else:
        # Fallback for single city dataset without City col
        data = df[feature_cols].values
        target = df[target_encoded_col].values
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(target[i])
            
    return np.array(X), np.array(y), classes, scaler, encoders, feature_cols
    
    X, y = [], []
    
    # 2. Sliding Window
    # Loop to create sequences
    for i in range(sequence_length, len(data)):
        X.append(data[i-sequence_length:i])
        y.append(target[i])
        
    return np.array(X), np.array(y), classes, scaler, encoders, feature_cols

if __name__ == "__main__":
    # Test
    df = load_traffic_data(r"c:/Users/Devanshu/OneDrive/Documents/datathon/synthetic_traffic_data.xml")
    X, y, classes, _ = create_sequences(df, 'CongestionLevel', sequence_length=5)
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Classes: {classes}")
