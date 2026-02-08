import requests
import json
import time

BASE_URL = "http://localhost:8005"

def test_analyze_routes():
    print("Wait for server startup on 8005...")
    time.sleep(3)
    
    print("Testing /analyze_routes on port 8005...")
    
    payload = {
        "start": {"lat": 19.0596, "lon": 72.8295}, 
        "destination": {"lat": 19.0176, "lon": 72.8484}, 
        "source_name": "Bandra",
        "dest_name": "Dadar"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/analyze_routes", json=payload, params={"user_preference": "Fastest route"})
        
        if response.status_code == 200:
            data = response.json()
            
            # Check Routes
            routes = data.get("routes", [])
            print(f"[CHECK] Routes Count: {len(routes)} (Expected >= 3)")
            if len(routes) >= 3:
                print("[SUCCESS] Found 3 or more routes.")
            else:
                print(f"[FAIL] Only found {len(routes)} routes.")
                
            # Check Insight
            if "ai_insight" in data and len(data["ai_insight"]) > 10:
                print("\n[SUCCESS] GenAI Response Received!")
                print(f"Insight: {data['ai_insight'][:100]}...")
            else:
                print("\n[WARNING] Response received but insight empty.")
                
        else:
            print(f"[ERROR] API failed with {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[CRITICAL] Request failed: {e}")

if __name__ == "__main__":
    test_analyze_routes()
