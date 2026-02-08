
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_city_data(city_name, lat, lon, num_days=30):
    print(f"Generating data for {city_name}...")
    
    start_date = datetime.now() - timedelta(days=num_days)
    data = []
    
    # Traffic Patterns
    # Peak hours: 8-11am, 5-8pm
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        for hour in range(24):
            # Base Factors
            is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)
            
            # Random Weather
            weather = np.random.choice(['Clear', 'Rain', 'Cloudy', 'Storm'], p=[0.6, 0.1, 0.25, 0.05])
            
            # Random Event (Rare)
            event_impact = 0.0
            event_name = "None"
            if random.random() < 0.05: # 5% chance of event
                event_name = np.random.choice(['Match', 'Protest', 'Festival', 'Accident'])
                event_impact = np.random.choice([0.5, 0.8, 1.0]) # Medium, High, Severe
                
            # Traffic generation logic for "Damn Accurate" patterns
            base_vol = 500 # Night
            if is_peak: base_vol = 2500
            elif 11 < hour < 17: base_vol = 1500 # Mid-day
            
            # Adjusters
            if is_weekend: base_vol *= 0.6 # Less traffic
            
            # Event Impact
            if event_impact > 0:
                base_vol *= (1 + event_impact) # Traffic increases? Or depends.
                # Actually, for congestion, volume might be high OR speed low.
                
            # Speed Logic
            # Higher volume = Lower Speed
            # Free flow speed ~ 60-80 km/h
            congestion_factor = base_vol / 4000.0 # Normalized-ish
            speed = 60 * (1 - congestion_factor) 
            speed += np.random.normal(0, 5) # Noise
            
            # Weather Impact on Speed
            if weather == 'Rain': speed *= 0.8
            if weather == 'Storm': speed *= 0.6
                
            # Congestion Level Target
            # 0: Low (>45 km/h), 1: Medium (25-45 km/h), 2: High (<25 km/h)
            if speed > 45: congestion = 0
            elif speed > 25: congestion = 1
            else: congestion = 2
            
            # Clip
            speed = max(5, min(100, speed))
            base_vol = max(0, int(base_vol + np.random.normal(0, 200)))
            
            row = {
                'City': city_name,
                'Latitude': lat,
                'Longitude': lon,
                'Timestamp': current_date.replace(hour=hour, minute=0, second=0),
                'VehicleCount': base_vol,
                'Speed': round(speed, 2),
                'WeatherCondition': weather,
                'EventName': event_name,
                'EventImpact': event_impact,
                'Hour': hour,
                'DayOfWeek': current_date.weekday(),
                'IsWeekend': 1 if is_weekend else 0,
                'CongestionLevel': congestion
            }
            data.append(row)
            
    return data

def generate_big_dataset():
    # Cities (State-wise representation)
    cities = [
        ("Mumbai", 19.0760, 72.8777),
        ("Delhi", 28.7041, 77.1025),
        ("Bangalore", 12.9716, 77.5946),
        ("Chennai", 13.0827, 80.2707),
        ("Kolkata", 22.5726, 88.3639)
    ]
    
    all_data = []
    for city, lat, lon in cities:
        # Generate 60 days of data per city
        city_data = generate_city_data(city, lat, lon, num_days=60) 
        all_data.extend(city_data)
        
    df = pd.DataFrame(all_data)
    print(f"Generated {len(df)} rows of synthetic state-wise data.")
    
    output_path = "state_wise_traffic_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    generate_big_dataset()
