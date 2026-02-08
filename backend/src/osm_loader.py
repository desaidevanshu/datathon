import osmnx as ox
import networkx as nx
import pandas as pd

def get_road_network_stats(place_name="Mumbai, India"):
    """
    Downloads the road network for a given place and returns statistics.
    """
    print(f"Downloading road network for: {place_name}...")
    G = None
    try:
        # 1. Try by Place Name (Polygon)
        try:
             G = ox.graph_from_place(place_name, network_type='drive')
        except Exception as e:
             print(f"⚠️  Could not find polygon for '{place_name}'. Trying point-based query...")
             
        # 2. Key Fallback: Graph from Point (Radius 2km)
        if G is None:
             # Coordinates for Mumbai (could also geocode using geopy, but hardcoding fallback for robustness)
             mumbai_point = (19.0760, 72.8777) 
             print(f"   Downloading 2km radius around {mumbai_point}...")
             G = ox.graph_from_point(mumbai_point, dist=2000, network_type='drive')
        
        # Calculate basic stats
        stats = ox.basic_stats(G)
        
        # Extract edge attributes (Speed limit, lanes, length)
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
        
        # Process Speed Limit (often heterogeneous or missing)
        if 'maxspeed' in edges.columns:
            # Clean and convert to numeric (takes first value if list)
            def clean_maxspeed(x):
                if isinstance(x, list):
                    x = x[0]
                try:
                    return float(x)
                except:
                    return 50.0 # Default fallback
            
            avg_speed_limit = edges['maxspeed'].apply(clean_maxspeed).mean()
        else:
            avg_speed_limit = 50.0 # Default
            
        # Process Lanes
        if 'lanes' in edges.columns:
            def clean_lanes(x):
                if isinstance(x, list):
                    x = x[0]
                try:
                    return int(x)
                except:
                    return 2 # Default fallback
            avg_lanes = edges['lanes'].apply(clean_lanes).mean()
        else:
            avg_lanes = 2.0
            
        # Average Road Length (Edge length)
        avg_road_length = edges['length'].mean()
        
        # Intersection density
        intersection_count = stats['n'] # Number of nodes ~ intersections
        
        result = {
            "Place": place_name,
            "Nodes (Intersections)": intersection_count,
            "Edges (Road Segments)": stats['m'],
            "Avg Speed Limit": round(avg_speed_limit, 2),
            "Avg Lanes": round(avg_lanes, 2),
            "Avg Road Length (m)": round(avg_road_length, 2),
            "Street Length Total (m)": stats['edge_length_total']
        }
        
        print("Road Network Stats:")
        for k, v in result.items():
            print(f"  {k}: {v}")
            
        return result
        
    except Exception as e:
        print(f"Error downloading OSM data: {e}")
        return None

if __name__ == "__main__":
    get_road_network_stats("Andheri East, Mumbai, India")
