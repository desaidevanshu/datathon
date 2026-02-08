import pandas as pd
import numpy as np
import os

# Paths
PROCESSED_DATA_DIR = r'data/processed'
REPORTS_DIR = r'reports'

def recommend_routes():
    print("Loading test data and predictions...")
    try:
        test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'test.csv'))
        
        # Load predictions
        # We'll use Random Forest predictions for demonstration as it's generally robust
        travel_time_preds = pd.read_csv(os.path.join(REPORTS_DIR, 'regression_predictions_actual_travel_time_min.csv'))
        congestion_preds = pd.read_csv(os.path.join(REPORTS_DIR, 'regression_predictions_congestion_index.csv'))
        
        # Check alignment
        if len(test_df) != len(travel_time_preds):
            print("Warning: Length mismatch between test data and predictions.")
            return

        # Add predictions to test_df
        test_df['predicted_travel_time'] = travel_time_preds['Random Forest']
        test_df['predicted_congestion'] = congestion_preds['Random Forest']
        
        # Ensure we have origin, destination, route_id
        if 'origin' not in test_df.columns or 'destination' not in test_df.columns:
            print("Error: origin/destination columns missing in test.csv")
            return
            
        print("Grouping by OD pair and timestamp...")
        # distinct OD pairs
        # We want to find cases where multiple routes exist for same OD at same time
        
        # Create OD column
        test_df['OD'] = test_df['origin'] + " TO " + test_df['destination']
        
        # Filter for OD pairs that have > 1 route options
        # In this dataset, 'route_id' often matches 'OD' name, but let's check.
        # If dataset structure is 1 route per OD, then "Alternate Route" logic implies we recommend the best *time* to leave or just show status?
        # User said: "For each origin-destination pair... Compare predicted travel time... Recommend best route".
        # This implies there are multiple route_ids for a single OD pair.
        
        # Let's count routes per OD
        od_route_counts = test_df.groupby('OD')['route_id'].nunique()
        multi_route_ods = od_route_counts[od_route_counts > 1].index.tolist()
        
        print(f"Found {len(multi_route_ods)} OD pairs with multiple routes.")
        
        recommendations = []
        
        # Iterate over multi-route ODs
        # Only take a subset of timestamps for demo (e.g., latest 50 timestamps) to avoid huge output
        timestamps = test_df['timestamp'].unique()[-10:] 
        
        for od in multi_route_ods:
            for ts in timestamps:
                group = test_df[(test_df['OD'] == od) & (test_df['timestamp'] == ts)]
                
                if group.empty: continue
                
                # Rank routes
                group = group.sort_values(by='predicted_travel_time')
                
                best_route = group.iloc[0]
                
                rec = {
                    'Timestamp': ts,
                    'Origin': best_route['origin'],
                    'Destination': best_route['destination'],
                    'Best_Route': best_route['route_id'],
                    'Predicted_Time_Min': round(best_route['predicted_travel_time'], 2),
                    'Predicted_Congestion': round(best_route['predicted_congestion'], 2),
                    'Alternative_Routes_Count': len(group) - 1,
                    'Time_Savings_Min': round(group.iloc[-1]['predicted_travel_time'] - best_route['predicted_travel_time'], 2) if len(group) > 1 else 0
                }
                recommendations.append(rec)
                
        if not recommendations:
            print("No multi-route scenarios found in last 10 timestamps. Showing single route status.")
             # Fallback: Just show status for single routes
            for i in range(min(10, len(test_df))):
                row = test_df.iloc[i]
                rec = {
                    'Timestamp': row['timestamp'],
                    'Origin': row['origin'],
                    'Destination': row['destination'],
                    'Best_Route': row['route_id'],
                    'Predicted_Time_Min': round(row['predicted_travel_time'], 2),
                    'Predicted_Congestion': round(row['predicted_congestion'], 2),
                    'Alternative_Routes_Count': 0,
                    'Time_Savings_Min': 0
                }
                recommendations.append(rec)

        rec_df = pd.DataFrame(recommendations)
        print("\nTop Recommendations:")
        print(rec_df.head())
        
        rec_df.to_csv(os.path.join(REPORTS_DIR, 'route_recommendations.csv'), index=False)
        print("Saved recommendations to route_recommendations.csv")
        
    except Exception as e:
        print(f"Error in recommendation: {e}")

if __name__ == "__main__":
    recommend_routes()
