"""
What-If Scenario Simulator
Allows users to test how predictions change with modified conditions.
"""
import pandas as pd

def run_what_if_scenario(model, scaler, label_encoders, current_params, modifications):
    """
    Run prediction with modified parameters.
    
    Args:
        model: Trained LSTM model
        scaler: Feature scaler
        label_encoders: Dict of label encoders
        current_params: Dict with current values (VehicleCount, Speed, Weather, etc.)
        modifications: Dict with changes (e.g., {'weather': 'Rain', 'volume_multiplier': 1.5})
        
    Returns:
        dict: {
            'original_level': int,
            'modified_level': int,
            'change': int,
            'impact_description': str
        }
    """
    import torch
    import numpy as np
    
    # Make a copy of current params
    modified_params = current_params.copy()
    
    # Apply modifications
    if 'weather' in modifications:
        modified_params['WeatherCondition'] = modifications['weather']
    
    if 'volume_multiplier' in modifications:
        mult = modifications['volume_multiplier']
        modified_params['VehicleCount'] = int(current_params['VehicleCount'] * mult)
        # More traffic -> slower speeds
        modified_params['Speed'] = max(5, current_params['Speed'] / mult)
    
    if 'speed_adjustment' in modifications:
        modified_params['Speed'] = modifications['speed_adjustment']
    
    # Create DataFrame
    df = pd.DataFrame([modified_params])
    
    # Encode categoricals - FIX: properly extract scalar values
    for col in ['WeatherCondition', 'origin', 'destination']:
        if col in df.columns and col in label_encoders:
            try:
                # Transform returns array, extract first element
                encoded_array = label_encoders[col].transform(df[col])
                df[col] = int(encoded_array[0])
            except (ValueError, KeyError, IndexError):
                # Unknown value - use default (0)
                df[col] = 0
                print(f"   (Note: '{modified_params.get(col)}' not in training data, using default)")


    # Scale features - use only the features the scaler was trained on (7 features)
    # DO NOT include 'origin' and 'destination' as they are not in the scaled features
    feature_cols = ['VehicleCount', 'Speed', 'Hour', 'DayOfWeek', 
                    'IsWeekend', 'WeatherCondition', 'NoveltyScore']
    
    # Force all columns to numeric type
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convert to numpy array and scale
    X = scaler.transform(df[feature_cols].values)
    X_tensor = torch.FloatTensor(X).unsqueeze(1)
    
    # Predict
    model.eval()
    with torch.no_grad():
        output = model(X_tensor)
        probabilities = torch.softmax(output, dim=1)
        pred_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][pred_class].item() * 100
    
    # Calculate change
    original_level = current_params.get('_original_prediction', 0)
    change = pred_class - original_level
    
    # Generate impact description
    if change > 0:
        impact = f"+{change} level(s) worse"
    elif change < 0:
        impact = f"{change} level(s) better"
    else:
        impact = "No significant change"
    
    # Describe reasons
    reasons = []
    if 'weather' in modifications and modifications['weather'] != current_params.get('_original_weather'):
        reasons.append(f"Weather: {modifications['weather']}")
    if 'volume_multiplier' in modifications and modifications['volume_multiplier'] != 1.0:
        mult = modifications['volume_multiplier']
        pct = int((mult - 1) * 100)
        if pct > 0:
            reasons.append(f"+{pct}% traffic volume")
        else:
            reasons.append(f"{pct}% traffic volume")
    
    if reasons:
        impact += f" due to {', '.join(reasons)}"
    
    return {
        'original_level': original_level,
        'modified_level': pred_class,
        'change': change,
        'confidence': confidence,
        'impact_description': impact
    }
