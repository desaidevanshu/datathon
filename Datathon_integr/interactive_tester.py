
import pandas as pd
import torch
import joblib
import os
import sys
import numpy as np
import time

# Suppress sklearn warnings for cleaner output
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

# Ensure src in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.train_lstm import AdvancedTrafficLSTM
from src.scraper import get_live_weather, get_city_events, get_event_impact_score
from src.sensor_interface import TrafficSensorNetwork, GPSDataStream
from src.bottleneck_detector import predict_future_bottlenecks, detect_bottleneck_formation
from src.station_locator import get_coords_for_location, get_stations_along_route
from src.smart_recommendations import get_route_viability, suggest_smart_break, optimize_departure_time
from src.what_if_simulator import run_what_if_scenario
from src.community_intel import get_reports_for_location, submit_report, flag_report

def load_resources():
    print("Loading resources...")
    if not os.path.exists("lstm_artifacts.pkl"):
        print("Error: Artifacts not found.")
        return None, None, None, None, None, None

    artifacts = joblib.load("lstm_artifacts.pkl")
    
    # Load dataset for valid routes
    csv_path = "mumbai_multi_route_traffic_dataset_FINAL_1LAKH.csv"
    if os.path.exists(csv_path):
        try:
             df = pd.read_csv(csv_path)
             valid_origins = sorted(df['origin'].unique().astype(str))
             valid_dests = sorted(df['destination'].unique().astype(str))
        except:
             valid_origins = []
             valid_dests = []
    else:
        valid_origins = []
        valid_dests = []

    # Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = len(artifacts['feature_cols'])
    num_classes = len(artifacts['classes'])
    model = AdvancedTrafficLSTM(input_size, 128, num_classes).to(device)
    
    if os.path.exists("traffic_lstm_model.pth"):
        model.load_state_dict(torch.load("traffic_lstm_model.pth", map_location=device))
        model.eval()
    else:
        print("Error: traffic_lstm_model.pth not found.")
        return None, None, None, None, None, None

    # Load Novelty Engine
    novelty_engine = None
    if os.path.exists("novelty_engine.pkl"):
        novelty_engine = joblib.load("novelty_engine.pkl")

    return artifacts, model, novelty_engine, valid_origins, valid_dests, device

def get_input(prompt, options=None, cast_func=str):
    while True:
        try:
            val = input(f"{prompt}: ").strip()
        except EOFError:
            return None
            
        if not val and options:
             print(f"Suggestions: {options[:5]}...")
             continue
        
        if options:
            match = next((opt for opt in options if opt.lower() == val.lower()), None)
            if match:
                return match
            else:
                 print(f"Invalid option. Suggestions: {options[:5]}...")
                 continue

        try:
            return cast_func(val)
        except:
             print("Invalid format.")

