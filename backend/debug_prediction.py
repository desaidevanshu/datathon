
import sys
import os
sys.path.append(os.getcwd())
from src.predict import get_prediction_data

try:
    print("Running prediction...")
    data = get_prediction_data(city="Mumbai, India", source="Andheri", dest="Gateway")
    print("Success!")
    print(data)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
