# Route Intelligence System - Component Map

## Where Everything Is Used:

### Backend (Python)
```
/api/route endpoint called when user clicks "Find Best Route"
  ↓
backend/api/routes.py (Line 297-400)
  ├─ Calls: src/route_analyzer.py
  │   └─ filter_alerts_by_route() - Filters 24hr events near route
  │   └─ calculate_route_impact_score() - Scores route danger
  │
  ├─ Calls: backend/services/reports_fetcher.py  
  │   └─ fetch_route_reports() - Gets Firestore community reports
  │
  ├─ Calls: src/bottleneck_detector.py
  │   └─ detect_bottlenecks() - Predicts future congestion
  │
  └─ Calls: generate_route_briefing()
      └─ Uses LLM (src/traffic_anchor.py) for AI explanation
  
  Returns: route_analysis object to frontend
```

### Frontend (React)
```
FullMap.jsx receives route_analysis in API response
  ↓
Sets state: setRouteAnalysis(data.route_analysis)
  ↓
Renders: <RouteAnalysisPanel /> (if routeAnalysis exists)
  └─ Location: LEFT sidebar overlay on map
  └─ File: frontend/src/components/RouteAnalysisPanel.jsx
  └─ Shows:
      • AI Route Briefing
      • Future Bottlenecks (⚠️ with ETA)
      • Active Alerts (24hrs)
      • Community Reports
      • Route Impact Score
  
Also renders: Bottleneck Markers on map
  └─ Pulsing warning icons at predicted congestion points
```

## Current Issue:

**Route Intelligence Panel is NOT visible in your screenshot.**

This means `routeAnalysis` state is either:
- `null` (no data returned)
- Empty object (all arrays empty)
- Error during fetch

## Quick Debug:

1. **Check browser console** for errors
2. **Check backend terminal** for error messages like:
   ```
   [ERROR] Alert filtering failed: ...
   [ERROR] Reports fetching failed: ...
   [ERROR] Bottleneck detection failed: ...
   ```

3. **Expected behavior**:
   - Panel appears on LEFT side
   - Overlays the map
   - Shows analysis cards

## Most Likely Cause:

**Firebase Admin SDK** not configured → Community reports fail → Panel doesn't show

**Solution**: The panel should show even without community reports. Let me update it to always display if there's any data OR if route is calculated.
