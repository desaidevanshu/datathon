import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Mumbai Locations
LOCATIONS = [
    'bandra_worli_sea_link', 'western_express_highway', 'eastern_express_highway',
    'dadar_tt', 'saki_naka', 'jvlr', 'colaba_causeway', 'link_road'
]

# Multivariate Features
WEATHER_CONDITIONS = ['Clear', 'Rainy', 'Cloudy', 'Foggy']
EVENTS = ['None', 'Cricket Match', 'Festival', 'VIP Movement', 'Accident']

def generate_traffic_data(days=30):
    print(f"Generating synthetic traffic data for {days} days...")
    
    start_date = datetime.now() - timedelta(days=days)
    data = []
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        for hour in range(24):
            # Base congestion pattern (Peak hours: 9-11 AM, 6-9 PM)
            is_peak = (9 <= hour <= 11) or (18 <= hour <= 21)
            
            for loc in LOCATIONS:
                # Random Factors
                weather = random.choice(WEATHER_CONDITIONS)
                event = random.choices(EVENTS, weights=[0.8, 0.05, 0.05, 0.05, 0.05])[0]
                
                # Base modifiers
                weather_factor = 1.0
                if weather == 'Rainy': weather_factor = 1.3
                if weather == 'Foggy': weather_factor = 1.1
                
                event_factor = 1.0
                if event != 'None': event_factor = 1.5
                if event == 'Accident': event_factor = 2.0
                
                # Calculate Traffic Volume (Cars/min) & Speed
                base_volume = random.randint(20, 50)
                if is_peak: base_volume += random.randint(40, 80)
                if is_weekend: base_volume *= 0.7
                
                final_volume = base_volume * weather_factor * event_factor
                
                # Inverse relationship between volume and speed
                # Max speed 60 km/h (city), Min speed 5 km/h
                predicted_speed = max(5, 60 - (final_volume * 0.4))
                
                # Add noise
                predicted_speed += np.random.normal(0, 3) 
                predicted_speed = max(5, min(80, predicted_speed))

                # Congestion Level Labeling
                if predicted_speed < 15: congestion = 'Critical'
                elif predicted_speed < 30: congestion = 'High'
                elif predicted_speed < 45: congestion = 'Medium'
                else: congestion = 'Low'

                data.append({
                    'timestamp': current_date.replace(hour=hour, minute=0, second=0),
                    'location_id': loc,
                    'hour': hour,
                    'is_weekend': is_weekend,
                    'weather': weather,
                    'event': event,
                    'traffic_volume': int(final_volume),
                    'average_speed': round(predicted_speed, 2),
                    'congestion_level': congestion
                })
    
    df = pd.DataFrame(data)
    df.to_csv('traffic_data_mumbai.csv', index=False)
    print(f"Data generation complete! Saved {len(df)} records to traffic_data_mumbai.csv")
    return df

if __name__ == "__main__":
    generate_traffic_data()
