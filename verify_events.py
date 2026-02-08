import requests

r = requests.get('http://localhost:8002/api/predict?city=Mumbai')
data = r.json()

events_data = data['context']['events']
print(f"Incident: {events_data.get('Incident')}")

events_list = events_data.get('Events', [])
print(f"Total Events Found: {len(events_list)}")

if events_list:
    print("\nDisplaying first 5 events:")
    for i, event in enumerate(events_list[:5], 1):
        print(f"{i}. [{event.get('Category')}] {event.get('Name')}")
        print(f"   Impact: {event.get('Impact')} | Location: {event.get('Location')}")
        print()
