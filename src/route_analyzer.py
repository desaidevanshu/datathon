"""
Route Analyzer - Filters alerts and events by route corridor
"""

from geopy.distance import geodesic
from datetime import datetime, timedelta

# Major Mumbai locations (approximate coordinates)
MUMBAI_LOCATIONS = {
    "Bandra": (19.0596, 72.8295),
    "Dadar": (19.0176, 72.8484),
    "Andheri": (19.1136, 72.8697),
    "Worli": (19.0183, 72.8179),
    "Kurla": (19.0728, 72.8826),
    "Powai": (19.1176, 72.9060),
    "Chembur": (19.0633, 72.8986),
    "Borivali": (19.2304, 72.8572),
    "Thane": (19.2183, 72.9781),
    "Navi Mumbai": (19.0330, 73.0297),
    "Marine Drive": (18.9432, 72.8236),
    "Colaba": (18.9067, 72.8147),
    "Fort": (18.9388, 72.8354),
    "Churchgate": (18.9320, 72.8260),
    "CST": (18.9398, 72.8355),
    "Goregaon": (19.1663, 72.8526),
    "Malad": (19.1868, 72.8489),
    "Kandivali": (19.2073, 72.8497),
    "Ghatkopar": (19.0863, 72.9082),
    "Vikhroli": (19.1069, 72.9255),
    "Mulund": (19.1726, 72.9562),
    "Mahim": (19.0410, 72.8412),
    "Santacruz": (19.0811, 72.8428),
    "Vile Parle": (19.1006, 72.8474),
    "CSMT": (18.9398, 72.8355), # Alien for CST
}


def get_route_coordinates(source, destination):
    """
    Get coordinates for source and destination
    Returns: (source_coords, dest_coords) or None if not found
    """
    source_clean = source.strip().title()
    dest_clean = destination.strip().title()
    
    source_coords = MUMBAI_LOCATIONS.get(source_clean)
    dest_coords = MUMBAI_LOCATIONS.get(dest_clean)
    
    if not source_coords or not dest_coords:
        # Try to find partial matches
        for loc_name, coords in MUMBAI_LOCATIONS.items():
            if source_clean in loc_name or loc_name in source_clean:
                source_coords = coords
            if dest_clean in loc_name or loc_name in dest_clean:
                dest_coords = coords
    
    return (source_coords, dest_coords) if source_coords and dest_coords else (None, None)


def calculate_distance_to_route(point_lat, point_lon, route_start, route_end):
    """
    Calculate minimum distance from a point to a route (line segment)
    Returns distance in km
    """
    point = (point_lat, point_lon)
    
    # Simple approximation: distance to nearest endpoint
    # For production, use proper point-to-line-segment distance
    dist_to_start = geodesic(point, route_start).kilometers
    dist_to_end = geodesic(point, route_end).kilometers
    
    # Check if point is roughly on the path
    route_length = geodesic(route_start, route_end).kilometers
    
    # If point is equidistant from both ends and distances sum to ~route length, it's on path
    if abs((dist_to_start + dist_to_end) - route_length) < 2:  # 2km tolerance
        return min(dist_to_start, dist_to_end, route_length / 2)
    else:
        return min(dist_to_start, dist_to_end)


