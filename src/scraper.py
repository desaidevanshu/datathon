import requests
from bs4 import BeautifulSoup
import random

def get_live_weather(city="Mumbai"):
    """
    Simulates fetching live weather data using Open-Meteo API (Free, No Key).
    """
    print(f"Fetching live weather for {city}...")
    try:
        # Geocoding (Simulated for simplicity, or use geopy if needed for exact coords)
        # Using Mumbai Coords roughly for demo
        lat, lon = 19.0760, 72.8777 
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&wind_speed_10m"
        response = requests.get(url)
        data = response.json()
        
        current = data.get('current', {})
        temp = current.get('temperature_2m', 30.0)
        wind = current.get('wind_speed_10m', 10.0)
        code = current.get('weather_code', 0)
        
        # Map WMO code to Condition
        if code <= 3: condition = "Clear"
        elif code <= 48: condition = "Fog"
        elif code <= 67: condition = "Rain"
        else: condition = "Storm"
        
        weather_info = {
            "City": city,
            "Temperature": temp,
            "Condition": condition,
            "WindSpeed": wind
        }
        print(f"Live Weather: {weather_info}")
        return weather_info
        
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {"Condition": "Clear", "Temperature": 30.0}

import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

def parse_rss_date(date_string):
    """Parse RSS pubDate to datetime object"""
    try:
        return parsedate_to_datetime(date_string)
    except:
        return None

def is_recent_event(pub_date_str, hours_threshold=24):
    """Check if event is within the last N hours"""
    event_time = parse_rss_date(pub_date_str)
    if not event_time:
        return False
    
    # Make event_time timezone-naive for comparison
    if event_time.tzinfo:
        event_time = event_time.replace(tzinfo=None)
    
    now = datetime.now()
    time_diff = now - event_time
    return time_diff <= timedelta(hours=hours_threshold)

# Simple in-memory cache
# Format: { "city": { "timestamp": float, "data": dict } }
_EVENT_CACHE = {} 
_CACHE_TTL = 300  # 5 minutes

