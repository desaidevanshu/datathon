import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
import joblib
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.data_loader import load_traffic_data
from src.data_preprocessing_seq import create_sequences
from src.novelty_engine import HybridNoveltyEngine

class AdvancedTrafficLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, num_layers=2):
        super(AdvancedTrafficLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Bidirectional LSTM for better context
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                            batch_first=True, dropout=0.3, bidirectional=True)
        
        # FC Layer (Features * 2 for bidirectional)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        # x: (batch, seq_len, features)
        # LSTM output: (batch, seq_len, num_directions * hidden_size)
        out, _ = self.lstm(x)
        
        # Use only the last time step features
        out = out[:, -1, :] 
        out = self.fc(out)
        return out

def train_lstm_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 1. Load Unified Data
    # 1. Load Unified Data
    # prioritizing the generated big data (Multi-Route)
    base_dir = r"c:/Users/Devanshu/OneDrive/Documents/datathon"
    # UPDATED: Use the 1 Lakh Final Dataset
    big_data_path = os.path.join(base_dir, "mumbai_multi_route_traffic_dataset_FINAL_1LAKH.csv")
    
    files = []
    if os.path.exists(big_data_path):
        print(f"Using Mumbai Multi-Route Dataset (1 Lakh): {big_data_path}")
        files.append(big_data_path)
    else:
        print("Warning: Multi-Route data not found. Falling back to synthetic.")
        files.append(os.path.join(base_dir, "state_wise_traffic_data.csv"))

    print("Loading unified datasets...")
    try:
        # data_loader now returns (df, encoders)
        df, encoders = load_traffic_data(files)
        print(f"Loaded Encoders for: {list(encoders.keys())}")
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # 2. Train & Apply Novelty Engine (Route-Aware)
    print("Training Hybrid Novelty Engine on new data...")
    try:
        # Prepare numerical features for engine
        # Now including encoded Origin/Dest for Route-Specific Novelty
        # Feature names must match the NORMALIZED names from data_loader.py
        req_cols = ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'origin', 'destination']
        
        # Ensure cols exist (Normalize names if needed)
        
        # Check if Timestamp exists (it should as returned by loader)
        if 'Timestamp' in df.columns:
            # Timestamp conversion handled by data_loader
            pass 
        
        for c in req_cols:
            if c not in df.columns: df[c] = 0
            
        X_novelty = df[req_cols].fillna(0).values
        
        # Initialize and Train
        # Higher contamination for massive synthetic data with events
        novelty_engine = HybridNoveltyEngine(contamination=0.05) 
        novelty_engine.fit(X_novelty)
        
        # Save it immediately
        joblib.dump(novelty_engine, "novelty_engine.pkl")
        print("Novelty Engine retrained and saved.")
        
        # Score
        df['NoveltyScore'] = novelty_engine.get_novelty_score(X_novelty)
        
    except Exception as e:
        print(f"Error training novelty engine: {e}")
        df['NoveltyScore'] = 0.0

    # 3. Create Sequences
    print("Creating multivariate sequences...")
    # Clean target
    df = df.dropna(subset=['CongestionLevel'])
    
    X, y, classes, scaler, encoders, feature_cols = create_sequences(df, 'CongestionLevel', sequence_length=5)
    
    print(f"Input Shape: {X.shape}")
    print(f"Features: {feature_cols}")
    
    # Save Scaler/Encoders for Prediction
    joblib.dump({'scaler': scaler, 'encoders': encoders, 'feature_cols': feature_cols, 'classes': classes}, 
                "lstm_artifacts.pkl")
    
    # Convert to Tensor
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
    y_tensor = torch.tensor(y, dtype=torch.long).to(device)
    
    # Train/Test Split
    split = int(0.8 * len(X))
    X_train, X_test = X_tensor[:split], X_tensor[split:]
    y_train, y_test = y_tensor[:split], y_tensor[split:]
    
    train_ds = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    
    # 4. Initialize Model
    model = AdvancedTrafficLSTM(input_size=X.shape[2], hidden_size=128, num_classes=len(classes)).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 5. Training Loop
    epochs = 15
    print("\nStarting Training...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for bx, by in train_loader:
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, pred = torch.max(out, 1)
            correct += (pred == by).sum().item()
            total += by.size(0)
            
        acc = correct / total
        if (epoch+1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(train_loader):.4f} | Acc: {acc:.4f}")

    # 6. Evaluation
    model.eval()
    with torch.no_grad():
        out = model(X_test)
        _, preds = torch.max(out, 1)
        test_acc = (preds == y_test).float().mean()
        
    print(f"\nTest Accuracy: {test_acc:.4f}")
    
    # Save Model
    torch.save(model.state_dict(), "traffic_lstm_model.pth")
    print("Model saved to traffic_lstm_model.pth")

if __name__ == "__main__":
    train_lstm_model()
