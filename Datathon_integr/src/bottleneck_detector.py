import numpy as np
import torch

def predict_future_bottlenecks(model, current_state, scaler, feature_cols, classes, 
                                time_horizons=[0.5, 1.0, 2.0], device='cpu'):
    """
    Predicts congestion levels at future time horizons.
    
    Args:
        model: Trained LSTM model
        current_state: Dict with current traffic parameters
        scaler: Fitted scaler from artifacts
        feature_cols: Feature column names
        classes: Congestion level classes
        time_horizons: List of hours ahead to predict (e.g., [0.5, 1, 2])
        device: torch device
        
    Returns:
        List of dicts: [{'time_ahead': 0.5, 'level': 1, 'confidence': 0.85}, ...]
    """
    results = []
    
    # Start with current state
    state = current_state.copy()
    
    for horizon in time_horizons:
        # Simulate time progression
        hour_delta = horizon
        new_hour = (state['Hour'] + int(hour_delta)) % 24
        
        # Traffic decay model (simple heuristic)
        # Peak hours: 8-11, 17-20
        is_current_peak = (8 <= state['Hour'] <= 11) or (17 <= state['Hour'] <= 20)
        is_future_peak = (8 <= new_hour <= 11) or (17 <= new_hour <= 20)
        
        if is_current_peak and not is_future_peak:
            # Leaving peak: traffic decreases
            state['VehicleCount'] *= 0.6
            state['Speed'] *= 1.3
        elif not is_current_peak and is_future_peak:
            # Entering peak: traffic increases
            state['VehicleCount'] *= 1.5
            state['Speed'] *= 0.7
        else:
            # Gradual decay
            state['VehicleCount'] *= 0.95
            state['Speed'] *= 1.02
            
        # Update time
        state['Hour'] = new_hour
        
        # Event impact decay (events typically last 2-3 hours)
        if 'EventImpact' in state and horizon > 1.5:
            state['EventImpact'] = max(0, state['EventImpact'] - 0.3)
            
        # Prepare for prediction
        import pandas as pd
        df = pd.DataFrame([state])
        
        # Scale
        X_input = df[feature_cols].values
        X_scaled = scaler.transform(X_input)
        
        # Sequence (steady state)
        X_seq = np.tile(X_scaled, (5, 1))
        X_batch = torch.tensor(X_seq, dtype=torch.float32).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            output = model(X_batch)
            probs = torch.softmax(output, dim=1)
            conf, pred_idx = torch.max(probs, 1)
            
        pred_class = int(classes[pred_idx.item()])
        confidence = conf.item()
        
        results.append({
            'time_ahead': horizon,
            'hour': new_hour,
            'level': pred_class,
            'confidence': confidence,
            'volume': int(state['VehicleCount']),
            'speed': round(state['Speed'], 1)
        })
        
    return results

def detect_bottleneck_formation(predictions):
    """
    Detects if a bottleneck is forming by comparing future states.
    
    Args:
        predictions: Output from predict_future_bottlenecks
        
    Returns:
        Dict with bottleneck info or None
    """
    if len(predictions) < 2:
        return None
        
    # Check for congestion level increase
    for i in range(1, len(predictions)):
        prev_level = predictions[i-1]['level']
        curr_level = predictions[i]['level']
        
        if curr_level > prev_level:
            return {
                'detected': True,
                'forms_at': predictions[i]['time_ahead'],
                'hour': predictions[i]['hour'],
                'severity': curr_level,
                'confidence': predictions[i]['confidence']
            }
            
    return {'detected': False}
