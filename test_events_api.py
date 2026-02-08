import requests
import json

r = requests.get('http://localhost:8002/api/predict?city=Mumbai')
data = r.json()

events = data['context']['events']
print(f"Incident Type: {events.get('Incident')}")
print(f"Events Count: {len(events.get('Events', []))}")

if events.get('Events'):
    print(f"\nFirst 3 events:")
    for i, event in enumerate(events['Events'][:3]):
        print(f"{i+1}. {event['Name']} ({event['Impact']}) - {event['Category']}")
else:
    print("No events found")
