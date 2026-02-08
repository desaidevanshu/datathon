import pandas as pd
import xml.etree.ElementTree as ET
import os

def load_traffic_data(file_path):
    """
    Loads traffic data from XML or CSV.
    Returns a pandas DataFrame with normalized column names (PascalCase).
    """
    if isinstance(file_path, list):
        return unify_datasets(file_path)
    
    if file_path.endswith('.csv'):
        return _parse_csv_to_df(file_path)
    else:
        return parse_xml_to_df(file_path)

def normalize_schema(df, source_name):
    """
    Normalizes column names to a canonical format based on the source dataset.
    Canonical Schema: Timestamp, Speed, VehicleCount, WeatherCondition, CongestionLevel
    """
    df = df.copy()
    
    # Strip whitespace from columns
    df.columns = [c.strip() for c in df.columns]
    
    # Normalize headers to PascalCase or standard keys
    rename_map = {}
    
    if "all_features" in source_name:
        # Check typical columns
        rename_map = {
            'Traffic_Volume': 'VehicleCount', 
            'Traffic_Speed': 'Speed',
            'Weather_Conditions': 'WeatherCondition',
            'Congestion_Level': 'CongestionLevel',
            'lat': 'Latitude', 'long': 'Longitude'
        }
    elif "smart_mobility" in source_name:
        rename_map = {
            'Vehicle_Count': 'VehicleCount',
            'Traffic_Speed_kmh': 'Speed',
            'Weather_Condition': 'WeatherCondition',
            'Traffic_Condition': 'CongestionLevel',
            'Traffic_Light_State': 'TrafficSignalStatus'
        }
        rename_map = {
            'Vehicle_Count': 'VehicleCount',
            'Vehicle_Speed': 'Speed',
            'Congestion_Level': 'CongestionLevel'
        }
    elif "mumbai_multi_route" in source_name:
        rename_map = {
            'traffic_volume': 'VehicleCount',
            'avg_speed': 'Speed',
            'hour': 'Hour',
            'day_of_week': 'DayOfWeek',
            'is_weekend': 'IsWeekend',
            'timestamp': 'Timestamp'
            # origin, destination, congestion_index kept as is
        }
    
    # Apply renaming (flexible lookup)
    # We invert the map to check if flexible matching is needed, but for now specific map
    df = df.rename(columns=rename_map)
    
    # Standardize CongestionLevel if it exists
    if 'CongestionLevel' in df.columns:
        # Convert text levels to numeric if needed, or unify strings
        pass # Will handle value mapping in unify_datasets
        
    return df

def unify_datasets(file_paths):
    """
    Loads and unifies multiple CSV datasets into a single DataFrame.
    """
    dfs = []
    print(f"Unifying {len(file_paths)} datasets...")
    
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: File not found {path}")
            continue
            
        try:
            df = pd.read_csv(path)
            df = normalize_schema(df, path)
            
            # Feature Engineering: Add Source
            df['DatasetSource'] = os.path.basename(path)
            
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {path}: {e}")

    if not dfs:
        raise ValueError("No datasets loaded.")
        
    unified_df = pd.concat(dfs, axis=0, ignore_index=True)
    
    # Handle CongestionLevel Unification
    if 'congestion_index' in unified_df.columns and 'CongestionLevel' not in unified_df.columns:
        print("   [INFO] Auto-Binning 'congestion_index' to create Target Variable...")
        try:
             unified_df['CongestionLevel'] = pd.qcut(unified_df['congestion_index'], q=3, labels=[0, 1, 2]).astype(int)
        except:
             unified_df['CongestionLevel'] = unified_df['congestion_index'].apply(lambda x: 2 if x > 1.5 else (1 if x > 1.0 else 0))
    
    # Map 'Fast', 'Normal', 'Slow', 'congestion', etc. to 0, 1, 2
    def map_congestion(val):
        if pd.isna(val): return -1
        # If already numeric, return it
        if isinstance(val, (int, float)): return int(val)
        
        val = str(val).lower()
        if val in ['0', 'low', 'fast', 'free flow']: return 0
        if val in ['1', 'medium', 'normal', 'moderate']: return 1
        if val in ['2', 'high', 'slow', 'heavy', 'congestion']: return 2
        return 0 
        
    if 'CongestionLevel' in unified_df.columns:
        unified_df['CongestionLevel'] = unified_df['CongestionLevel'].apply(map_congestion)
        
    # Multi-Route Encoding
    encoders = {}
    if 'origin' in unified_df.columns:
        from sklearn.preprocessing import LabelEncoder
        le_origin = LabelEncoder()
        unified_df['origin'] = le_origin.fit_transform(unified_df['origin'].astype(str))
        encoders['origin'] = le_origin
        
    if 'destination' in unified_df.columns:
        from sklearn.preprocessing import LabelEncoder
        le_dest = LabelEncoder()
        unified_df['destination'] = le_dest.fit_transform(unified_df['destination'].astype(str))
        encoders['destination'] = le_dest

    # Fill NaN for critical columns with defaults or imputation
    unified_df['VehicleCount'] = unified_df['VehicleCount'].fillna(0)
    unified_df['Speed'] = unified_df['Speed'].fillna(unified_df['Speed'].mean())
    
    return unified_df, encoders

