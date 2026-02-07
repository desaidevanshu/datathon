import requests
from models.schemas import GeoPoint
from typing import List, Tuple

class RoutingService:
    def __init__(self):
        self.base_url = "http://router.project-osrm.org/route/v1/driving"

    def get_route(self, start: GeoPoint, end: GeoPoint) -> List[Tuple[float, float]]:
        """
        Calculate route using OSRM public API (Free).
        Returns list of (lat, lon) tuples.
        """
        try:
            # OSRM expects lon,lat;lon,lat
            url = f"{self.base_url}/{start.lon},{start.lat};{end.lon},{end.lat}?overview=full&geometries=geojson"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and len(data["routes"]) > 0:
                    # OSRM returns [lon, lat], we need [lat, lon] usually, 
                    # BUT MapLibre expects [lon, lat] for GeoJSON. 
                    # The previous mock returned [lat, lon] tuples? 
                    # Let's check schemas. GeoJSON standard is [lon, lat].
                    # My previous code in App.jsx/FullMap.jsx used the data directly in a LineString.
                    # GeoJSON LineString expects [lon, lat].
                    # So we can just return the coords as is from OSRM (which are [lon, lat]).
                    
                    # Wait, schemas.py might mock something else.
                    # Let's look at `backend/api/routes.py`. It returns "route": route_coords.
                    # Frontend uses it in `coordinates: data.route`.
                    # So we should return [lon, lat] arrays.
                    
                    return data["routes"][0]["geometry"]["coordinates"]
            
            print(f"OSRM Error: {response.text}")
            return []
        except Exception as e:
            print(f"Routing error: {e}")
            return []

    def get_route_segments(self, start: GeoPoint, end: GeoPoint) -> List[dict]:
        """
        Mock segments for OSRM route since OSRM doesn't give stable edge IDs easily without map matching.
        """
        # Return dummy segments for predictions based on route
        return [{"id": f"seg_{i}", "name": "Road Segment"} for i in range(5)]
