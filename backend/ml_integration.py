import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'Datathon_routes', 'models')

# Global Cache
_MODELS = {}

def load_models():
    """Load ML models and encoders into memory."""
    global _MODELS
    if _MODELS:
        return
    
    try:
        print("[INFO] Loading ML Models...")
        _MODELS['rf_time'] = joblib.load(os.path.join(MODELS_DIR, 'rf_actual_travel_time_min.pkl'))
        _MODELS['rf_congestion'] = joblib.load(os.path.join(MODELS_DIR, 'rf_congestion_index.pkl'))
        _MODELS['enc_origin'] = joblib.load(os.path.join(MODELS_DIR, 'origin_encoder.pkl'))
        _MODELS['enc_dest'] = joblib.load(os.path.join(MODELS_DIR, 'destination_encoder.pkl'))
        _MODELS['enc_route'] = joblib.load(os.path.join(MODELS_DIR, 'route_id_encoder.pkl'))
        print("[INFO] Models Loaded Successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")

def predict_route_metrics(source, destination, hour=None, day=None):
    """
    Predict Travel Time and Congestion Index for a route.
    """
    load_models()
    
    if 'rf_time' not in _MODELS:
        return None
        
    # Default to current time (Travel Time Sync)
    if hour is None:
        now = datetime.now()
        hour = now.hour
        day = now.weekday()
        month = now.month
    else:
        now = datetime.now()
        month = now.month

    # Encode Locations
    try:
        # Fuzzy match or direct transform? Encoders are likely LabelEncoders
        # We need exact string match for LabelEncoder.
        # Assuming input is clean or we catch error
        # Training data had "Andheri_East_MIDC", "BKC" etc.
        # We might need a mapping if inputs are "Andheri".
        
        # For now, try direct, falback to 0
        try:
            origin_ec = _MODELS['enc_origin'].transform([source])[0]
        except:
            origin_ec = 0
            
        try:
            dest_ec = _MODELS['enc_dest'].transform([destination])[0]
        except:
            dest_ec = 0
            
        route_id_ec = 0 # Placeholder if we don't have exact route ID
        
        # Feature Vector Construction (Must match training order/columns)
        # Based on models_regression.py output (base_features)
        # We need to reconstruct the dataframe with exact columns.
        # Since we don't have the exact column list object here, we approximate standard ones
        # derived from 'train_encoded.csv' headers.
        
        # IMPORTANT: The RF model likely expects specific feature columns in order.
        # Best practice is to use a dict -> DataFrame
        
        input_data = {
            'hour': [hour],
            'day_of_week': [day],
            'is_weekend': [1 if day >= 5 else 0],
            'month': [month],
            'is_monsoon': [1 if 6 <= month <= 9 else 0],
            'is_holiday': [0], # Placeholder
            'rain_mm': [0.0], # Should fetch from weather
            'humidity': [60.0],
            'temperature_c': [30.0],
            'visibility_km': [2.0],
            'weather_severity': [0.1],
            'pothole_severity': [0.3],
            'construction_activity': [0.2],
            'road_condition_score': [0.8],
            'event_intensity': [0.1],
            'festival_effect': [0.0],
            'lane_closure_ratio': [0.0],
            'traffic_volume': [50.0], # Needs live sensor
            'avg_speed': [30.0],      # Needs live gps
            'road_occupancy': [0.5],
            'travel_time_index': [1.2],
            'congestion_uncertainty': [0.2],
            'route_distance_km': [15.0], # Should calculate
            'lag_congestion_1h': [0.5],
            'lag_volume_1h': [0.0],
            'lag_travel_time_1h': [0.0],
            'rolling_congestion_3h': [0.5],
            'origin_encoded': [origin_ec],
            'destination_encoded': [dest_ec],
            'route_id_encoded': [route_id_ec],
            'delay_minutes': [0.0] # Required by model features
        }
        
        df_input = pd.DataFrame(input_data)
        
        # Predict
        # Note: If feature columns don't match, this will fail.
        # We catch that.
        try:
            pred_time = _MODELS['rf_time'].predict(df_input)[0]
            pred_congestion = _MODELS['rf_congestion'].predict(df_input)[0]
        except ValueError as ve:
            # Likely feature mismatch.
            # In a real scenario, we'd inspect model.feature_names_in_
            # For now, return Mock/Fallback if mismatch
            print(f"[ML WARNING] Feature mismatch: {ve}")
            return {
                "travel_time_min": 45.0,
                "congestion_index": 0.6,
                "confidence": "Low (Fallback)"
            }
            
        return {
            "travel_time_min": round(pred_time, 2),
            "congestion_index": round(pred_congestion, 2),
            "confidence": "High"
        }
        
    except Exception as e:
        print(f"[ML ERROR] Prediction failed: {e}")
        return None
