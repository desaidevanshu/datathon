
import pandas as pd
import torch
import joblib
import os
import sys
import numpy as np

# Ensure src is in path (though running from root usually works)
# We append current directory explicitly just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.train_lstm import AdvancedTrafficLSTM
from src.novelty_engine import HybridNoveltyEngine

def run_batch_inference(csv_path):
    print(f"Loading dataset: {csv_path}")
    if not os.path.exists(csv_path):
        print("Error: Dataset not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Basic Preprocessing (similar to data_loader)
    # Ensure standard columns (VehicleCount, Speed, etc.)
    # The dataset might use different names, so let's try to map them if needed
    # Start with simple normalization based on standard names
    rename_map = {
        'traffic_volume': 'VehicleCount',
        'avg_speed': 'Speed',
        'hour': 'Hour',
        'day_of_week': 'DayOfWeek',
        'is_weekend': 'IsWeekend',
        'weather_condition': 'WeatherCondition',
        'congestion_index': 'CongestionIndex'
    }
    df = df.rename(columns=rename_map)
    
    # Load Artifacts
    if not os.path.exists("lstm_artifacts.pkl"):
        print("Error: listm_artifacts.pkl not found.")
        return
        
    artifacts = joblib.load("lstm_artifacts.pkl")
    scaler = artifacts['scaler']
    encoders = artifacts['encoders']
    feature_cols = artifacts['feature_cols']
    classes = artifacts['classes']
    
    print(f"Loaded artifacts. Feature columns: {feature_cols}")
    
    # Load Novelty Engine
    novelty_engine = None
    if os.path.exists("novelty_engine.pkl"):
        novelty_engine = joblib.load("novelty_engine.pkl")
        print("Loaded Novelty Engine.")
    else:
        print("Warning: Novelty Engine not found. Using default scores.")

    # Prepare Data for Inference
    # 1. Fill Missing
    for col in feature_cols:
        if col not in df.columns:
            if col == 'NoveltyScore': df[col] = 0.0
            else: df[col] = 0
            
    # 2. Novelty Score
    if novelty_engine:
        # Features expected by novelty engine might differ slightly, but usually are subset of numericals
        # Let's assume it used the same cols as train_lstm.py for now or try to match
        # In train_lstm.py: ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'origin', 'destination']
        nov_cols = [c for c in ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'origin', 'destination'] if c in df.columns]
        
        # Encoders for origin/dest might be needed for novelty engine too?
        # Actually train_lstm.py encodes them BEFORE partial fit.
        # We need to encode origin/dest first.
        
        if 'origin' in encoders and 'origin' in df.columns:
             # Handle unseen labels by mapping to a default or skipping
             # Using map with fillna
             known_classes = set(encoders['origin'].classes_)
             df['origin'] = df['origin'].apply(lambda x: x if x in known_classes else list(known_classes)[0])
             df['origin'] = encoders['origin'].transform(df['origin'])
             
        if 'destination' in encoders and 'destination' in df.columns:
             known_classes = set(encoders['destination'].classes_)
             df['destination'] = df['destination'].apply(lambda x: x if x in known_classes else list(known_classes)[0])
             df['destination'] = encoders['destination'].transform(df['destination'])

        try:
            X_nov = df[nov_cols].values
            df['NoveltyScore'] = novelty_engine.get_novelty_score(X_nov)
        except Exception as e:
            print(f"Novelty Engine Error: {e}")
            df['NoveltyScore'] = 0.0

    # 3. Encode Categorical (Weather)
    if 'WeatherCondition' in encoders and 'WeatherCondition' in df.columns:
        le = encoders['WeatherCondition']
        known_classes = set(le.classes_)
        df['WeatherCondition'] = df['WeatherCondition'].astype(str).apply(lambda x: x if x in known_classes else list(known_classes)[0])
        df['WeatherCondition'] = le.transform(df['WeatherCondition'])
        
    # Scale Features
    X_input = df[feature_cols].values
    X_scaled = scaler.transform(X_input)
    
    # Create Sequences
    sequence_length = 5
    X_seq = []
    # We'll just take the first N sequences to demonstrate (or all if feasible)
    # Using sliding window
    num_sequences = len(df) - sequence_length
    print(f"Generating {num_sequences} sequences...")
    
    if num_sequences <= 0:
        print("Not enough data for sequences.")
        return

    # For efficiency in this script, let's just do a batch of 1000 or so
    limit = 1000
    indices = range(min(num_sequences, limit))
    
    for i in indices:
        seq = X_scaled[i : i + sequence_length]
        X_seq.append(seq)
        
    X_batch = torch.tensor(np.array(X_seq), dtype=torch.float32)
    
    # Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = len(feature_cols)
    num_classes = len(classes)
    model = AdvancedTrafficLSTM(input_size, 128, num_classes).to(device)
    
    if os.path.exists("traffic_lstm_model.pth"):
        model.load_state_dict(torch.load("traffic_lstm_model.pth", map_location=device))
        model.eval()
        print("Model loaded successfully.")
    else:
        print("Error: traffic_lstm_model.pth not found.")
        return
        
    # Inference
    print("Running Inference...")
    with torch.no_grad():
        X_batch = X_batch.to(device)
        outputs = model(X_batch)
        probs = torch.softmax(outputs, dim=1)
        confs, preds = torch.max(probs, 1)
        
    print("\nInference Results (First 10):")
    for i in range(10):
        cls = classes[preds[i].item()]
        conf = confs[i].item()
        print(f"Seq {i}: Pred={cls} (Conf: {conf:.2f})")
        
    print(f"\nBatch Inference Completed on {len(X_batch)} sequences.")

if __name__ == "__main__":
    csv_file = r"C:\Users\USER\Desktop\Datathon_integr\mumbai_multi_route_traffic_dataset_FINAL_1LAKH.csv"
    run_batch_inference(csv_file)
