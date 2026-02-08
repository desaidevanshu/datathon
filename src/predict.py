
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import joblib
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.osm_loader import get_road_network_stats
from src.scraper import get_live_weather, get_city_events, get_event_impact_score
from src.novelty_engine import HybridNoveltyEngine
from src.train_lstm import AdvancedTrafficLSTM
from src.sensor_interface import TrafficSensorNetwork, GPSDataStream

# Prediction Cache
_PRED_CACHE = {}
_PRED_TTL = 60 # 1 minute cache

def get_prediction_data(city="Mumbai, India", source=None, dest=None):
    """
    Core logic to generate traffic predictions.
    Returns a dictionary suitable for API response.
    Optimized with Result Caching.
    """
    import time
    
    # Check Cache
    cache_key = f"{city}|{source}|{dest}"
    now = time.time()
    
    if cache_key in _PRED_CACHE:
        cached = _PRED_CACHE[cache_key]
        if now - cached["timestamp"] < _PRED_TTL:
            # print(f"[CACHE HIT] Returning prediction for {cache_key}")
            return cached["data"]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 1. Load Artifacts & Model
    if not os.path.exists("lstm_artifacts.pkl") or not os.path.exists("traffic_lstm_model.pth"):
        return {"error": "Model or artifacts not found. Please train the model first."}
        
    artifacts = joblib.load("lstm_artifacts.pkl")
    scaler = artifacts['scaler']
    encoders = artifacts['encoders']
    feature_cols = artifacts['feature_cols']
    classes = artifacts['classes']
    
    input_size = len(feature_cols)
    num_classes = len(classes)
    model = AdvancedTrafficLSTM(input_size, 128, num_classes).to(device)
    model.load_state_dict(torch.load("traffic_lstm_model.pth", map_location=device))
    model.eval()

    # Load Novelty Engine
    try:
        novelty_engine = joblib.load("novelty_engine.pkl")
    except:
        novelty_engine = None

    # 2. Fetch Live Context
    city_name = city.split(',')[0]
    weather = get_live_weather(city_name)
    event_score = get_event_impact_score(city_name)
    events_data = get_city_events(city_name) # Returns {Incident: "Multiple"/"None", Events: [...]}
    events = events_data.get("Events", []) # Extract the events array

    # 3. Stream Synthesis
    sensors = TrafficSensorNetwork(location=f"{city} (Central)")
    gps = GPSDataStream(location=f"{city} (Cluster)")
    
    current_hour = 17 # Mock 5 PM
    seq_data = []
    
    # Generate Sequence
    for i in range(5):
        h = current_hour - (4-i)
        real_time_vol = sensors.get_realtime_volume()
        real_time_speed = gps.get_average_speed(real_time_vol)
        
        if event_score > 0.5:
            real_time_vol *= 1.2
            real_time_speed *= 0.7
            
        row = {
            'VehicleCount': int(real_time_vol),
            'Speed': round(real_time_speed, 2),
            'Hour': h,
            'DayOfWeek': 2,
            'IsWeekend': 0,
            'WeatherCondition': weather.get("Condition", "Clear"),
        }
        
        # Inject Source/Dest
        if 'origin' in encoders and source:
            try: row['origin'] = encoders['origin'].transform([source])[0]
            except: row['origin'] = 0
        elif 'origin' in feature_cols: row['origin'] = 0

        if 'destination' in encoders and dest:
            try: row['destination'] = encoders['destination'].transform([dest])[0]
            except: row['destination'] = 0
        elif 'destination' in feature_cols: row['destination'] = 0

        seq_data.append(row)
        
    df_seq = pd.DataFrame(seq_data)
    
    # Novelty Score Support
    if novelty_engine:
        novelty_cols = ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'origin', 'destination']
        for c in novelty_cols:
             if c not in df_seq.columns: df_seq[c] = 0.0
        X_nov = df_seq[novelty_cols].values
        try:
            nov_scores = novelty_engine.get_novelty_score(X_nov, context_data={'city': city})
            df_seq['NoveltyScore'] = nov_scores
        except:
             # Heuristic Fallback
             base_score = 0.4 if event_score > 0.5 else 0.0
             speed_dev = np.abs(df_seq['Speed'] - 50) / 50.0 
             df_seq['NoveltyScore'] = (base_score + (speed_dev * 0.3)).clip(0, 1)
    else:
        df_seq['NoveltyScore'] = 0.0
        
    # Preprocessing
    if 'WeatherCondition' in encoders:
        le = encoders['WeatherCondition']
        df_seq['WeatherCondition'] = df_seq['WeatherCondition'].apply(lambda x: x if x in le.classes_ else le.classes_[0])
        df_seq['WeatherCondition'] = le.transform(df_seq['WeatherCondition'])
        
    X_input_df = df_seq[feature_cols]
    X_scaled = scaler.transform(X_input_df)
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(0).to(device)
    
    # Predict Current
    with torch.no_grad():
        output = model(X_tensor)
        probs = torch.softmax(output, dim=1)
        conf, pred_idx = torch.max(probs, 1)
        
    congestion_level = classes[pred_idx.item()]
    confidence = conf.item() * 100

    # 4. Future Bottleneck Detection (Forecast +1, +2, +3 hrs)
    forecasts = []
    future_steps = 3
    
    # We will simulate the next steps by sliding the window
    # For a real autoregressive model, we'd predict features. 
    # Here, we project time and use the sensor stats for that future time.
    
    current_seq_list = seq_data.copy()
    
    for step in range(1, future_steps + 1):
        next_hour = (current_hour + step) % 24
        
        # Estimate conditions for next hour
        # (In a real system, we'd have a separate forecaster for Volume/Speed)
        # We use the sensor network's implicit periodic patterns (if any) or simple heuristics
        # For demo: specific bottlenecks might emerge
        
        # Heuristic: Evening Rush Hour Peak (17-19)
        vol_factor = 1.0
        if 17 <= next_hour <= 19: vol_factor = 1.3
        elif 8 <= next_hour <= 10: vol_factor = 1.2 # Morning
        else: vol_factor = 0.8 # Off-peak
        
        predicted_vol = sensors.get_realtime_volume() * vol_factor
        predicted_speed = gps.get_average_speed(predicted_vol)
        
        new_row = {
            'VehicleCount': int(predicted_vol),
            'Speed': round(predicted_speed, 2),
            'Hour': next_hour,
            'DayOfWeek': 2,
            'IsWeekend': 0,
            'WeatherCondition': weather.get("Condition", "Clear"),
        }
        
        # Persist location context
        if 'origin' in current_seq_list[-1]: new_row['origin'] = current_seq_list[-1]['origin']
        if 'destination' in current_seq_list[-1]: new_row['destination'] = current_seq_list[-1]['destination']
        
        # Append to sequence, remove oldest (Sliding Window)
        current_seq_list.append(new_row)
        current_seq_list.pop(0)
        
        # Prepare Tensor
        df_future = pd.DataFrame(current_seq_list)
        
        # Fix: Ensure NoveltyScore is present if required by scaler
        # We don't check feature_cols here to avoid dependency on global scope variables not available 
        # (though feature_cols is available in function scope).
        # Robust fix:
        if 'NoveltyScore' not in df_future.columns:
             df_future['NoveltyScore'] = 0.0

        # Preprocessing (Mirroring logic above)
        if 'WeatherCondition' in encoders:
            le = encoders['WeatherCondition']
            df_future['WeatherCondition'] = df_future['WeatherCondition'].apply(lambda x: x if x in le.classes_ else le.classes_[0])
            df_future['WeatherCondition'] = le.transform(df_future['WeatherCondition'])
            
        X_future = scaler.transform(df_future[feature_cols])
        X_future_tensor = torch.tensor(X_future, dtype=torch.float32).unsqueeze(0).to(device)
        
        with torch.no_grad():
            f_out = model(X_future_tensor)
            f_probs = torch.softmax(f_out, dim=1)
            f_conf, f_idx = torch.max(f_probs, 1)
            
        f_congestion = classes[f_idx.item()]
        
        forecasts.append({
            "step": f"+{step}h",
            "hour": next_hour,
            "congestion_level": str(f_congestion),
            "confidence": float(round(f_conf.item() * 100, 2)),
            "is_bottleneck": f_congestion in ['2', '3', 'High', 'Critical'] # Assuming '2' is High
        })

    
    # Construct Response
    response = {
        "city": city,
        "source": source,
        "destination": dest,
        "prediction": {
            "congestion_level": str(congestion_level),
            "confidence_score": float(round(confidence, 2)),
            "novelty_score": float(round(df_seq['NoveltyScore'].mean(), 4))
        },
        "forecast": forecasts,
        "context": {
            "weather": weather,
            "events": events_data,  # Return full structure: {Incident: "Multiple", Events: [...]}
            "event_impact_score": float(event_score)
        },
        "live_data": {
            "current_speed": float(round(df_seq['Speed'].iloc[-1], 2)),
            "current_volume": int(df_seq['VehicleCount'].iloc[-1])
        },
        "analysis": {
            "unique_insight": bool(df_seq['NoveltyScore'].mean() > 0.6),
            "insight_message": "Contextual adaptation detected." if df_seq['NoveltyScore'].mean() > 0.6 else "Standard traffic patterns."
        }
    }
    
    # Generate AI Traffic Bulletin
    try:
        from src.traffic_anchor import generate_traffic_bulletin
        # CAUTIOUS call - traffic_anchor should handle its own timeouts
        traffic_bulletin = generate_traffic_bulletin(response)
        response["traffic_bulletin"] = traffic_bulletin
    except Exception as e:
        print(f"[WARNING] Failed to generate traffic bulletin: {e}")
        response["traffic_bulletin"] = joblib.load("lstm_artifacts.pkl") # Just random error access?
        response["traffic_bulletin"] = f"Traffic is currently {congestion_level.lower()}."
    
    # Update Cache
    _PRED_CACHE[cache_key] = {
        "timestamp": now,
        "data": response
    }
    
    return response

