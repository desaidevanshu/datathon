
import sys
import os
# Mock setup similar to main.py
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

try:
    print("Attempting to import src.bottleneck_detector...")
    import src.bottleneck_detector as bd
    print(f"Success: {dir(bd)}")
    
    print("Attempting to import src.predict...")
    import src.predict as p
    print("Success: predict imported")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
