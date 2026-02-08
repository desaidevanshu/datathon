import sys
sys.path.append('.')

from src.station_locator import get_coords_for_location, get_stations_along_route

# Test with CSMT and Gateway of India
print("Testing Station Locator...")
print("="*50)

origin = "CSMT" 
dest = "Gateway of India"
city = "Mumbai"

print(f"\nOrigin: {origin}")
print(f"Destination: {dest}")
print(f"\nGetting coordinates...")

origin_coords = get_coords_for_location(origin, city)
dest_coords = get_coords_for_location(dest, city)

print(f"Origin coords: {origin_coords}")
print(f"Dest coords: {dest_coords}")

if origin_coords and dest_coords:
    print(f"\nQuerying OpenStreetMap for stations...")
    stations = get_stations_along_route(origin_coords, dest_coords, radius_km=2.0)
    
    print(f"\n>>> NEARBY STATIONS <<<")
    fuel_count = len(stations['fuel_stations'])
    ev_count = len(stations['ev_chargers'])
    
    print(f"Fuel Stations: {fuel_count} found")
    for station in stations['fuel_stations'][:5]:
        print(f"  - {station['name']} ({station['distance']:.2f} km)")
    
    print(f"\nEV Chargers: {ev_count} found")
    for charger in stations['ev_chargers'][:5]:
        print(f"  - {charger['name']} ({charger['distance']:.2f} km)")
else:
    print("ERROR: Could not get coordinates")
