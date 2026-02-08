
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from data_loader import load_traffic_data
import pandas as pd

def test_loading():
    base_dir = r"c:/Users/Devanshu/OneDrive/Documents/datathon"
    files = [
        os.path.join(base_dir, "all_features_traffic_dataset.csv"),
        os.path.join(base_dir, "smart_mobility_dataset.csv"),
        os.path.join(base_dir, "urban_traffic_flow_with_target.csv")
    ]
    
    print("Testing load_traffic_data with list of files...")
    try:
        df = load_traffic_data(files)
        print("Success!")
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df[['DatasetSource', 'VehicleCount', 'Speed', 'CongestionLevel']].head())
        print("\nCongestionLevel Distribution:")
        print(df['CongestionLevel'].value_counts())
        
        # Check for NaNs in critical columns
        print(f"\nNaNs in VehicleCount: {df['VehicleCount'].isna().sum()}")
        print(f"NaNs in Speed: {df['Speed'].isna().sum()}")
        
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_loading()
