"""
Firebase Admin - Fetch community reports from Firestore
NOTE: Requires firebase_admin_config.json in backend folder
"""

import os
from pathlib import Path

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from datetime import datetime, timedelta
    
    # Initialize Firebase Admin (only once)
    if not firebase_admin._apps:
        # Look for config file
        config_path = Path(__file__).parent.parent / "backend" / "firebase_admin_config.json"
        
        if config_path.exists():
            cred = credentials.Certificate(str(config_path))
            firebase_admin.initialize_app(cred)
            print("[INFO] Firebase Admin initialized successfully")
        else:
            print(f"[WARNING] Firebase Admin config not found at {config_path}")
            print("[INFO] Community reports will not be available")
            firebase_admin = None
    
    db = firestore.client() if firebase_admin._apps else None
    
except Exception as e:
    print(f"[WARNING] Failed to initialize Firebase Admin: {e}")
    firebase_admin = None
    db = None


def fetch_route_reports(source, destination, hours=24, min_score=0, limit=10):
    """
    Fetch community reports relevant to a route
    
    Args:
        source: Source location name
        destination: Destination location name
        hours: Time window in hours (default 24)
        min_score: Minimum netScore to filter (default 0)
        limit: Maximum number of reports (default 10)
    
    Returns:
        List of report dictionaries
    """
    if not db:
        print("[INFO] Firestore not available, returning empty reports")
        return []
    
    try:
        # Calculate time cutoff
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Query Firestore
        reports_ref = db.collection('reports')
        query = reports_ref.where('netScore', '>=', min_score).order_by('netScore', direction=firestore.Query.DESCENDING).limit(limit * 2)  # Get more to filter
        
        # Execute query
        docs = query.stream()
        
        reports = []
        for doc in docs:
            data = doc.to_dict()
            
            # Check timestamp
            timestamp = data.get('timestamp')
            if timestamp and timestamp >= cutoff_time:
                # Filter by location relevance
                location = data.get('location', '').lower()
                source_match = source.lower() in location or location in source.lower()
                dest_match = destination.lower() in location or location in destination.lower()
                
                # Also check title and description
                title = data.get('title', '').lower()
                description = data.get('description', '').lower()
                
                route_relevant = (
                    source_match or dest_match or
                    source.lower() in title or destination.lower() in title or
                    source.lower() in description or destination.lower() in description
                )
                
                if route_relevant or not location:  # Include if relevant or location unknown
                    reports.append({
                        'id': doc.id,
                        'title': data.get('title', ''),
                        'description': data.get('description', ''),
                        'location': data.get('location', 'Mumbai'),
                        'category': data.get('category', 'Other'),
                        'userName': data.get('userName', 'Anonymous'),
                        'netScore': data.get('netScore', 0),
                        'thumbsUp': len(data.get('thumbsUp', [])),
                        'thumbsDown': len(data.get('thumbsDown', [])),
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else None
                    })
        
        # Sort by score and limit
        reports.sort(key=lambda x: x['netScore'], reverse=True)
        return reports[:limit]
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch reports: {e}")
        return []


def get_top_reports_summary(reports):
    """
    Create a summary string of top reports for AI context
    """
    if not reports:
        return "No community reports available for this route."
    
    summary_lines = []
    for i, report in enumerate(reports[:5], 1):
        summary_lines.append(
            f"{i}. [{report['category']}] {report['title']} "
            f"(Score: +{report['netScore']}, {report['location']})"
        )
    
    return "\n".join(summary_lines)
