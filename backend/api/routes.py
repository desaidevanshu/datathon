from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.routing import RoutingService
from services.featherless import FeatherlessService
# from services.prediction import PredictionService
from models.schemas import RouteRequest, CongestionPredictionRequest, CongestionPredictionResponse, GeoPoint

router = APIRouter()
routing_service = RoutingService()
featherless_service = FeatherlessService()
# prediction_service = PredictionService()

@router.post("/route", response_model=dict)
async def get_route(request: RouteRequest):
    """
    Get route coordinates and congestion prediction.
    """
    try:
        # 1. Calculate Route
        route_coords = routing_service.get_route(request.start, request.destination)
        if not route_coords:
            raise HTTPException(status_code=404, detail="No route found")

        # 2. Get Route Segments (for prediction)
        # Mock segment IDs based on route length
        segment_ids = [f"seg_{i}" for i in range(len(route_coords) // 10 + 1)] 
        
        # 3. Predict Congestion (Using Featherless API)
        congestion = await featherless_service.predict_congestion(segment_ids)
        
        return {
            "route": route_coords,
            "congestion": congestion,
            "duration": 1200, # Mock duration
            "distance": 5.0   # Mock distance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/congestion/heatmap")
async def get_heatmap(lat: float, lon: float, radius: float = 2000):
    """
    Get congestion heat map data for a specific area.
    """
    # Mock data for heatmap
    # Return a list of points with intensity
    heatmap_data = []
    import random
    
    # Generate random points around center
    for _ in range(50):
        d_lat = random.uniform(-0.01, 0.01)
        d_lon = random.uniform(-0.01, 0.01)
        heatmap_data.append({
            "lat": lat + d_lat,
            "lon": lon + d_lon,
            "intensity": random.random() # 0 to 1
        })
        
    return {"heatmap": heatmap_data}

@router.get("/models")
async def get_models():
    """
    List available models (Mock or Real from Featherless)
    """
    return {"models": ["traffic-forecaster-v1", "urban-flow-optimizer"]}
