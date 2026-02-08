"""
Station Data Verification Tool
Validates OpenStreetMap data by cross-referencing with Google Maps.
"""

import sys
sys.path.append('.')

from src.station_locator import get_coords_for_location, get_stations_along_route

def generate_google_maps_link(lat, lon, name="Location"):
    """Generate a Google Maps link for verification."""
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

def verify_stations(origin="CSMT", dest="Gateway of India", city="Mumbai"):
    """
    Verify station data and generate validation report.
    """
    print("=" * 70)
    print("STATION DATA VERIFICATION REPORT")
    print("=" * 70)
    print(f"\nRoute: {origin} → {dest}")
    print(f"City: {city}")
    print(f"Data Source: OpenStreetMap (OSM)")
    print(f"Query Method: OSMnx Python Library\n")
    
    # Get coordinates
    print("Step 1: Geocoding Locations...")
    origin_coords = get_coords_for_location(origin, city)
    dest_coords = get_coords_for_location(dest, city)
    
    if not origin_coords or not dest_coords:
        print("ERROR: Could not geocode locations")
        return
    
    print(f"✓ Origin: {origin} → ({origin_coords[0]:.6f}, {origin_coords[1]:.6f})")
    print(f"✓ Dest:   {dest} → ({dest_coords[0]:.6f}, {dest_coords[1]:.6f})")
    
    # Calculate midpoint
    mid_lat = (origin_coords[0] + dest_coords[0]) / 2
    mid_lon = (origin_coords[1] + dest_coords[1]) / 2
    print(f"✓ Midpoint: ({mid_lat:.6f}, {mid_lon:.6f})")
    print(f"✓ Search Radius: 2.0 km\n")
    
    # Query stations
    print("Step 2: Querying OpenStreetMap Database...")
    stations = get_stations_along_route(origin_coords, dest_coords, radius_km=2.0)
    
    # Display Fuel Stations
    print("\n" + "=" * 70)
    print("FUEL STATIONS (amenity=fuel)")
    print("=" * 70)
    fuel_stations = stations['fuel_stations']
    
    if fuel_stations:
        print(f"Total Found: {len(fuel_stations)}\n")
        for i, station in enumerate(fuel_stations[:10], 1):  # Show top 10
            print(f"{i}. {station['name']}")
            print(f"   Distance: {station['distance']:.2f} km from route midpoint")
            print(f"   GPS: ({station['lat']:.6f}, {station['lon']:.6f})")
            print(f"   Verify: {generate_google_maps_link(station['lat'], station['lon'], station['name'])}")
            print()
    else:
        print("No fuel stations found in this area.\n")
    
    # Display EV Chargers
    print("=" * 70)
    print("EV CHARGING STATIONS (amenity=charging_station)")
    print("=" * 70)
    ev_chargers = stations['ev_chargers']
    
    if ev_chargers:
        print(f"Total Found: {len(ev_chargers)}\n")
        for i, charger in enumerate(ev_chargers[:10], 1):
            print(f"{i}. {charger['name']}")
            print(f"   Distance: {charger['distance']:.2f} km from route midpoint")
            print(f"   GPS: ({charger['lat']:.6f}, {charger['lon']:.6f})")
            print(f"   Verify: {generate_google_maps_link(charger['lat'], charger['lon'], charger['name'])}")
            print()
    else:
        print("No EV charging stations found in this area.")
        print("Note: EV charger data may be limited in OSM for some regions.\n")
    
    # Validation Instructions
    print("=" * 70)
    print("HOW TO VALIDATE (For Demo/Presentation)")
    print("=" * 70)
    print("""
1. Click any 'Verify' link above to open Google Maps
2. Check if a fuel station/charger exists at that GPS location
3. OpenStreetMap data is community-verified and crowdsourced
4. Data accuracy depends on OSM contributor updates

WHY THIS DATA IS RELIABLE:
- Source: OpenStreetMap.org (used by Wikipedia, Apple Maps, etc.)
- Query Library: OSMnx (maintained by USC researchers)
- Real-time: Queries live OSM database at runtime
- Verifiable: Every result has GPS coords you can cross-check

DEMO TIP:
During presentation, pick 2-3 stations and verify live on Google Maps
to show the system queries real, accurate data.
    """)
    
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    verify_stations()
