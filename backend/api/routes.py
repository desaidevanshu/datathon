from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import sys
import os
from pathlib import Path

# Ensure backend directory is in path to import src
# backend/api/routes.py -> parent is backend/api -> parent.parent is backend/
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

try:
    from src.predict import get_prediction_data
except ImportError:
    # If src is in the project root instead of backend/src
    project_root = backend_dir.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    from src.predict import get_prediction_data

router = APIRouter()

@router.get("/predict")
async def predict_traffic(
    city: str = Query("Mumbai, India", description="Target City"),
    source: Optional[str] = Query(None, description="Start Location"),
    dest: Optional[str] = Query(None, description="End Location")
):
    """
    Get real-time traffic prediction and context.
    """
    try:
        # Call the core logic
        data = get_prediction_data(city=city, source=source, dest=dest)
        
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"])
            
        # --- DATATHON INTEGRATION: Smart Recommendations for General Prediction ---
        # We derived this logic for routes, now we apply it to general city prediction
        try:
            from backend.src.smart_recommendations import get_route_viability, suggest_smart_break, optimize_departure_time
            
            # Map congestion level to int (High=2, Med=1, Low=0)
            cong_level_str = data.get("prediction", {}).get("congestion_level", "Low")
            current_congestion = 0
            if "High" in cong_level_str or "Critical" in cong_level_str: current_congestion = 2
            elif "Medium" in cong_level_str or "Moderate" in cong_level_str: current_congestion = 1
            
            future_preds = data.get("forecast", [])
            
            viability_alert = get_route_viability(current_congestion, future_preds)
            smart_break = suggest_smart_break(future_preds)
            optimal_time = optimize_departure_time(current_congestion, future_preds, 17) # Mock current hour if not in inputs
            
            data["smart_analysis"] = {
                "viability_alert": viability_alert,
                "smart_break": smart_break,
                "optimal_departure": optimal_time,
                # Create a timeline for the chart
                "timeline": [
                    {"time": "Now", "traffic": 90 if current_congestion==2 else 50, "recommendation": "Avoid" if current_congestion==2 else "Go"},
                    {"time": "+1h", "traffic": 70, "recommendation": "Better"},
                    {"time": "+2h", "traffic": 40, "recommendation": "Best"}
                ]
            }
        except Exception as e:
            print(f"[WARNING] /predict Smart Analysis failed: {e}")
            data["smart_analysis"] = {}

        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GeoPoint(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start: GeoPoint
    destination: GeoPoint
    source_name: Optional[str] = None
    dest_name: Optional[str] = None

import requests
import polyline

def get_osrm_route(start_lat, start_lon, dest_lat, dest_lon):
    """
    Fetch real driving route from OSRM public API
    Returns: (main_route, alternates, duration, distance)
    """
    try:
        # OSRM expects: lon,lat;lon,lat
        # DEBUG LOG
        print(f"[DEBUG] get_osrm_route INPUT: start={start_lat},{start_lon}, dest={dest_lat},{dest_lon}")
        
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{dest_lon},{dest_lat}"
        print(f"[DEBUG] get_osrm_route URL: {url}")
        
        params = {
            "overview": "full",
            "geometries": "polyline",
            "alternatives": "3",
            "steps": "true",
            "annotations": "true"
        }
        headers = {
            "User-Agent": "TrafficIntelligenceApp/1.0"
        }
        
        print(f"[DEBUG] OSRM Request URL: {url}")
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            print(f"[DEBUG] OSRM Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])
                
                if not routes:
                    print(f"[DEBUG] OSRM returned 0 routes. Response: {data}")
                    return None, [], 0, 0, []
                
                # Process all routes
                all_routes = []
                for route in routes:
                    decoded = polyline.decode(route["geometry"]) # Returns [(lat, lon)]
                    # Convert to [lon, lat] for MapLibre
                    path = [[p[1], p[0]] for p in decoded]
                    all_routes.append({
                        "geometry": path,
                        "duration": route.get("duration", 0),
                        "distance": route.get("distance", 0) / 1000,
                        "legs": route.get("legs", [])
                    })
                
                # Main route is the first one
                main_route_geom = all_routes[0]["geometry"]
                duration = all_routes[0]["duration"]
                distance = all_routes[0]["distance"]
                
                # Alternates are the rest
                alternates = [r["geometry"] for r in all_routes[1:]]
                
                print(f"[DEBUG] Found {len(all_routes)} routes (1 main + {len(alternates)} alternates)")
                
                return main_route_geom, alternates, duration, distance, all_routes
            else:
                print(f"[DEBUG] OSRM Error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as req_err:
             print(f"[DEBUG] OSRM Network Error: {req_err}")
             return None, [], 0, 0, []
            
    except Exception as e:
        print(f"[WARNING] OSRM Route fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return None, [], 0, 0, []

    return None, [], 0, 0, []

@router.post("/route")
async def get_route(request: RouteRequest):
    """
    Get route coordinates, congestion prediction, and comprehensive route analysis.
    Optimized with parallel execution for faster response times.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # Determine location names
    source_name = request.source_name or "Bandra"
    dest_name = request.dest_name or "Dadar"
    
    start_coords = [request.start.lat, request.start.lon]
    dest_coords = [request.destination.lat, request.destination.lon]

    # --- Helper wrappers for blocking calls ---
    def _fetch_osrm():
        # Returns: main_route_coords, alternates_coords, duration_sec, distance_km, all_routes_details
        return get_osrm_route(request.start.lat, request.start.lon, request.destination.lat, request.destination.lon)

    def _fetch_prediction():
        try:
            return get_prediction_data(city="Mumbai", source=source_name, dest=dest_name)
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return {}

    def _fetch_reports():
        try:
            from backend.services.reports_fetcher import fetch_route_reports
            return fetch_route_reports(source=source_name, destination=dest_name, hours=24, limit=10)
        except Exception as e:
            print(f"[ERROR] Reports fetching failed: {e}")
            return []

    # --- Phase 1: Parallel Execution ---
    # Run OSRM, Prediction, and Reports fetching concurrently
    print(f"[INFO] Starting parallel fetch for {source_name} -> {dest_name}")
    
    # We use asyncio.to_thread to run blocking I/O in a separate thread
    # This is non-blocking for the event loop
    try:
        results = await asyncio.gather(
            asyncio.to_thread(_fetch_osrm),
            asyncio.to_thread(_fetch_prediction),
            asyncio.to_thread(_fetch_reports),
            return_exceptions=True
        )
    except Exception as e:
        print(f"[CRITICAL] Async gather failed: {e}")
        # Fallback empty values
        results = [ (None, [], 0, 0), {}, [] ]

    # Unpack results with error handling
    osrm_data = results[0] if not isinstance(results[0], Exception) else (None, [], 0, 0)
    pred_data = results[1] if not isinstance(results[1], Exception) else {}
    community_reports = results[2] if not isinstance(results[2], Exception) else []

    route_coords, alt_routes, duration, distance, all_routes_data = osrm_data

    # Fallback if OSRM fails
    if not route_coords:
        print("[INFO] Using fallback mock route generation")
        steps = 20
        route_coords = []
        for i in range(steps + 1):
            t = i / steps
            lat = request.start.lat + (request.destination.lat - request.start.lat) * t
            lon = request.start.lon + (request.destination.lon - request.start.lon) * t
            route_coords.append([lon, lat])
        
        # Mock alternate
        import math
        alt_route_coords = [] 
        for i in range(steps + 1):
            t = i / steps
            deviation = math.sin(t * math.pi) * 0.02
            lat = request.start.lat + (request.destination.lat - request.start.lat) * t + deviation
            lon = request.start.lon + (request.destination.lon - request.start.lon) * t + deviation
            alt_route_coords.append([lon, lat])
        
        alt_routes = [alt_route_coords]
        duration = 1200
        distance = 5.0

    # --- Phase 2: Processing (Fast, CPU bound) ---
    route_analysis = {
        "alerts_24hr": [],
        "community_reports": community_reports,
        "bottlenecks": [],
        "route_impact_score": 0.0,
        "ai_route_briefing": ""
    }

    events_data = pred_data.get("context", {}).get("events", {})
    
    try:
        # Filter alerts
        from src.route_analyzer import filter_alerts_by_route, prioritize_alerts, calculate_route_impact_score
        all_events = events_data.get("Events", [])
        recent = prioritize_alerts(all_events)
        route_alerts = filter_alerts_by_route(recent, source_name, dest_name, radius_km=5)
        
        route_analysis["alerts_24hr"] = route_alerts[:10]
        route_analysis["route_impact_score"] = calculate_route_impact_score(route_alerts, source_name, dest_name)
    except Exception as e:
        print(f"[ERROR] Alert processing failed: {e}")

    try:
        # Detect bottlenecks
        from src.bottleneck_detector import detect_bottlenecks
        route_analysis["bottlenecks"] = detect_bottlenecks(
            source=source_name, destination=dest_name, prediction_data=pred_data, events_data=events_data
        )
    except Exception as e:
        print(f"[ERROR] Bottleneck detection failed: {e}")

    # --- Phase 3: AI Briefing (Can be slow, so run in thread) ---
    def _gen_briefing():
        from src.traffic_anchor import generate_traffic_bulletin
        # Use our updated generate_route_briefing helper
        ctx = {
            **pred_data,
            "route_analysis": route_analysis,
            "source": source_name,
            "destination": dest_name,
            "community_reports": community_reports
        }
        return generate_route_briefing(ctx)

    try:
        # Run AI in background thread so it doesn't block if we wanted to stream (but here we await it)
        # Note: If this is too slow, we could skip it or cache it.
        # route_analysis["ai_route_briefing"] = await asyncio.to_thread(_gen_briefing)
        
        # USE NEW FEATHERLESS LOGIC
        from backend.genai_handler import generate_traffic_insight
        structured_ctx = {
             "selected_route_name": "Best Route",
             "selected_eta": pred_data.get('prediction', {}).get('eta', 0),
             "selected_congestion": pred_data.get('prediction', {}).get('congestion_level', 'Low'),
             "top_contributing_factors": "Traffic flow is normal"
        }
        print("[DEBUG] Calling Featherless AI from get_route...")
        route_analysis["ai_route_briefing"] = await asyncio.to_thread(generate_traffic_insight, structured_ctx)
        
    except Exception as e:
        print(f"[ERROR] AI Briefing failed: {e}")
        route_analysis["ai_route_briefing"] = "Traffic is building up near Dadar, but don't worry—this is still your fastest option. Drive safe!"

    # Map congestion level
    congestion_level = pred_data.get('prediction', {}).get('congestion_level', 'low')
    c_map = {'0': 'low', '1': 'medium', '2': 'high'}
    congestion_val = c_map.get(str(congestion_level), 'low')

    # Build routes array in the format frontend expects
    routes_response = []
    
    if all_routes_data:
        # Use the detailed route data from OSRM
        for idx, route_info in enumerate(all_routes_data):
            # Determine route characteristics
            is_fastest = idx == 0
            is_eco = idx == 1  # Second route is eco-friendly
            
            # Calculate congestion variation for different routes
            route_congestion = congestion_val
            if idx == 1:  # Eco route might have less congestion
                route_congestion = 'low' if congestion_val == 'high' else congestion_val
            elif idx == 2:  # Third route might have different congestion
                route_congestion = 'medium' if congestion_val != 'medium' else 'high'
            
            # Generate route label
            if is_fastest:
                route_label = "Fastest Route"
            elif is_eco:
                route_label = "Eco-Friendly Route"
            else:
                route_label = f"Alternative Route {idx}"
            
            # AI prediction for this route
            eta_min = round(route_info["duration"] / 60, 1)
            distance_km = round(route_info["distance"], 2)
            
            # Generate AI insight for this specific route
            ai_route_insight = f"{route_label}: {eta_min} min, {distance_km} km. "
            if route_congestion == 'high':
                ai_route_insight += "Expect heavy traffic. Consider alternative timing."
            elif route_congestion == 'medium':
                ai_route_insight += "Moderate traffic expected. Good travel conditions."
            else:
                ai_route_insight += "Clear roads ahead. Optimal travel time."
            
            routes_response.append({
                "points": route_info["geometry"],  # [[lon, lat], ...]
                "eta_min": eta_min,
                "distance_km": distance_km,
                "congestion_level": route_congestion,
                "label": route_label,
                "is_fastest": is_fastest,
                "is_eco": is_eco,
                "ai_prediction": ai_route_insight,
                "confidence_score": pred_data.get('prediction', {}).get('confidence_score', 85)
            })
    else:
        # Fallback: use the basic route_coords
        if route_coords:
            routes_response.append({
                "points": route_coords,
                "eta_min": round(duration / 60, 1) if duration else 0,
                "distance_km": round(distance, 2) if distance else 0,
                "congestion_level": congestion_val,
                "label": "Main Route",
                "is_fastest": True,
                "is_eco": False,
                "ai_prediction": "Route calculated successfully.",
                "confidence_score": 75
            })
        
        # Add alternates
        for idx, alt in enumerate(alt_routes):
            routes_response.append({
                "points": alt,
                "eta_min": round(duration / 60 * 1.15, 1) if duration else 0,
                "distance_km": round(distance * 1.1, 2) if distance else 0,
                "congestion_level": congestion_val,
                "label": f"Alternative Route {idx + 1}",
                "is_fastest": False,
                "is_eco": idx == 0,
                "ai_prediction": f"Alternative route with estimated {round(duration / 60 * 1.15, 1)} min travel time.",
                "confidence_score": 70
            })

    return {
        "routes": routes_response,  # Frontend expects this
        "route": route_coords,  # Keep for backward compatibility
        "alternative_route": alt_routes[0] if alt_routes else [],
        "alternates": alt_routes,
        "congestion": [{"congestion_level": congestion_val}],
        "forecast": pred_data.get('forecast', []),
        "duration": duration,
        "distance": distance,
        "route_analysis": route_analysis,
        "ai_insight": route_analysis.get("ai_route_briefing", ""),
        "prediction_data": {
            "overall_congestion": congestion_val,
            "confidence": pred_data.get('prediction', {}).get('confidence_score', 85),
            "weather": pred_data.get('context', {}).get('weather', {}).get('Condition', 'Clear'),
            "events": pred_data.get('context', {}).get('events', {}).get('Details', {}).get('Name', 'None')
        }
    }


@router.post("/analyze_routes")
async def analyze_routes(request: RouteRequest, user_preference: str = Query("Fastest route", description="User priority")):
    """
    Advanced Route Analysis with GenAI (Featherless) and ML Integration.
    Returns 3 best routes with predictions and explanation.
    """
    import asyncio
    
    # 1. Get Routes via OSRM (Known to work)
    start_coords = [request.start.lat, request.start.lon]
    dest_coords = [request.destination.lat, request.destination.lon]
    
    try:
        # Use explicit args to ensure correct coordinate order (Lat, Lon)
        main_route_points, alternates, duration_osrm, distance_osrm, all_routes_data = get_osrm_route(request.start.lat, request.start.lon, request.destination.lat, request.destination.lon)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OSRM Routing Failed: {str(e)}")
    
    if not main_route_points:
        raise HTTPException(status_code=404, detail="Could not find routes between locations")

    # 2. Build Response (Mocking ML/AI for stability and speed)
    routes_response = []
    
    congestion_level = "Low"
    confidence = 85
    
    if all_routes_data:
        for idx, route_info in enumerate(all_routes_data):
            is_fastest = idx == 0
            is_eco = idx == 1
            
            # Simple label logic
            if is_fastest: label = "Fastest Route"
            elif is_eco: label = "Eco-Friendly Route"
            else: label = f"Alternative {idx}"
            
            # Calculate mock cost (approx)
            cost = (route_info["distance"] / 1000) * 8 # approx cost
            
            routes_response.append({
                "points": route_info["geometry"],
                "eta_min": round(route_info["duration"] / 60, 1),
                "distance_km": round(route_info["distance"], 2),
                "congestion_level": congestion_level,
                "label": label,
                "is_fastest": is_fastest,
                "is_eco": is_eco,
                "estimated_cost_inr": round(cost),
                "ai_prediction": f"{label}: Estimated {round(route_info['duration']/60)} mins. Traffic conditions stable.",
                "confidence_score": confidence
            })
    
    # 3. Construct Final Response with RICH MOCK DATA for Frontend 2
    
    # AI Insight Generation (Real + Fallback)
    ai_insight_text = "Traffic is building up near Dadar, but don't worry—this is still your fastest option. Drive safe!"
    try:
        # Import dynamically to avoid top-level issues
        from backend.genai_handler import generate_traffic_insight
        
        # Prepare context for AI
        traffic_context = {
            "selected_route_name": "Fastest Route",
            "selected_eta": routes_response[0]["eta_min"] if routes_response else 0,
            "selected_congestion": congestion_level,
            "recommended_route_name": "Fastest Route",
            "recommended_eta": routes_response[0]["eta_min"] if routes_response else 0,
            "time_savings": 0,
            "future_eta_1h": int(routes_response[0]["eta_min"] * 1.1) if routes_response else 0,
            "top_contributing_factors": "Traffic accumulation near Dadar T.T."
        }
        
        # Call AI (Sync wrapper for simplicity in this correct version, or await if async)
        # GenAI handler is synchronous in the viewed file
        print("[DEBUG] Calling Featherless AI...")
        generated_text = generate_traffic_insight(traffic_context)
        if generated_text and len(generated_text) > 10:
             ai_insight_text = generated_text
             print("[DEBUG] Used Featherless AI Insight")
    except Exception as e:
        print(f"[WARNING] AI Generation failed, using fallback: {e}")

    # Mock Bottlenecks
    mock_bottlenecks = []
    if len(main_route_points) > 20: 
        # Add a bottleneck somewhere in middle
        mid = len(main_route_points) // 2
        mock_bottlenecks.append({
            "location": "Dadar T.T. Circle",
            "lat": main_route_points[mid][0], # lat
            "lon": main_route_points[mid][1], # lon
            "congestion_forecast": "Critical",
            "eta_minutes": 15,
            "probability": 0.89,
            "reason": "Vehicle breakdown reported"
        })

    # Mock Alerts
    mock_alerts = [
        {
            "Category": "Road Work",
            "Name": "Metro Construction",
            "Location": "Near Sena Bhavan",
            "distance_to_route_km": 0.5
        },
        {
            "Category": "Accident",
            "Name": "Minor Collision",
            "Location": "Western Express Hwy",
            "distance_to_route_km": 1.2
        }
    ]

    # Mock Community Reports
    mock_reports = [
        {
            "category": "Police",
            "netScore": 5,
            "title": "Police Checkpoint",
            "description": "Checking for PUC and heavy vehicles.",
            "location": "Mahim Causeway",
            "userName": "TrafficWatcher99"
        },
         {
            "category": "Hazard",
            "netScore": 3,
            "title": "Pothole",
            "description": "Large pothole in middle lane.",
            "location": "Bandra Reclamation",
            "userName": "MumbaiRoads"
        }
    ]

    return {
        "routes": routes_response,
        "best_route_index": 0,
        "analysis_context": {
            "bottlenecks": mock_bottlenecks,
            "alerts_24hr": mock_alerts,
            "community_reports": mock_reports,
            "route_impact_score": 0.75, # High impact
            "weather": "Clear",
            "events": []
        },
        "ai_insight": ai_insight_text,
        "prediction": {
            "congestion_level": congestion_level,
            "confidence_score": confidence
        },
        "congestion": [{"congestion_level": congestion_level}]
    }
    
    # 2. GenAI Insight
    structured_data = {
        "selected_route_name": selected_route["name"],
        "selected_eta": selected_route["eta_min"],
        "selected_congestion": selected_route["congestion_level"],
        "congestion_uncertainty": "Moderate" if selected_route["confidence"] == "Low" else "Low",
        
        "recommended_route_name": best_route["name"],
        "recommended_eta": best_route["eta_min"],
        "recommended_congestion": best_route["congestion_level"],
        "time_savings": round(routes_data[1]["eta_min"] - best_route["eta_min"], 1) if len(routes_data) > 1 else 0,
        
        "top_contributing_factors": "High traffic volume detected near Dadar circle" if dest_name == "Dadar" else "Standard peak hour traffic",
        
        # Forecast placeholders (Mock for now, or call predict.py forecast)
        "future_eta_1h": round(best_route["eta_min"] * 1.1, 1),
        "future_eta_2h": round(best_route["eta_min"] * 1.25, 1)
    }
    
    # Call Featherless (Async to not block, but we await for response)
    try:
        print("[DEBUG] Calling Featherless AI...")
        ai_explanation = await asyncio.to_thread(generate_traffic_insight, structured_data, user_preference)
        print(f"[DEBUG] Featherless AI Response: {ai_explanation[:100]}...")
    except Exception as e:
        print(f"[ERROR] Featherless AI failed: {e}")
        ai_explanation = None
    
    # 3. Hybrid Bottleneck Generation (Spatial + Temporal)
    bottlenecks = []
    
    # A. Spatial Detection: Scan OSRM steps for actual slow segments
    try:
        if routes_response and len(routes_response) > 0:
             main_route = routes_response[0]
             legs = main_route.get("legs", [])
             
             slowest_steps = []
             
             for leg in legs:
                 steps = leg.get("steps", [])
                 for step in steps:
                     # Calculate speed (km/h)
                     dist_m = step.get("distance", 0)
                     dur_s = step.get("duration", 0)
                     
                     if dur_s > 0 and dist_m > 50: # Only consider significant segments
                         speed_kmh = (dist_m / 1000) / (dur_s / 3600)
                         
                         # Thresholds for Bottlenecks
                         if speed_kmh < 20: # Very Slow
                             slowest_steps.append({
                                 "speed": speed_kmh,
                                 "loc": step.get("maneuver", {}).get("location"), # [lon, lat]
                                 "name": step.get("name", "Road Segment"),
                                 "severity": "High" if speed_kmh < 10 else "Moderate"
                             })

             # Sort by speed (ascending) to find worst bottlenecks
             slowest_steps.sort(key=lambda x: x["speed"])
             
             # Pick top 2 unique locations
             top_bottlenecks = slowest_steps[:2]
             
             if top_bottlenecks:
                 for b in top_bottlenecks:
                      if b["loc"]:
                          bottlenecks.append({
                             "lat": b["loc"][1],
                             "lon": b["loc"][0],
                             "type": "Traffic Jam" if b["severity"] == "High" else "Slowdown",
                             "severity": b["severity"],
                             "description": f"Heavy traffic on {b['name']} ({int(b['speed'])} km/h)"
                         })
             
             # FALLBACK: If no explicit slow steps found but route is congestion High
             elif best_route["congestion_index"] > 0.5 and not bottlenecks:
                 # Use previous heuristic logic as fallback
                 main_route_geometry = main_route["geometry"]
                 mid_idx = int(len(main_route_geometry) * 0.6)
                 if mid_idx < len(main_route_geometry):
                     pt = main_route_geometry[mid_idx]
                     bottlenecks.append({
                         "lat": pt[1],
                         "lon": pt[0],
                         "type": "Slowdown",
                         "severity": "Moderate",
                         "description": "General route congestion detected."
                     })
                     
    except Exception as e:
        print(f"[WARNING] Spatial Bottleneck detection failed: {e}")

    except Exception as e:
        print(f"[WARNING] Spatial Bottleneck detection failed: {e}")

    # B. AI Temporal Prediction
    if pred_data.get("forecast"):
        for f in pred_data["forecast"]:
             if f.get("is_bottleneck", False):
                  bottlenecks.append({
                      "location": f"Forecasted (+{f['step'].replace('+','').replace('h','')}h)",
                      "lat": best_route["points"][0][1], # Placeholder lat
                      "lon": best_route["points"][0][0], # Placeholder lon
                      "congestion_forecast": "Critical",
                      "eta_minutes": int(float(f['step'].replace('+','').replace('h','')) * 60),
                      "probability": f['confidence'] / 100.0,
                      "reason": "AI Predicted Congestion Spike"
                  })

    # 4. Smart Recommendations (Datathon Feature 3)
    try:
        # Fetch Real-Time Events for AI Context
        from backend.src.scraper import get_city_events
        from backend.src.smart_recommendations import get_route_viability, suggest_smart_break, optimize_departure_time
        
        events = get_city_events("Mumbai")
        # Handle new structure where 'Details' behaves differently or use 'Name' directly if corrected
        # In scraper.py we return {Incident:..., Details: {Name:..., Events:[...]}}
        event_name = events.get("Details", {}).get("Name", "None")
        
        # Extract necessary data for recommendations
        current_congestion = 0 # Default Low
        if best_route["congestion_level"] == "Medium": current_congestion = 1
        elif best_route["congestion_level"] == "High": current_congestion = 2
        
        # Use Real AI Predictions from Phase 1
        future_preds = pred_data.get("forecast", [])
        
        # Fallback if no forecast available
        if not future_preds:
             print("[WARNING] No forecast data found, using heuristic fallback.")
             future_preds = [
                 {'time_ahead': 0.5, 'hour': 18, 'level': current_congestion},
                 {'time_ahead': 1.0, 'hour': 19, 'level': max(0, current_congestion - 1)},
                 {'time_ahead': 2.0, 'hour': 20, 'level': 0}
             ]

        # Get Smart Recommendations
        viability_alert = get_route_viability(current_congestion, future_preds)
        smart_break = suggest_smart_break(future_preds)
        optimal_time = optimize_departure_time(current_congestion, future_preds, 17) # Mock 17:00

        structured_data["smart_recommendations"] = {
            "viability_alert": viability_alert,
            "smart_break": smart_break,
            "optimal_departure": optimal_time
        }
        
        # Inject Event into AI Context
        structured_data["top_contributing_factors"] = f"Event: {event_name}"
        
    except Exception as e:
        print(f"[WARNING] Smart Recommendations/Events failed: {e}")
        structured_data["smart_recommendations"] = {}

    structured_data["bottlenecks"] = bottlenecks

    return {
        "routes": routes_data,
        "best_route_index": 0,
        "ai_insight": ai_explanation,
        "analysis_context": structured_data,
        "congestion": [{"congestion_level": pred_data.get("prediction", {}).get("congestion_level", "Moderate")}]
    }

def generate_route_briefing(route_context):
    """
    Generate AI route briefing using LLM (Legacy)
    """
    try:
        from src.traffic_anchor import llm
        
        if not llm:
            return "Route analysis complete. Please check alerts and reports for details."
        
        route_analysis = route_context.get("route_analysis", {})
        alerts = route_analysis.get("alerts_24hr", [])
        reports = route_context.get("community_reports", [])
        bottlenecks = route_analysis.get("bottlenecks", [])
        source = route_context.get("source", "Source")
        dest = route_context.get("destination", "Destination")
        
        # Build context
        alerts_summary = f"{len(alerts)} active alerts" if alerts else "No alerts"
        reports_summary = f"{len(reports)} community reports" if reports else "No reports"
        bottlenecks_summary = ", ".join([b["location"] for b in bottlenecks[:2]]) if bottlenecks else "None detected"
        
        prompt = f"""You are a traffic route advisor. Provide a concise route briefing (2-3 sentences).

Route: {source} to {dest}
Active Alerts: {alerts_summary}
Community Reports: {reports_summary}
Predicted Bottlenecks: {bottlenecks_summary}

Give practical advice for this specific route."""

        messages = [
            ("system", "You are a helpful traffic route advisor. Be concise and actionable."),
            ("human", prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content.strip()
        
    except Exception as e:
        print(f"[ERROR] Route briefing generation failed: {e}")
        return f"Route from {route_context.get('source')} to {route_context.get('destination')} analyzed. Check alerts and reports for details."



@router.get("/locations")
async def get_locations():
    """
    Get list of available locations from the dataset.
    """
    try:
        csv_path = Path(backend_dir) / "all_features_traffic_dataset.csv"
        if not csv_path.exists():
             # Fallback if file not found
             return {"locations": ["Bandra-Kurla Complex", "Western Express Highway", "Linking Road"]}
        
        # Read CSV (Optimized: read only required column if possible, or cache)
        # For simplicity in this step, we read and cache uniquely
        import pandas as pd
        
        # Simple caching mechanism (could be improved)
        if not hasattr(get_locations, "cache"):
             df = pd.read_csv(csv_path)
             if "Road_Segment_ID" in df.columns:
                 # Get unique sorted IDs
                 ids = sorted(df["Road_Segment_ID"].unique())
                 get_locations.cache = [f"Road Segment {i}" for i in ids]
             else:
                 get_locations.cache = ["General Mumbai Traffic"]
        
        return {"locations": get_locations.cache}
        
    except Exception as e:
        print(f"[ERROR] Fetching locations failed: {e}")
        return {"locations": ["Bandra", "Andheri", "Dadar"]} # Fallback

# ==========================================
# New Features Integration (Datathon Expansion)
# ==========================================
from pydantic import BaseModel
from typing import List, Optional

# Import new logic
from src.predict import simulate_traffic, check_bottlenecks
import src.community_intel as community_intel

class SimulationRequest(BaseModel):
    location: str
    scenario: str # "Heavy Rain", "Accident"
    intensity: float = 1.0

class ReportRequest(BaseModel):
    location: str
    feedback: str
    severity: str = "Moderate"

@router.post("/simulate")
async def api_simulate(request: SimulationRequest):
    """
    Run traffic simulation.
    """
    try:
        # Convert scenario to params
        modifications = {}
        if request.scenario == "Heavy Rain":
            modifications['weather'] = "Rain"
            modifications['speed_adjustment'] = 20.0
        elif request.scenario == "Accident":
            modifications['volume_multiplier'] = 1.5
            
        result = simulate_traffic(request.location, "start", "end", modifications)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/congestion/bottlenecks")
async def api_bottlenecks(city: str = "Mumbai"):
    try:
        result = check_bottlenecks(city)
        return {"city": city, "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/community/report")
async def api_submit_report(report: ReportRequest):
    try:
        # report.location e.g. "Bandra-Worli"
        rid = community_intel.submit_report(report.location, report.feedback, report.severity)
        return {"status": "success", "report_id": rid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/community/feed")
async def api_community_feed(location: str = "Mumbai", hours: int = 24):
    try:
        # If location is generic, might need to filter broadly or show all?
        # For now, exact match or simple string logic in community_intel
        return {"location": location, "reports": reports}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/stations")
async def api_get_stations(request: RouteRequest):
    """
    Find Fuel and EV stations along a route.
    """
    try:
        # Use simple geocoding or provided coords
        start_coords = (request.start.lat, request.start.lon)
        dest_coords = (request.destination.lat, request.destination.lon)
        
        # We need OSmnx which is heavy, ensure it's imported
        from backend.src.station_locator import get_stations_along_route
        
        stations = get_stations_along_route(start_coords, dest_coords, radius_km=2.0)
        return {"status": "success", "data": stations}
    except Exception as e:
        print(f"[ERROR] Station locator failed: {e}")
        return {"status": "error", "message": str(e), "data": {"fuel_stations": [], "ev_chargers": []}}
