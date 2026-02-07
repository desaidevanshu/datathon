from pydantic import BaseModel
from typing import List, Optional

class GeoPoint(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start: GeoPoint
    destination: GeoPoint

class CongestionPredictionRequest(BaseModel):
    segment_ids: List[str]
    time_of_day: str  # e.g., "08:00"
    weather: Optional[str] = "clear"

class CongestionPredictionResponse(BaseModel):
    segment_id: str
    congestion_level: str  # low, medium, high
    confidence: float
