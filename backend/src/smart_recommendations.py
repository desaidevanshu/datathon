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
        if pred['level'] > current_level and pred['level'] >= 2:
            # High congestion expected
            time_ahead = pred['time_ahead']
            hour = pred['hour']
            return f"ROUTE ALERT: High congestion expected in {time_ahead}h (at {hour:02d}:00)"
        elif pred['level'] > current_level and pred['level'] == 1:
            # Moderate congestion building
            time_ahead = pred['time_ahead']
            return f"Route Advisory: Moderate congestion building up in {time_ahead}h"
    
    # Route looks clear
    return None

def suggest_smart_break(future_predictions):
    """
    Recommends waiting if congestion will clear soon.
    
    Args:
        future_predictions: List of prediction dicts
        
    Returns:
        str: Break recommendation message, None if not applicable
    """
    if len(future_predictions) < 2:
        return None
    
    # Check for spike-then-ease pattern
    # If congestion rises then falls, suggest waiting
    for i in range(len(future_predictions) - 1):
        current_pred = future_predictions[i]
        next_pred = future_predictions[i + 1]
        
        # If congestion peaks then eases
        if current_pred['level'] >= 2 and next_pred['level'] < current_pred['level']:
            wait_time = next_pred['time_ahead']
            clear_hour = next_pred['hour']
            return f"SMART BREAK: Wait {wait_time:.1f}h for congestion to ease (clears by {clear_hour:02d}:00)"
    
    # Check if waiting would help (any future time is better than now)
    first_level = future_predictions[0]['level']
    for pred in future_predictions[1:]:
        if pred['level'] < first_level - 1:  # Significant improvement
            wait_time = pred['time_ahead']
            return f"SMART BREAK: Consider waiting {wait_time:.1f}h for better traffic conditions"
    
    return None

def optimize_departure_time(current_level, future_predictions, current_hour):
    """
    Finds the optimal departure time based on forecasts.
    
    Args:
        current_level: Current congestion level
        future_predictions: List of prediction dicts
        current_hour: Current hour (0-23)
        
    Returns:
        str: Departure time recommendation
    """
    level_names = {0: "Low / Free Flow", 1: "Moderate", 2: "High Congestion"}
    
    # Build time windows with levels
    windows = [("Now", current_hour, current_level)]
    for pred in future_predictions:
        time_label = f"+{pred['time_ahead']:.1f}h"
        windows.append((time_label, pred['hour'], pred['level']))
    
    # Find best window (lowest congestion level)
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
            # Current time is as good as it gets
            return "OPTIMAL DEPARTURE: Current time is acceptable (no significant improvement expected)"
