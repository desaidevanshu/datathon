
import requests
import json

try:
    response = requests.get("http://localhost:8005/api/predict?city=Mumbai")
    with open("backend/debug_output.txt", "w") as f:
        f.write(f"Status Code: {response.status_code}\n")
        if response.status_code == 200:
            data = response.json()
            f.write(json.dumps(data, indent=2))
            
            # Check specific fields
            if "smart_analysis" in data:
                f.write("\n[SUCCESS] 'smart_analysis' field found.")
            else:
                f.write("\n[ERROR] 'smart_analysis' field MISSING.")
                
            if "forecast" in data:
                f.write("\n[SUCCESS] 'forecast' field found.")
            else:
                f.write("\n[ERROR] 'forecast' field MISSING.")
        else:
            f.write(f"Error: {response.text}")
except Exception as e:
    with open("backend/debug_output.txt", "w") as f:
        f.write(f"Request failed: {e}")