def main():
    artifacts, model, novelty_engine, valid_origins, valid_dests, device = load_resources()
    if not artifacts: return
    
    scaler = artifacts['scaler']
    encoders = artifacts['encoders']
    feature_cols = artifacts['feature_cols']
    classes = artifacts['classes']

    print("\n--- Intelligent Traffic Forecaster (Interactive) ---")
    print("System Online. Connected to Live Weather & Events API.")
    
    while True:
        try:
            print("\n=== New Trip Query ===")
            city = "Mumbai" # Default
            
            # 1. User Input: Route
            origin = get_input("Enter Origin", valid_origins)
            if origin is None: break
            
            dest = get_input("Enter Destination", valid_dests)
            
            # Community Intelligence: Show recent reports
            route_key = f"{origin}-{dest}"
            reports = get_reports_for_location(route_key, hours_back=2)
            
            if reports:
                print(f"\n>>> COMMUNITY REPORTS ({len(reports)}) <<<")
                for i, r in enumerate(reports[:5], 1):  # Show top 5
                    verified_mark = "[V] " if r['verified'] else ""
                    flag_mark = f" [⚠ {r['flags']} flags]" if r['flags'] > 0 else ""
                    print(f"{i}. {verified_mark}{r['report']}{flag_mark}")
                    print(f"   (reported {r['ago']}, severity: {r['severity']})")
            else:
                print(f"\n>>> COMMUNITY REPORTS <<<")
                print("No recent reports for this route.")

            
            # 2. Nearby Stations (Fuel & EV Chargers)
            print("\n[SYSTEM] Locating Nearby Stations...")
            origin_coords = get_coords_for_location(origin, city)
            dest_coords = get_coords_for_location(dest, city)
            
            if origin_coords and dest_coords:
                stations = get_stations_along_route(origin_coords, dest_coords, radius_km=2.0)
                
                print(f"\n>>> NEARBY STATIONS <<<")
                fuel_count = len(stations['fuel_stations'])
                ev_count = len(stations['ev_chargers'])
                
                print(f"Fuel Stations: {fuel_count} found")
                for station in stations['fuel_stations'][:3]:  # Top 3
                    print(f"  • {station['name']} ({station['distance']:.1f} km)")
                
                print(f"EV Chargers:   {ev_count} found")
                for charger in stations['ev_chargers'][:3]:
                    print(f"  • {charger['name']} ({charger['distance']:.1f} km)")
                
                if fuel_count == 0 and ev_count == 0:
                    print("  (No stations found within 2 km radius)")
            else:
                print("  ! Location coordinates unavailable, skipping station search.")
            
            # 3. Automated Context Fetching
            print("\n[SYSTEM] Scanning Environment & Sensors...")
            
            # Weather
            weather_data = get_live_weather(city)
            weather_cond = weather_data.get("Condition", "Clear")
            print(f"   > Weather: {weather_cond} ({weather_data.get('Temperature')}C)")
            
            # Events
            event_score = get_event_impact_score(city)
            events = get_city_events(city, context={'source': origin, 'dest': dest})
            event_name = events.get("Details", {}).get("Name", "None")
            print(f"   > Events:  {event_name} (Impact: {event_score})")
            
            # Real-Time Sensors (Simulated)
            sensors = TrafficSensorNetwork(location=f"{city} (Central)")
            gps = GPSDataStream(location=f"{city} (Cluster)")
            
            vol = sensors.get_realtime_volume()
            speed = gps.get_average_speed(vol)
            
            # Apply Event Impact logic for simulation
            if event_score > 0.5:
                vol *= 1.2
                speed *= 0.7
                
            print(f"   > Traffic: {int(vol)} veh/hr | Speed: {speed:.1f} km/h")
            
            # Time
            now = time.localtime()
            hour = now.tm_hour
            day = now.tm_wday
            is_weekend = 1 if day >= 5 else 0

            # 4. Model Inference
            # Prepare Input DataFrame
            row = {
                'VehicleCount': vol,
                'Speed': speed,
                'Hour': hour,
                'DayOfWeek': day,
                'IsWeekend': is_weekend,
                'WeatherCondition': weather_cond,
                'origin': origin,
                'destination': dest,
                'NoveltyScore': 0.0 # Placeholder
            }
            df = pd.DataFrame([row])
            
            # Encode Categorical
            if 'origin' in encoders:
                le = encoders['origin']
                try: df['origin'] = le.transform(df['origin'])
                except: df['origin'] = 0
            
            if 'destination' in encoders:
                le = encoders['destination']
                try: df['destination'] = le.transform(df['destination'])
                except: df['destination'] = 0

            if 'WeatherCondition' in encoders:
                 le = encoders['WeatherCondition']
                 try: df['WeatherCondition'] = le.transform(df['WeatherCondition'])
                 except: df['WeatherCondition'] = 0

            # Calculate Novelty Score
            if novelty_engine:
                 req_nov_cols = [c for c in ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 'IsWeekend', 'origin', 'destination'] if c in df.columns]
                 try:
                     X_nov = df[req_nov_cols].values
                     df['NoveltyScore'] = novelty_engine.get_novelty_score(X_nov)
                 except:
                     df['NoveltyScore'] = 0.0
            
            # Scale
            X_input = df[feature_cols].values
            X_scaled = scaler.transform(X_input)
            
            # Sequence (Steady state assumption)
            X_seq = np.tile(X_scaled, (5, 1)) 
            X_batch = torch.tensor(X_seq, dtype=torch.float32).unsqueeze(0).to(device)
            
            # Predict
            with torch.no_grad():
                output = model(X_batch)
                probs = torch.softmax(output, dim=1)
                conf, pred_idx = torch.max(probs, 1)
                
            pred_class = classes[pred_idx.item()]
            confidence = conf.item() * 100
            mapping = {0: "Low / Free Flow", 1: "Moderate", 2: "High / Congestion"}
            
            print(f"\n>>> FORECAST <<<")
            print(f"Prediction: {mapping.get(int(pred_class), 'Unknown')} (Level {pred_class})")
            print(f"Confidence: {confidence:.1f}%")
            if df['NoveltyScore'].values[0] > 0.6:
                print("Note: Unusual traffic pattern detected (High Novelty).")

            # 5. Future Bottleneck Detection
            print(f"\n>>> BOTTLENECK FORECAST <<<")
            current_state_dict = {
                'VehicleCount': vol,
                'Speed': speed,
                'Hour': hour,
                'DayOfWeek': day,
                'IsWeekend': is_weekend,
                'WeatherCondition': df['WeatherCondition'].values[0],  # Already encoded
                'NoveltyScore': df['NoveltyScore'].values[0],
                'EventImpact': event_score
            }
            
            future_predictions = predict_future_bottlenecks(
                model, current_state_dict, scaler, feature_cols, classes,
                time_horizons=[0.5, 1.0, 2.0], device=device
            )
            
            for pred in future_predictions:
                time_label = f"+{pred['time_ahead']:.1f}h"
                level_str = mapping.get(pred['level'], 'Unknown')
                conf_str = f"{pred['confidence']*100:.0f}%"
                
                # Highlight if congestion increases
                if pred['level'] > int(pred_class):
                    marker = "[!] RISING"
                elif pred['level'] < int(pred_class):
                    marker = "[V] EASING"
                else:
                    marker = "-> STABLE"
                    
                print(f"  {time_label} ({pred['hour']:02d}:00): {level_str} [{conf_str}] {marker}")
            
            # Alert if bottleneck forming
            bottleneck_info = detect_bottleneck_formation(future_predictions)
            if bottleneck_info.get('detected'):
                print(f"\n[!] BOTTLENECK ALERT!")
                print(f"   Congestion will spike in {bottleneck_info['forms_at']}h")
                print(f"   Expected at: {bottleneck_info['hour']:02d}:00")
                print(f"   Severity: Level {bottleneck_info['severity']}")

            # 6. Smart Recommendations (Routing & Timing)
            print(f"\n>>> SMART RECOMMENDATIONS <<<")
            
            # Route Viability Check
            route_alert = get_route_viability(int(pred_class), future_predictions)
            if route_alert:
                print(f"[!] {route_alert}")
            else:
                print("[OK] Route looks clear - No major congestion predicted")
            
            # Smart Break Suggestion
            break_rec = suggest_smart_break(future_predictions)
            if break_rec:
                print(f"[INFO] {break_rec}")
            
            # Optimal Departure Time
            optimal = optimize_departure_time(int(pred_class), future_predictions, hour)
            print(f"[TIME] {optimal}")

            # 7. What-If Scenario Simulation
            what_if_choice = input("\n\nRun What-If Scenario? (y/n): ").strip().lower()
            if what_if_choice == 'y':
                print("\n=== WHAT-IF SIMULATOR ===")
                print("Modify conditions to see impact:\n")
                
                # Get modifications
                print(f"Current Weather: {weather_cond}")
                new_weather = input("Change weather (Clear/Rain/Fog or Enter to keep): ").strip() or weather_cond
                
                print(f"\nCurrent Traffic Volume: {vol}")
                volume_input = input("Traffic multiplier (1.0=current, 1.5=50% more, 0.5=50% less): ").strip()
                volume_mult = float(volume_input) if volume_input else 1.0
                
                # Prepare current params for simulation
                current_params = {
                    'VehicleCount': vol,
                    'Speed': speed,
                    'Hour': hour,
                    'DayOfWeek': day,
                    'IsWeekend': is_weekend,
                    'WeatherCondition': weather_cond,
                    'origin': origin,
                    'destination': dest,
                    'NoveltyScore': df['NoveltyScore'].values[0],
                    '_original_prediction': int(pred_class),
                    '_original_weather': weather_cond
                }
                
                modifications = {
                    'weather': new_weather,
                    'volume_multiplier': volume_mult
                }
                
                # Run simulation
                result = run_what_if_scenario(model, scaler, encoders, current_params, modifications)
                
                level_names = {0: "Low / Free Flow", 1: "Moderate", 2: "High / Congestion"}
                print(f"\n>>> WHAT-IF RESULT <<<")
                print(f"Original:  {level_names.get(result['original_level'], 'Unknown')} (Level {result['original_level']})")
                print(f"Modified:  {level_names.get(result['modified_level'], 'Unknown')} (Level {result['modified_level']})")
                print(f"Impact:    {result['impact_description']}")
                print(f"Confidence: {result['confidence']:.1f}%")

            # 8. Community Reporting & Misinformation Flagging
            print("\n")
            
            # Allow reporting
            submit_choice = input("Submit traffic report for this route? (y/n): ").strip().lower()
            if submit_choice == 'y':
                report_text = input("Describe current conditions: ").strip()
                if report_text:
                    severity = input("Severity (Low/Moderate/High): ").strip() or "Moderate"
                    submit_report(route_key, report_text, severity)
                    print("[OK] Report submitted anonymously. Thank you!")
            
            # Allow flagging
            if reports:
                flag_choice = input("\nFlag a report as false/misleading? (number or 'n'): ").strip()
                if flag_choice.isdigit() and 1 <= int(flag_choice) <= len(reports):
                    idx = int(flag_choice) - 1
                    flag_report(reports[idx]['id'])
                    print(f"[OK] Report flagged. Reports with 5+ flags will be hidden.")

            again = input("\n\nCheck another route? (y/n): ").strip().lower()
            if again != 'y': break
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
