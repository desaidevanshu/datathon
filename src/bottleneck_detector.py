"""
Future Bottleneck Detector
Predicts traffic bottlenecks on specific route segments
"""

from src.route_analyzer import get_route_coordinates, MUMBAI_LOCATIONS
from geopy.distance import geodesic
import numpy as np


def divide_route_into_segments(source, destination, segment_length_km=2):
    """
    Divide route into segments for analysis
    
    Returns: List of segment dictionaries with coordinates and names
    """
    source_coords, dest_coords = get_route_coordinates(source, destination)
    
    if not source_coords or not dest_coords:
        return []
    
    # Calculate route distance
    total_distance = geodesic(source_coords, dest_coords).kilometers
    num_segments = max(int(total_distance / segment_length_km), 1)
    
    segments = []
    
    for i in range(num_segments + 1):
        # Linear interpolation between source and dest
        ratio = i / num_segments if num_segments > 0 else 0
        
        lat = source_coords[0] + (dest_coords[0] - source_coords[0]) * ratio
        lon = source_coords[1] + (dest_coords[1] - source_coords[1]) * ratio
        
        # Find nearest known location for naming
        nearest_loc = find_nearest_location(lat, lon)
        
        segments.append({
            "index": i,
            "lat": lat,
            "lon": lon,
            "name": nearest_loc,
            "distance_from_start_km": round(total_distance * ratio, 2)
        })
    
    return segments


def find_nearest_location(lat, lon):
    """Find nearest named location from coordinates"""
    point = (lat, lon)
    min_dist = float('inf')
    nearest = "Mumbai"
    
    for loc_name, coords in MUMBAI_LOCATIONS.items():
        dist = geodesic(point, coords).kilometers
        if dist < min_dist:
            min_dist = dist
            nearest = loc_name
    
    return f"near {nearest}" if min_dist > 1 else nearest


def detect_bottlenecks(source, destination, prediction_data, events_data):
    """
    Detect future bottlenecks on route
    
    Args:
        source: Source location
        destination: Destination location
        prediction_data: LSTM prediction data with forecasts
        events_data: Current events affecting the route
    
    Returns:
        List of bottleneck predictions
    """
    segments = divide_route_into_segments(source, destination)
    
    if not segments:
        return []
    
    # Get forecast data
    forecasts = prediction_data.get("forecast", [])
    events = events_data.get("Events", [])
    
    bottlenecks = []
    
    for segment in segments:
        # Check if segment will have high congestion in forecasts
        bottleneck_prob = calculate_bottleneck_probability(
            segment, forecasts, events
        )
        
        if bottleneck_prob["probability"] > 0.5:  # 50% threshold
            bottlenecks.append({
                "location": segment["name"],
                "lat": segment["lat"],
                "lon": segment["lon"],
                "eta_minutes": bottleneck_prob["eta_minutes"],
                "congestion_forecast": bottleneck_prob["level"],
                "probability": round(bottleneck_prob["probability"], 2),
                "reason": bottleneck_prob["reason"]
            })
    
    # Sort by ETA (soonest first)
    bottlenecks.sort(key=lambda x: x["eta_minutes"])
    
    return bottlenecks[:3]  # Top 3 bottlenecks


def calculate_bottleneck_probability(segment, forecasts, events):
    """
    Calculate probability of bottleneck at a segment
    
    Returns: dict with probability, level, eta_minutes, reason
    """
    probability = 0.0
    level = "Medium"
    eta_minutes = 60
    reasons = []
    
    # Check forecasts for high congestion
    for forecast in forecasts[:3]:  # Check next 3 hours
        congestion = forecast.get("congestion_level", "Low")
        step_hour = int(forecast.get("step", "+1h").replace("+", "").replace("h", ""))
        
        if congestion in ["High", "Critical", "2", "3"]:
            probability += 0.4
            level = "High"
            eta_minutes = min(eta_minutes, step_hour * 60)
            reasons.append(f"High congestion predicted in {step_hour}h")
    
    # Check nearby events
    segment_coords = (segment["lat"], segment["lon"])
    
    for event in events:
        # Try to determine if event is near segment
        event_location = event.get("Location", "")
        
        # Simple check if segment name is in event location
        if segment["name"].replace("near ", "") in event_location:
            impact = event.get("Impact", "Low")
            
            if impact == "High":
                probability += 0.3
                level = "High"
                reasons.append(f"{event.get('Category')}: {event.get('Name')[:50]}")
            elif impact == "Medium":
                probability += 0.15
                reasons.append(f"{event.get('Category')}: {event.get('Name')[:50]}")
    
    # Cap probability at 1.0
    probability = min(probability, 1.0)
    
    # Determine final level
    if probability > 0.7:
        level = "Critical"
    elif probability > 0.5:
        level = "High"
    else:
        level = "Medium"
    
    reason = reasons[0] if reasons else "Traffic pattern analysis"
    
    return {
        "probability": probability,
        "level": level,
        "eta_minutes": eta_minutes,
        "reason": reason
    }
