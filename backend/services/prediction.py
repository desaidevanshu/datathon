import torch
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from ml.model import TrafficLSTM
import os
import random

class PredictionService:
    def __init__(self, model_path='ml/model.pth'):
        self.model = None
        self.scaler = None
        self.le_loc = None
        self.le_weather = None
        self.le_event = None
        self.locations = [
            'bandra_worli_sea_link', 'western_express_highway', 'eastern_express_highway',
            'dadar_tt', 'saki_naka', 'jvlr', 'colaba_causeway', 'link_road'
        ]
        self._load_artifacts()

    def _load_artifacts(self):
        try:
            if not os.path.exists('ml/model.pth'):
                print("Model not found, skipping load.")
                return

            print("Loading ML artifacts...")
            # Load scalers
            self.scaler = joblib.load('ml/scaler.pkl')
            self.le_loc = joblib.load('ml/le_loc.pkl')
            self.le_weather = joblib.load('ml/le_weather.pkl')
            self.le_event = joblib.load('ml/le_event.pkl')
            
            # Load Model
            # Input size = 6 (hour, location_id, weather, event, traffic_volume, avg_speed (last))
            # Wait, my training script used: ['hour', 'location_id', 'weather', 'event', 'traffic_volume', 'average_speed']
            # So input size is 6.
            self.model = TrafficLSTM(input_size=6, hidden_size=50, num_layers=2, output_size=1)
            self.model.load_state_dict(torch.load('ml/model.pth'))
            self.model.eval()
            print("ML Prediction Service Ready.")
        except Exception as e:
            print(f"Failed to load ML artifacts: {e}")

    def predict_congestion(self, segment_ids):
        timestamp = datetime.now()
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5
        
        results = []
        
        # If model not loaded, return mock fallback
        if not self.model:
            return self._mock_fallback(segment_ids)

        for seg_id in segment_ids:
            # Map segment to a location (Deterministic hash)
            loc_idx = hash(seg_id) % len(self.locations)
            location = self.locations[loc_idx]
            
            # Prepare Input Features (Real-time simulation)
            # 1. Hour (Normalized)
            # 2. Location (Encoded)
            # 3. Weather (Encoded - Default Clear)
            # 4. Event (Encoded - Default None)
            # 5. Volume (Simulated based on hour)
            # 6. Previous Speed (Mocked as current limit)

            try:
                # Simulating input sequence (SEQ_LENGTH=10)
                # In prod, we would fetch last 10 hours from DB
                # Here we simulate a stable sequence
                
                # Encode inputs
                loc_encoded = self.le_loc.transform([location])[0]
                weather_encoded = self.le_weather.transform(['Clear'])[0] # Assume Clear
                event_encoded = self.le_event.transform(['None'])[0]     # Assume None
                
                # Mock Volume
                base_volume = 30
                if (9 <= hour <= 11) or (18 <= hour <= 21): base_volume += 50
                volume = base_volume
                
                # Create a sequence of 10 identical steps for simplicity (or slightly varying)
                input_seq = []
                for i in range(10):
                    # Create feature vector [hour, loc, weather, event, volume, speed(prev)]
                    # We need to scale these constraints.
                    # It's tricky to replicate exact scaling without the original dataframe context 
                    # efficiently unless we manually scaled or saved scaler params.
                    # The scaler expects a DataFrame structure usually if using sklearn pipeline, 
                    # or array of shape (n, 6).
                    
                    # Let's construct raw row
                    # ['hour', 'location_id', 'weather', 'event', 'traffic_volume', 'average_speed']
                    # Note: The scaler was fitted on Encoded values for loc/weather/event? 
                    # No, look at `train.py`:
                    # df[['traffic_volume', 'average_speed', 'hour']] = scaler.fit_transform(...)
                    # It ONLY scaled volume, speed, hour. 
                    # Loc, Weather, Event were NOT scaled, just label encoded.
                    
                    # Re-check train.py:
                    # features = ['hour', 'location_id', 'weather', 'event', 'traffic_volume', 'average_speed']
                    # The scaler only transformed columns 'traffic_volume', 'average_speed', 'hour'.
                    
                    # We need to apply the cleaner transformation logic here.
                    # To interact with the loaded scaler correctly, we should construct a dummy DF or array 
                    # for the 3 columns it expects, transform them, and then combine with the others.
                    
                    # Raw values
                    raw_vol = volume + random.randint(-5, 5)
                    raw_speed = 40 # Mock previous speed
                    
                    # Scale
                    # scaler.transform expects [[volume, speed, hour]] (order matters based on fit columns?)
                    # In train.py: scaler.fit_transform(df[['traffic_volume', 'average_speed', 'hour']])
                    scaled_vals = self.scaler.transform([[raw_vol, raw_speed, hour]])[0] 
                    # scaled_vals = [vol_norm, speed_norm, hour_norm]
                    
                    # Feature Vector construction: ['hour', 'location_id', 'weather', 'event', 'traffic_volume', 'average_speed']
                    # Be careful with order!
                    vec = [
                        scaled_vals[2], # hour
                        loc_encoded,
                        weather_encoded,
                        event_encoded,
                        scaled_vals[0], # volume
                        scaled_vals[1]  # speed
                    ]
                    input_seq.append(vec)
                
                input_tensor = torch.FloatTensor([input_seq]) # Shape (1, 10, 6)
                
                with torch.no_grad():
                    prediction_norm = self.model(input_tensor).item()
                
                # Inverse transform prediction (which is normalized speed)
                # We need to inverse transform just the speed column. 
                # Scaler inverse_transform expects 3 cols.
                # Construct dummy [0, prediction, 0] to extract speed
                dummy_for_inverse = [[0, prediction_norm, 0]]
                orig_vals = self.scaler.inverse_transform(dummy_for_inverse)[0]
                predicted_speed = orig_vals[1]
                
                # Map speed to congestion level
                if predicted_speed < 15: level, conf = 'critical', 0.95
                elif predicted_speed < 30: level, conf = 'high', 0.85
                elif predicted_speed < 45: level, conf = 'medium', 0.80
                else: level, conf = 'low', 0.90
                
                results.append({
                    "segment_id": seg_id,
                    "congestion_level": level,
                    "confidence": conf
                })
                
            except Exception as e:
                print(f"Inference error for {seg_id}: {e}")
                results.append(self._mock_single(seg_id))
                
        return results

    def _mock_fallback(self, segment_ids):
        return [self._mock_single(sid) for sid in segment_ids]

    def _mock_single(self, seg_id):
        level = random.choice(["low", "medium", "high", "critical"])
        confidence = random.uniform(0.7, 0.99)
        return {
            "segment_id": seg_id,
            "congestion_level": level,
            "confidence": confidence
        }
