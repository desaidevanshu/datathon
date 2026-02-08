import pandas as pd

try:
    df = pd.read_csv('data/raw/mumbai_multi_route_traffic_INTELLIGENCE_READY.csv')
    print("Columns:", df.columns.tolist())
    print("\nInfo:")
    print(df.info())
    print("\nHead:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
