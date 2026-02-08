import requests
import json

url = "http://localhost:8005/api/analyze_routes"
payload = {
    "start": {"lat": 19.0760, "lon": 72.8777},
    "destination": {"lat": 19.1136, "lon": 72.8697},
    "source_name": "Mumbai",
    "dest_name": "Andheri"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Request Failed: {e}")