def _parse_csv_to_df(csv_path):
    print(f"Parsing CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Rename columns to match the XML schema (PascalCase) used in preprocessing
    rename_map = {
        'Traffic_Volume': 'TrafficVolume',
        'Traffic_Speed': 'TrafficSpeed',
        'Traffic_Density': 'TrafficDensity',
        'Congestion_Level': 'CongestionLevel',
        'Number_of_Lanes': 'NumberOfLanes',
        'Weather_Conditions': 'Condition',
        'Incidents_or_Events': 'Incident',
        'Travel_Time': 'TravelTime',
        'Road_Occupancy': 'RoadOccupancy',
        'Vehicle_Count': 'VehicleCount',
        'Vehicle_Speed': 'VehicleSpeed'
    }
    
    # Only rename columns that exist
    df = df.rename(columns=rename_map)
    
    # Parse Timestamp
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    return df

def parse_xml_to_df(xml_file_path):
    """
    Parses the traffic data XML file and returns a pandas DataFrame.
    """
    if not os.path.exists(xml_file_path):
        raise FileNotFoundError(f"File not found: {xml_file_path}")

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = []

    # Iterate through all nodes
    for node in root.findall('.//Node'):
        node_id = node.get('id')
        location = node.find('Location').text
        road_type = node.find('RoadType').text
        lanes = int(node.find('Lanes').text)
        speed_limit = float(node.find('SpeedLimit').text)

        # Iterate through all records in the TimeSeries
        for record in node.findall('.//Record'):
            record_data = {
                'NodeID': node_id,
                'Location': location,
                'RoadType': road_type,
                'Lanes': lanes,
                'SpeedLimit': speed_limit,
                'Timestamp': record.get('timestamp'),
                'Split': record.get('split')
            }

            # Helper function to extract text deeply
            def extract_text(element, tag_name, type_func=str, default=None):
                found = element.find(tag_name)
                if found is not None and found.text is not None:
                    try:
                        return type_func(found.text)
                    except ValueError:
                        return default
                return default

            # Traffic
            traffic = record.find('Traffic')
            if traffic is not None:
                record_data['TrafficVolume'] = extract_text(traffic, 'TrafficVolume', float)
                record_data['TrafficSpeed'] = extract_text(traffic, 'TrafficSpeed', float)
                record_data['TrafficDensity'] = extract_text(traffic, 'TrafficDensity', float)
                record_data['VehicleCount'] = extract_text(traffic, 'VehicleCount', int)
                record_data['VehicleSpeed'] = extract_text(traffic, 'VehicleSpeed', float)
                record_data['RoadOccupancy'] = extract_text(traffic, 'RoadOccupancy', float)
                record_data['TravelTime'] = extract_text(traffic, 'TravelTime', float)

            # Temporal
            temporal = record.find('Temporal')
            if temporal is not None:
                record_data['Hour'] = extract_text(temporal, 'Hour', int)
                record_data['DayOfWeek'] = extract_text(temporal, 'DayOfWeek')
                record_data['PeakType'] = extract_text(temporal, 'PeakType')

            # Infrastructure
            infra = record.find('Infrastructure')
            if infra is not None:
                record_data['RoadLength'] = extract_text(infra, 'RoadLength', float)
                record_data['NumberOfLanes'] = extract_text(infra, 'NumberOfLanes', int)
                record_data['IntersectionPresent'] = extract_text(infra, 'IntersectionPresent') == 'true'
                record_data['TrafficSignalCount'] = extract_text(infra, 'TrafficSignalCount', int)
                record_data['SignalPhaseDuration'] = extract_text(infra, 'SignalPhaseDuration', int)

            # Weather
            weather = record.find('Weather')
            if weather is not None:
                record_data['Condition'] = extract_text(weather, 'Condition')
                record_data['EmissionLevel'] = extract_text(weather, 'EmissionLevel', float)
                record_data['EnergyConsumption'] = extract_text(weather, 'EnergyConsumption', float)
            
            # Events
            events = record.find('Events')
            if events is not None:
                record_data['Incident'] = extract_text(events, 'Incident')
                record_data['AccidentCount'] = extract_text(events, 'AccidentCount', int)

            # SmartMobility
            mobility = record.find('SmartMobility')
            if mobility is not None:
                record_data['GPSUtilization'] = extract_text(mobility, 'GPSUtilization', float)
                record_data['PublicTransportActive'] = extract_text(mobility, 'PublicTransportActive') == 'true'
                record_data['RideSharingDemand'] = extract_text(mobility, 'RideSharingDemand', int)
                record_data['ParkingAvailability'] = extract_text(mobility, 'ParkingAvailability', int)
                record_data['SentimentScore'] = extract_text(mobility, 'SentimentScore', float)

            # GraphContext
            graph = record.find('GraphContext')
            if graph is not None:
                record_data['PreviousTimesteps'] = extract_text(graph, 'PreviousTimesteps', int)
                record_data['ConnectedNodes'] = extract_text(graph, 'ConnectedNodes')
                record_data['EdgeWeight'] = extract_text(graph, 'EdgeWeight', float)

            # Target
            target = record.find('Target')
            if target is not None:
                record_data['CongestionLevel'] = extract_text(target, 'CongestionLevel')
                record_data['DelayReduction'] = extract_text(target, 'DelayReduction', float)
                record_data['OptimalRoute'] = extract_text(target, 'OptimalRoute')

            data.append(record_data)

    return pd.DataFrame(data)

if __name__ == "__main__":
    # Test
    csv_path = r"c:/Users/Devanshu/OneDrive/Documents/datathon/all_features_traffic_dataset.csv"
    if os.path.exists(csv_path):
        df = load_traffic_data(csv_path)
        print(df.head())
        print(df.info())
    else:
        print("CSV file not found.")