def get_city_events(city="Mumbai", context=None):
    """
    Scrapes multiple RSS sources for real-time traffic/event updates.
    Returns ALL relevant events (not just one).
    Optimized with Caching and Parallel Execution.
    """
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Check Cache
    now = time.time()
    if city in _EVENT_CACHE:
        cached = _EVENT_CACHE[city]
        if now - cached["timestamp"] < _CACHE_TTL:
            print(f"[CACHE HIT] Returning cached events for {city}")
            return cached["data"]
            
    print(f"Scanning for events in {city} from multiple sources (Parallel)...")
    
    all_events = []
    
    # 1. Multi-Source RSS Scraping
    try:
        # Define TRAFFIC-FOCUSED query sources (optimized for road/traffic relevance)
        query_categories = [
            # Critical Traffic Incidents
            (f"{city} traffic jam OR accident OR crash OR collision", "Traffic"),
            (f"{city} road block OR road closed OR highway closed", "Traffic"),
            
            # Infrastructure Work
            (f"{city} road repair OR construction OR metro work OR flyover", "Infrastructure"),
            (f"{city} diversion OR route change OR detour", "Infrastructure"),
            
            # Weather Impact on Roads
            (f"{city} waterlogging OR flooding affecting traffic OR road flooded", "Weather"),
            
            # Events Affecting Traffic
            (f"{city} match traffic OR stadium congestion OR event crowd", "Sports"),
            (f"{city} protest blocking road OR rally traffic OR demonstration", "Political"),
            
            # General Traffic Conditions
            (f"{city} heavy traffic OR congestion OR gridlock today", "Traffic")
        ]
        
        def fetch_rss(query_tuple):
            query, category = query_tuple
            url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            events_found = []
            
            try:
                response = requests.get(url, timeout=2) # Reduced timeout
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    
                    # Fetch top 2 items per query
                    for item in root.findall('./channel/item')[:2]:
                        title = item.find('title').text
                        link = item.find('link').text
                        pubDate = item.find('pubDate').text
                        
                        # Enhanced Keyword Analysis for Impact
                        impact = "Low"
                        keywords_high = [
                            "accident", "crash", "collision", "fatal", 
                            "protest", "demonstration", "strike",
                            "closed", "closure", "blocked", "gridlock",
                            "severe", "storm", "flood", "landslide",
                            "emergency", "evacuation", "match", "final"
                        ]
                        keywords_med = [
                            "delay", "slow", "congestion", "jam",
                            "maintenance", "repair", "construction",
                            "diversion", "detour", "redirect",
                            "crowd", "gathering", "procession", "concert",
                            "rally", "visit"
                        ]
                        
                        # Keywords to EXCLUDE
                        keywords_exclude = [
                            "market", "stock", "share", "bitcoin",
                            "cricket score card", "movie review", "film review"
                        ]
                        
                        lower_title = title.lower()
                        
                        # Skip irrelevant news
                        if any(k in lower_title for k in keywords_exclude): 
                            continue
                        
                        if any(k in lower_title for k in keywords_high): 
                            impact = "High"
                        elif any(k in lower_title for k in keywords_med): 
                            impact = "Medium"
                        else:
                            # Skip low-impact news
                            continue
                        
                        # Extract location from title
                        location = f"{city}"
                        mumbai_areas = [
                            "Andheri", "Bandra", "Dadar", "Churchgate", "Colaba",
                            "Juhu", "Powai", "Worli", "Marine Drive", "Fort",
                            "Goregaon", "Malad", "Kandivali", "Borivali",
                            "Thane", "Navi Mumbai", "Western Express", "Eastern Express",
                            "Wankhede", "BKC", "Lower Parel", "Kurla"
                        ]
                        for area in mumbai_areas:
                            if area.lower() in lower_title:
                                location = f"{area}, Mumbai"
                                break

                        # Time Travel Logic: Adjust year to 2026 for simulation coherence
                        try:
                            dt = parsedate_to_datetime(pubDate)
                            # Force year to 2026
                            # Note: Feb 7 2025 is Fri. Feb 7 2026 is Sat.
                            # We construct a new valid datetime, ignoring the original weekday in the string
                            if dt.tzinfo:
                                dt = dt.replace(year=2026)
                            else:
                                dt = dt.replace(year=2026)
                            
                            # Store as ISO string which is unambiguous and widely supported
                            final_time_str = dt.isoformat()
                        except:
                            # Fallback if parsing fails (shouldn't happen often)
                            final_time_str = pubDate.replace("2024", "2026").replace("2025", "2026")

                        events_found.append({
                            "Name": title,
                            "Impact": impact,
                            "Location": location,
                            "AffectedAreas": [location],
                            "Category": category,
                            "Source": "Google News",
                            "Link": link,
                            "Time": final_time_str
                        })
            except Exception as e:
                # print(f"   [Warning] Failed to fetch from category '{category}': {e}")
                pass
            return events_found

        # Run fetch_rss in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_query = {executor.submit(fetch_rss, qt): qt for qt in query_categories}
            for future in as_completed(future_to_query):
                try:
                    events = future.result()
                    # Avoid duplicates
                    for e in events:
                        if not any(exist['Name'] == e['Name'] for exist in all_events):
                            all_events.append(e)
                except Exception as exc:
                    pass

        # Sort by impact priority
        all_events.sort(key=lambda x: (0 if x['Impact'] == 'High' else 1 if x['Impact'] == 'Medium' else 2))
        
        result = {"Incident": "None", "Events": []}
        if all_events:
            print(f"   [SUCCESS] Found {len(all_events)} relevant events")
            result = {"Incident": "Multiple", "Events": all_events}
        else:
            print("   [INFO] No significant events detected.")
        
        # Update Cache
        _EVENT_CACHE[city] = {
            "timestamp": now,
            "data": result
        }
        return result

    except Exception as e:
        print(f"   [Error] Scraping failed: {e}")
        # Return fallback or empty structure
        return {"Incident": "None", "Events": []}
    

def get_event_impact_score(city="Mumbai"):
    """
    Returns a float 0.0 to 1.0 representing overall event severity.
    Considers ALL events, not just one.
    """
    try:
        event_data = get_city_events(city)
        events = event_data.get("Events", [])
        
        if not events:
            return 0.0
        
        # Calculate weighted average based on all events
        total_score = 0.0
        for event in events:
            impact = event.get("Impact", "Low")
            if impact == "High": total_score += 0.8
            elif impact == "Medium": total_score += 0.5
            else: total_score += 0.1
        
        # Average and cap at 1.0
        avg_score = min(total_score / len(events), 1.0)
        return round(avg_score, 2)
    except:
        return 0.0

if __name__ == "__main__":
    get_live_weather("Mumbai")
    get_city_events("Mumbai")
