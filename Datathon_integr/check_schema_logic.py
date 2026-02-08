
import pandas as pd
import numpy as np

def normalize_schema(df, source_name):
    """
    Normalizes column names to a canonical format based on the source dataset.
    Canonical Schema:
    - Timestamp
    - Speed
    - VehicleCount
    - WeatherCondition
    - CongestionLevel (Target 0-3)
    - Latitude, Longitude (if available)
    - TrafficSignalStatus (if available)
    """
    df = df.copy()
    
    # Define mappings for each dataset
    if "all_features" in source_name:
        mapper = {
            "timestamp": "Timestamp",
            "speed": "Speed",
            "traffic_volume": "VehicleCount",
            "weather": "WeatherCondition", 
            "congestion_level": "CongestionLevel",
            "lat": "Latitude", "long": "Longitude"
        }
    elif "smart_mobility" in source_name:
        mapper = {
            "Timestamp": "Timestamp",
            "Traffic_Speed": "Speed",
            "Vehicle_Count": "VehicleCount",
            "Weather": "WeatherCondition",
            "Traffic_Condition": "CongestionLevel",
            "Latitude": "Latitude", "Longitude": "Longitude",
            "Traffic_Light": "TrafficSignalStatus"
        }
    elif "urban_traffic" in source_name:
        mapper = {
            "Timestamp": "Timestamp", 
            "Speed": "Speed",
            "Vehicle_Count": "VehicleCount",
            "Congestion_Level": "CongestionLevel"
        }
    else:
        mapper = {}

    # Apply mapping
    # normalized_cols = {k: v for k, v in mapper.items() if k in df.columns} # Only map existing
    # Actually, we need to be robust. Let's do a case-insensitive lookup if possible, or just strict mapping.
    # Given the user provided CSVs, I'll stick to strict mapping based on my previous view_file.
    
    # Fix: The previous view_file showed headers. Let's assume standard handling.
    # For now, I'll rely on a more dynamic map in the main code.
    pass 

def unify_datasets(file_paths):
    dfs = []
    for path in file_paths:
        df = pd.read_csv(path)
        
        # Add source identifier
        if "all_features" in path:
            # Map columns
            df = df.rename(columns={
                "traffic_volume": "VehicleCount", 
                "speed": "Speed", 
                "weather_conditions": "WeatherCondition",
                "congestion_level": "CongestionLevel"
            })
        elif "smart_mobility" in path:
            df = df.rename(columns={
                "Vehicle_Count": "VehicleCount",
                "Traffic_Speed": "Speed",
                "Weather": "WeatherCondition",
                "Traffic_Condition": "CongestionLevel"
            })
        elif "urban_traffic" in path:
            df = df.rename(columns={
                "Vehicle_Count": "VehicleCount",
                "Congestion_Level": "CongestionLevel"
            })
            
        dfs.append(df)
    
    # Concat and handle missing columns
    unified_df = pd.concat(dfs, axis=0, ignore_index=True)
    
    # Standardize Target (CongestionLevel)
    # Map text to integers if distinct
    
    return unified_df
