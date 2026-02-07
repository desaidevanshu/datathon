import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from model import TrafficLSTM
import joblib

# Constants
SEQ_LENGTH = 10  # Number of past hours to look back
HIDDEN_SIZE = 50
NUM_LAYERS = 2
EPOCHS = 50
LEARNING_RATE = 0.001

def train_model():
    print("Loading data...")
    df = pd.read_csv('traffic_data_mumbai.csv')
    
    # Preprocessing
    # Encode Categorical Variables
    le_loc = LabelEncoder()
    df['location_id'] = le_loc.fit_transform(df['location_id'])
    
    le_weather = LabelEncoder()
    df['weather'] = le_weather.fit_transform(df['weather'])
    
    le_event = LabelEncoder()
    df['event'] = le_event.fit_transform(df['event'])
    
    # Normalize Numerical Features
    scaler = MinMaxScaler()
    df[['traffic_volume', 'average_speed', 'hour']] = scaler.fit_transform(df[['traffic_volume', 'average_speed', 'hour']])
    
    # Target: We want to predict average_speed (which determines congestion)
    # Features: hour, location_id, weather, event, traffic_volume
    # For simplicity in this demo, we will treat it as a regression problem predicting 'average_speed'
    
    # Create Sequences
    features = ['hour', 'location_id', 'weather', 'event', 'traffic_volume', 'average_speed']
    data_matrix = df[features].values
    
    X, y = [], []
    for i in range(len(data_matrix) - SEQ_LENGTH):
        X.append(data_matrix[i:i+SEQ_LENGTH])
        y.append(data_matrix[i+SEQ_LENGTH][5]) # Predicting average_speed
        
    X = np.array(X)
    y = np.array(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Convert to Tensors
    X_train = torch.FloatTensor(X_train)
    y_train = torch.FloatTensor(y_train).view(-1, 1)
    X_test = torch.FloatTensor(X_test)
    y_test = torch.FloatTensor(y_test).view(-1, 1)
    
    # Model Setup
    input_size = len(features)
    model = TrafficLSTM(input_size, HIDDEN_SIZE, NUM_LAYERS, output_size=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print("Starting training...")
    for epoch in range(EPOCHS):
        model.train()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{EPOCHS}], Loss: {loss.item():.4f}')
            
    print("Training complete!")
    
    # Save Artifacts
    torch.save(model.state_dict(), 'model.pth')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(le_loc, 'le_loc.pkl')
    joblib.dump(le_weather, 'le_weather.pkl')
    joblib.dump(le_event, 'le_event.pkl')
    print("Model and scalers saved.")

if __name__ == "__main__":
    train_model()
