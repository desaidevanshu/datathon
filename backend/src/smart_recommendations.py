"""
Smart Recommendations Module
Provides intelligent routing and timing suggestions based on congestion forecasts.
"""

def get_route_viability(current_level, future_predictions):
    """
    Checks if the route will experience high congestion.
    
    Args:
        current_level: Current congestion level (0, 1, or 2)
        future_predictions: List of prediction dicts from bottleneck_detector
        
    Returns:
        str: Warning message if congestion expected, None otherwise
    """
    # Check if any future prediction shows worsening congestion
    for pred in future_predictions:
        # Map congestion string to level if needed, or use existing logic if adapted
        # predict.py keys: step (+1h), hour, congestion_level (High), is_bottleneck
        
        level_str = pred.get('congestion_level', 'Low')
        level = 0
        if level_str in ['High', 'Critical']: level = 2
        elif level_str in ['Medium', 'Moderate']: level = 1
        
        # Parse time_ahead from step string "+1h" -> 1.0
        try:
            time_ahead = float(pred.get('step', '+0h').replace('+', '').replace('h', ''))
        except:
            time_ahead = 0.0
            
        hour = pred.get('hour', 0)

        if level > current_level and level >= 2:
            # High congestion expected
            return f"ROUTE ALERT: High congestion expected in {time_ahead}h (at {hour:02d}:00)"
        elif level > current_level and level == 1:
            # Moderate congestion building
            return f"Route Advisory: Moderate congestion building up in {time_ahead}h"
    
    # Route looks clear
    return "Route condition stable."

def suggest_smart_break(future_predictions):
    """
    Recommends waiting if congestion will clear soon.
    """
    if len(future_predictions) < 2:
        return "No specific break needed."
    
    # Pre-process predictions into a uniform list of (level, time_ahead, hour)
    processed_preds = []
    for pred in future_predictions:
        level_str = pred.get('congestion_level', 'Low')
        level = 0
        if level_str in ['High', 'Critical']: level = 2
        elif level_str in ['Medium', 'Moderate']: level = 1
        
        try:
            time_ahead = float(pred.get('step', '+0h').replace('+', '').replace('h', ''))
        except:
            time_ahead = 0.0
            
        processed_preds.append({'level': level, 'time_ahead': time_ahead, 'hour': pred.get('hour', 0)})

    # Check for spike-then-ease pattern
    for i in range(len(processed_preds) - 1):
        current_pred = processed_preds[i]
        next_pred = processed_preds[i + 1]
        
        # If congestion peaks then eases
        if current_pred['level'] >= 2 and next_pred['level'] < current_pred['level']:
            wait_time = next_pred['time_ahead']
            clear_hour = next_pred['hour']
            return f"SMART BREAK: Wait {wait_time:.1f}h for congestion to ease (clears by {clear_hour:02d}:00)"
    
    # Check if waiting would help (any future time is better than now)
    if not processed_preds: return "Traffic flow normal."
    
    first_level = processed_preds[0]['level']
    for pred in processed_preds[1:]:
        if pred['level'] < first_level - 1:  # Significant improvement
            wait_time = pred['time_ahead']
            return f"SMART BREAK: Consider waiting {wait_time:.1f}h for better traffic conditions"
    
    return "Traffic is standard. No specific break needed."

def optimize_departure_time(current_level, future_predictions, current_hour):
    """
    Finds the optimal departure time based on forecasts.
    """
    level_names = {0: "Low / Free Flow", 1: "Moderate", 2: "High Congestion"}
    
    # Build time windows with levels
    windows = [("Now", current_hour, current_level)]
    
    for pred in future_predictions:
        level_str = pred.get('congestion_level', 'Low')
        level = 0
        if level_str in ['High', 'Critical']: level = 2
        elif level_str in ['Medium', 'Moderate']: level = 1
        
        try:
            time_ahead = float(pred.get('step', '+0h').replace('+', '').replace('h', ''))
        except:
            time_ahead = 0.0
            
        time_label = f"+{time_ahead:.1f}h"
        windows.append((time_label, pred.get('hour', 0), level))
    
    # Find best window (lowest congestion level)
    if not windows: return "Leave anytime."
    
    best_window = min(windows, key=lambda x: x[2])
    
    # Build recommendation
    if best_window[0] == "Now":
        return "OPTIMAL DEPARTURE: Leave now for best travel conditions"
    else:
        best_time = best_window[0]
        best_hour = best_window[1]
        best_level = level_names.get(best_window[2], "Unknown")
        
        if best_window[2] < current_level:
            return f"OPTIMAL DEPARTURE: Wait and leave at {best_hour:02d}:00 ({best_time}) - {best_level}"
        else:
            return "OPTIMAL DEPARTURE: Current time is acceptable."