def predict_live(city="Mumbai, India", source=None, dest=None):
    print(f"\n[INFO] Starting Advanced Traffic Intelligence Engine for {city}...")
    
    if source and dest:
        print(f"[INFO] Route Specific Mode: {source} -> {dest}")
    
    data = get_prediction_data(city, source, dest)
    
    if "error" in data:
        print(data["error"])
        return

    # Extract for Display
    pred = data["prediction"]
    ctx = data["context"]
    live = data["live_data"]
    events = ctx["events"]
    event_name = events.get("Details", {}).get("Name", "None")
    
    print("\n[INFO] Environment Sensed.")
    print(f"   Weather: {ctx['weather']['Condition']} ({ctx['weather']['Temperature']}C)")
    print(f"   Events:  {event_name} (Impact: {ctx['event_impact_score']})")
    
    print(f"\n{'-'*60}")
    print(f"| PREDICTION RESULT | {city.split(',')[0].upper():<31}|")
    print(f"{'-'*60}")
    print(f"| Congestion Level      | {pred['congestion_level'].upper():<30} |")
    print(f"| Confidence Score      | {pred['confidence_score']}%{' ':<26} |")
    print(f"| Novelty Score         | {pred['novelty_score']}{' ':<26} |")
    print(f"{'-'*60}")

    if data["analysis"]["unique_insight"]:
        print(f"\n  >> UNIQUE INSIGHT GENERATED:")
        print(f"     {data['analysis']['insight_message']}")
        
    # ... (Keep existing Traffic Management Strategy print logic if desired, or simplify)
    
    print(f"\n{'-'*60}")
    print("SYSTEM READY FOR DEPLOYMENT")
    print(f"{'-'*60}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Traffic Intelligence Engine")
    parser.add_argument("--city", type=str, default="Mumbai", help="City to predict for")
    parser.add_argument("--source", type=str, help="Start location")
    parser.add_argument("--dest", type=str, help="End location")
    
    args = parser.parse_args()
    
    predict_live(city=args.city, source=args.source, dest=args.dest)
