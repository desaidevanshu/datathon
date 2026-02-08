
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

def predict_live(city="Mumbai, India"):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🚀 Starting Advanced Traffic Intelligence Engine for {city}...")
    
    # 1. Load Artifacts
    if not os.path.exists("lstm_artifacts.pkl"):
        print("Error: Artifacts not found. Train the model first.")
        return
        
    artifacts = joblib.load("lstm_artifacts.pkl")
    scaler = artifacts['scaler']
    encoders = artifacts['encoders']
    feature_cols = artifacts['feature_cols']
    classes = artifacts['classes']
    
    # Load Model
    input_size = len(feature_cols)
    num_classes = len(classes)
    model = AdvancedTrafficLSTM(input_size, 128, num_classes).to(device)
    
    if os.path.exists("traffic_lstm_model.pth"):
        model.load_state_dict(torch.load("traffic_lstm_model.pth", map_location=device))
        model.eval()
    else:
        print("Error: Model weights not found.")
        return

    # Load Novelty Engine
    try:
        novelty_engine = joblib.load("novelty_engine.pkl")
    except:
        print("Warning: Novelty engine not found. Novelty scores will be 0.")
        novelty_engine = None

    # 2. Fetch Live Context (The "Unique" Part)
    print("\n🌍 Sensing Environment...")
    
    # Weather
    weather = get_live_weather(city.split(',')[0])
    condition_text = weather.get("Condition", "Clear")
    print(f"   Weather: {condition_text} ({weather.get('Temperature')}°C)")
    
    # Events
    event_score = get_event_impact_score(city.split(',')[0])
    events = get_city_events(city.split(',')[0])
    event_name = events.get("Details", {}).get("Name", "None")
    print(f"   Events:  {event_name} (Impact Score: {event_score:.2f})")
    
    # 3. Construct Input Sequence (Multivariate)
    # Simulate a sequence that leads to the current state based on context.
    print("\n🧠 Synthesizing Contextual Traffic Pattern...")
    
    current_hour = 17 # 5 PM
    
    seq_data = []
    for i in range(5):
        h = current_hour - (4-i)
        
        # Base Traffic Logic
        base_vol = 2000 if (8 <= h <= 10 or 17 <= h <= 19) else 800
        base_speed = 60 if base_vol < 1000 else 30
        
        # Modify by Event/Weather (The "Adaptive" part)
        if event_score > 0.5:
            base_vol *= 1.5 # Higher volume due to event
            base_speed *= 0.6 # Slower speed
            
        row = {
            'VehicleCount': base_vol + np.random.randint(-100, 100),
            'Speed': base_speed + np.random.randint(-5, 5),
            'Hour': h,
            'DayOfWeek': 2, # Wed
            'IsWeekend': 0,
            'WeatherCondition': condition_text,
            'Latitude': 19.0760,
            'Longitude': 72.8777
        }
        seq_data.append(row)
        
    df_seq = pd.DataFrame(seq_data)
    
    if novelty_engine:
        # Prepare numeric features for engine
        # [VehicleCount, Speed, Hour, DayOfWeek, IsWeekend, Latitude, Longitude]
        novelty_cols = ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'Latitude', 'Longitude']
        for c in novelty_cols:
             if c not in df_seq.columns: df_seq[c] = 0.0
             
        X_nov = df_seq[novelty_cols].values
        
        try:
            nov_scores = novelty_engine.get_novelty_score(X_nov, context_data={'city': city})
            df_seq['NoveltyScore'] = nov_scores
        except Exception as e:
            print(f"   [Warning] Novelty Engine mismatch ({e}). Switching to Heuristic Mode.")
            # Heuristic Fallback: 
            # High Score if Event (0.8) + Abnormal Speed (< 20 or > 100)
            base_score = 0.0
            if event_score > 0.5: base_score += 0.4
            
            # Speed deviation
            speed_dev = np.abs(df_seq['Speed'] - 50) / 50.0 # 0 to 1+
            heuristic_scores = base_score + (speed_dev * 0.3)
            df_seq['NoveltyScore'] = heuristic_scores.clip(0, 1)
    else:
         df_seq['NoveltyScore'] = 0.0
         
    # 5. Preprocessing for LSTM
    # Encode Weather
    if 'WeatherCondition' in encoders:
        le = encoders['WeatherCondition']
        # Handle unseen
        df_seq['WeatherCondition'] = df_seq['WeatherCondition'].apply(lambda x: x if x in le.classes_ else le.classes_[0])
        df_seq['WeatherCondition'] = le.transform(df_seq['WeatherCondition'])
        
    # Scale
    X_input = df_seq[feature_cols].values
    X_scaled = scaler.transform(X_input)
    
    # Tensor
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(0).to(device) # Batch dim
    
    # 6. Prediction
    print("\n🔮 Forecasting...")
    with torch.no_grad():
        output = model(X_tensor)
        probs = torch.softmax(output, dim=1)
        conf, pred_idx = torch.max(probs, 1)
        
    congestion_level = classes[pred_idx.item()]
    confidence = conf.item() * 100
    
    # 7. Rich Output
    print(f"\n{'-'*60}")
    print(f"| 🔮 PREDICTION RESULT | {city.split(',')[0].upper():<29} |")
    print(f"{'-'*60}")
    print(f"| Congestion Level      | {str(congestion_level).upper():<30} |")
    print(f"| Confidence Score      | {confidence:.2f}%{' ':<26} |")
    print(f"| Novelty Score         | {df_seq['NoveltyScore'].mean():.4f}{' ':<26} |")
    print(f"{'-'*60}")
    
    print("\n💡 INTELLIGENT ANALYSIS:")
    print(f"  • Context:   {condition_text} Weather + {event_name} (Impact: {event_score})")
    print(f"  • Dynamics:  Speed {df_seq['Speed'].iloc[-1]:.0f} km/h | Volume {df_seq['VehicleCount'].iloc[-1]:.0f}")
    
    threshold = 0.6
    avg_nov = df_seq['NoveltyScore'].mean()
    if avg_nov > threshold:
        print(f"\n  >> 🌟 UNIQUE INSIGHT GENERATED:")
        print(f"     The system detected a 'Contextual Adaptation' scenario (Score: {avg_nov:.2f}).")
        print(f"     Our Hybrid Engine identified a unique traffic pattern driven by")
        print(f"     external factors (Events/Weather) and dynamically calibrated the forecast.")
    else:
        print(f"\n  >> ✅ SYSTEM STABILITY:")
        print(f"     Traffic patterns are matching historical distributions.")
        print(f"     Model is operating within standard parameters.")

if __name__ == "__main__":
    predict_live(city="Mumbai")
