import osmnx as ox
import pandas as pd
from geopy.distance import geodesic

# Location cache to avoid repeated geocoding
_location_cache = {}

def get_coords_for_location(location_name, city="Mumbai, India"):
    """
    Geocodes a location name to (lat, lon) coordinates.
    Uses caching to speed up repeated queries.
    
    Args:
        location_name: Name of the location (e.g., "CSMT", "Gateway of India")
        city: City context for geocoding
        
    Returns:
        Tuple (lat, lon) or None if geocoding fails
    """
    # Check cache first
    cache_key = f"{location_name}, {city}"
    if cache_key in _location_cache:
        return _location_cache[cache_key]
    
    try:
        # Try geocoding with city context
        full_query = f"{location_name}, {city}"
        location = ox.geocode(full_query)
        _location_cache[cache_key] = location
        return location
    except Exception as e:
        print(f"   ! Geocoding failed for '{location_name}': {e}")
        return None

def get_stations_along_route(origin_coords, dest_coords, radius_km=2.0):
    """
    Finds fuel stations and EV charging stations near the route corridor.
    
    Args:
        origin_coords: (lat, lon) tuple for origin
        dest_coords: (lat, lon) tuple for destination
        radius_km: Search radius from route midpoint in kilometers
        
    Returns:
        dict: {
            'fuel_stations': [{name, distance, lat, lon}, ...],
            'ev_chargers': [{name, distance, lat, lon}, ...]
        }
    """
    if not origin_coords or not dest_coords:
        return {'fuel_stations': [], 'ev_chargers': []}
    
    # Calculate midpoint
    mid_lat = (origin_coords[0] + dest_coords[0]) / 2
    mid_lon = (origin_coords[1] + dest_coords[1]) / 2
    midpoint = (mid_lat, mid_lon)
    
    results = {
        'fuel_stations': [],
        'ev_chargers': []
    }
    
    try:
        # Query fuel stations (amenity=fuel)
        tags_fuel = {'amenity': 'fuel'}
        gdf_fuel = ox.features_from_point(
            midpoint, 
            tags=tags_fuel, 
            dist=radius_km * 1000  # Convert km to meters
        )
        
        if not gdf_fuel.empty:
            for idx, row in gdf_fuel.iterrows():
                # Extract coordinates
                if row.geometry.geom_type == 'Point':
                    poi_coords = (row.geometry.y, row.geometry.x)
                else:
                    # For polygons, use centroid
                    poi_coords = (row.geometry.centroid.y, row.geometry.centroid.x)
                
                # Calculate distance from midpoint
                distance = geodesic(midpoint, poi_coords).km
                
                # Get name (fallback to "Unnamed")
                name = row.get('name', 'Unnamed Fuel Station')
                if pd.isna(name):
                    name = 'Unnamed Fuel Station'
                
                results['fuel_stations'].append({
                    'name': name,
                    'distance': distance,
                    'lat': poi_coords[0],
                    'lon': poi_coords[1]
                })
        
    except Exception as e:
        print(f"   ! Fuel station query failed: {e}")
    
    try:
        # Query EV charging stations (amenity=charging_station)
        tags_ev = {'amenity': 'charging_station'}
        gdf_ev = ox.features_from_point(
            midpoint,
            tags=tags_ev,
            dist=radius_km * 1000
        )
        
        if not gdf_ev.empty:
            for idx, row in gdf_ev.iterrows():
                if row.geometry.geom_type == 'Point':
                    poi_coords = (row.geometry.y, row.geometry.x)
                else:
                    poi_coords = (row.geometry.centroid.y, row.geometry.centroid.x)
                
                distance = geodesic(midpoint, poi_coords).km
                
                name = row.get('name', 'Unnamed EV Charger')
                if pd.isna(name):
                    operator = row.get('operator', '')
                    if operator and not pd.isna(operator):
                        name = f"{operator} Charging Point"
                    else:
                        name = 'Unnamed EV Charger'
                
                results['ev_chargers'].append({
                    'name': name,
                    'distance': distance,
                    'lat': poi_coords[0],
                    'lon': poi_coords[1]
                })
        
    except Exception as e:
        print(f"   ! EV charger query failed: {e}")
    
    # Sort by distance
    results['fuel_stations'].sort(key=lambda x: x['distance'])
    results['ev_chargers'].sort(key=lambda x: x['distance'])
    
    return results
