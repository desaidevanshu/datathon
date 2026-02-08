import sys
sys.path.append('.')

from src.smart_recommendations import get_route_viability, suggest_smart_break, optimize_departure_time

# Simulate bottleneck forecast data
print("Testing Smart Recommendations...")
print("="*60)

# Scenario 1: Congestion building up
print("\nScenario 1: Congestion Building Up")
print("-"*60)
current_level = 0  # Low now
future_preds = [
    {'time_ahead': 0.5, 'hour': 18, 'level': 1, 'confidence': 0.85},
    {'time_ahead': 1.0, 'hour': 19, 'level': 2, 'confidence': 0.90},
    {'time_ahead': 2.0, 'hour': 20, 'level': 1, 'confidence': 0.75},
]

route_alert = get_route_viability(current_level, future_preds)
break_rec = suggest_smart_break(future_preds)
optimal = optimize_departure_time(current_level, future_preds, 17)

print(f"Route Alert: {route_alert or 'None'}")
print(f"Break Rec: {break_rec or 'None'}")
print(f"Optimal: {optimal}")

# Scenario 2: All clear
print("\n\nScenario 2: Route Clear")
print("-"*60)
current_level = 0
future_preds = [
    {'time_ahead': 0.5, 'hour': 14, 'level': 0, 'confidence': 0.95},
    {'time_ahead': 1.0, 'hour': 15, 'level': 0, 'confidence': 0.93},
    {'time_ahead': 2.0, 'hour': 16, 'level': 0, 'confidence': 0.88},
]

route_alert = get_route_viability(current_level, future_preds)
break_rec = suggest_smart_break(future_preds)
optimal = optimize_departure_time(current_level, future_preds, 13)

print(f"Route Alert: {route_alert or 'None'}")
print(f"Break Rec: {break_rec or 'None'}")
print(f"Optimal: {optimal}")

# Scenario 3: Spike then ease
print("\n\nScenario 3: Congestion Spike Then Ease")
print("-"*60)
current_level = 2  # High now
future_preds = [
    {'time_ahead': 0.5, 'hour': 18, 'level': 2, 'confidence': 0.88},
    {'time_ahead': 1.0, 'hour': 19, 'level': 1, 'confidence': 0.82},
    {'time_ahead': 2.0, 'hour': 20, 'level': 0, 'confidence': 0.90},
]

route_alert = get_route_viability(current_level, future_preds)
break_rec = suggest_smart_break(future_preds)
optimal = optimize_departure_time(current_level, future_preds, 17)

print(f"Route Alert: {route_alert or 'None'}")
print(f"Break Rec: {break_rec or 'None'}")
print(f"Optimal: {optimal}")

print("\n" + "="*60)
print("✓ Smart Recommendations Test Complete")