def filter_alerts_by_route(events, source, destination, radius_km=5):
    """
    Filter events that are within radius_km of the route corridor
    
    Args:
        events: List of event dictionaries with Location field
        source: Source location name
        destination: Destination location name
        radius_km: Maximum distance from route (default 5km)
    
    Returns:
        List of filtered events with distance added
    """
    source_coords, dest_coords = get_route_coordinates(source, destination)
    
    if not source_coords or not dest_coords:
        print(f"[WARNING] Could not find coordinates for {source} or {destination}")
        return events  # Return all events if coords not found
    
    filtered_events = []
    
    for event in events:
        location_name = event.get("Location", "")
        
        # Try to get coordinates from location name
        event_coords = None
        for loc_name, coords in MUMBAI_LOCATIONS.items():
            if loc_name in location_name or location_name in loc_name:
                event_coords = coords
                break
        
        if event_coords:
            # Calculate distance to route
            distance = calculate_distance_to_route(
                event_coords[0], event_coords[1],
                source_coords, dest_coords
            )
            
            if distance <= radius_km:
                event_copy = event.copy()
                event_copy["distance_to_route_km"] = round(distance, 2)
                filtered_events.append(event_copy)
        else:
            # If we can't determine location, include it with high distance
            event_copy = event.copy()
            event_copy["distance_to_route_km"] = radius_km + 1
            filtered_events.append(event_copy)
    
    # Sort by distance to route
    filtered_events.sort(key=lambda x: x.get("distance_to_route_km", 999))
    
    return filtered_events


def calculate_route_impact_score(events, source, destination):
    """
    Calculate overall impact score for a route based on events
    
    Returns: float between 0 and 1
    """
    if not events:
        return 0.0
    
    total_score = 0.0
    
    for event in events:
        impact = event.get("Impact", "Low")
        distance = event.get("distance_to_route_km", 10)
        
        # Base score by impact
        if impact == "High":
            base_score = 0.8
        elif impact == "Medium":
            base_score = 0.5
        else:
            base_score = 0.2
        
        # Reduce score based on distance
        distance_factor = max(0, 1 - (distance / 10))  # 0 at 10km+
        
        total_score += base_score * distance_factor
    
    # Normalize to 0-1 range
    normalized_score = min(total_score / len(events), 1.0)
    
    return round(normalized_score, 2)


def prioritize_alerts(events):
    """
    Sort events by priority:
    1. Recent (last 24h) + High Impact
    2. Recent + Medium/Low Impact
    3. Older (but still relevant)
    
    Does NOT strictly exclude older events, but pushes them to the bottom.
    """
    from email.utils import parsedate_to_datetime
    
    now = datetime.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7) # exclude very old stuff
    
    processed_events = []
    
    print(f"[DEBUG] Prioritizing {len(events)} events...")
    
    for event in events:
        time_str = event.get("Time", "")
        is_recent = False
        event_dt = None
        
        if time_str:
            try:
                # Try ISO format first (from our time-travel logic)
                event_dt = datetime.fromisoformat(time_str)
            except ValueError:
                try:
                    # Fallback to RSS/Email format
                    event_dt = parsedate_to_datetime(time_str)
                except:
                    pass
            
            if event_dt:
                if event_dt.tzinfo:
                    event_dt = event_dt.replace(tzinfo=None)
                
                # Filter out very old events (> 7 days)
                if event_dt < cutoff_7d:
                    continue
                    
                if event_dt >= cutoff_24h:
                    is_recent = True
        
        # Calculate Sort Score (Lower is better/higher priority)
        # Level 1: Recent High Impact (0)
        # Level 2: Recent Medium Impact (1)
        # Level 3: Recent Low Impact (2)
        # Level 4: Older High Impact (3)
        # Level 5: Older Medium Impact (4)
        # Level 6: Older Low Impact (5)
        
        impact = event.get("Impact", "Low")
        impact_score = 0 if impact == "High" else 1 if impact == "Medium" else 2
        
        recency_score = 0 if is_recent else 3
        
        final_score = recency_score + impact_score
        
        # Add sort keys
        event_copy = event.copy()
        event_copy["_sort_score"] = final_score
        event_copy["_timestamp"] = event_dt.timestamp() if event_dt else 0
        
        processed_events.append(event_copy)
    
    # Sort by: Score (asc), then Timestamp (desc - newest first)
    processed_events.sort(key=lambda x: (x["_sort_score"], -x["_timestamp"]))
    
    # Clean up internal keys
    for e in processed_events:
        e.pop("_sort_score", None)
        e.pop("_timestamp", None)

    print(f"[DEBUG] Returned {len(processed_events)} prioritized events")
    return processed_events
