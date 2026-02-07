import pandas as pd
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data_loader import load_traffic_data
from data_preprocessing_seq import create_sequences

csv_path = r"c:/Users/Devanshu/OneDrive/Documents/datathon/all_features_traffic_dataset.csv"

print(f"Checking {csv_path}...")
if not os.path.exists(csv_path):
    print("File not found!")
    sys.exit(1)

df = load_traffic_data(csv_path)
print("Columns:", df.columns)
if 'CongestionLevel' in df.columns:
    print("Unique CongestionLevel:", df['CongestionLevel'].unique())
    print("Value Counts:\n", df['CongestionLevel'].value_counts())
else:
    print("CongestionLevel column missing!")

print("\nRunning create_sequences...")
try:
    X, y, classes, scaler, encoders, feature_cols = create_sequences(df, 'CongestionLevel', sequence_length=5)
    print("Classes found:", classes)
    print("Num classes:", len(classes))
except Exception as e:
    print("create_sequences failed:", e)
