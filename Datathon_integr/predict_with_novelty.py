
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from predict import predict_live

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Traffic Intelligence Engine (Legacy Wrapper)")
    parser.add_argument("--city", type=str, default="Mumbai", help="City to predict for")
    parser.add_argument("--source", type=str, help="Start location")
    parser.add_argument("--dest", type=str, help="End location")
    
    args = parser.parse_args()
    
    print("[INFO] Redirecting to main prediction engine...")
    predict_live(city=args.city, source=args.source, dest=args.dest)
