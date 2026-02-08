"""
Community Intelligence System
Anonymous traffic reporting with misinformation moderation.
"""
import json
import os
from datetime import datetime, timedelta
import hashlib

REPORTS_FILE = "community_reports.json"

def _load_reports():
    """Load reports from JSON file."""
    if not os.path.exists(REPORTS_FILE):
        return {"reports": []}
    
    try:
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"reports": []}

def _save_reports(data):
    """Save reports to JSON file."""
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _generate_reporter_id():
    """Generate anonymous reporter ID."""
    import random
    return f"anon_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"

def submit_report(location, report_text, severity="Moderate"):
    """
    Submit an anonymous traffic report.
    
    Args:
        location: Route location (e.g., "CSMT-Dadar")
        report_text: User description
        severity: Low, Moderate, or High
    """
    data = _load_reports()
    
    report_id = f"r{len(data['reports']) + 1:04d}"
    
    new_report = {
        "id": report_id,
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "reporter_id": _generate_reporter_id(),
        "report": report_text,
        "severity": severity,
        "verified": False,
        "flags": 0
    }
    
    data["reports"].append(new_report)
    _save_reports(data)
    
    return report_id

def get_reports_for_location(location, hours_back=2):
    """
    Get recent reports for a location.
    
    Args:
        location: Route location
        hours_back: How many hours back to search
        
    Returns:
        list: Reports sorted by most recent
    """
    data = _load_reports()
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    relevant_reports = []
    for report in data["reports"]:
        # Skip if wrong location
        if report["location"] != location:
            continue
        
        # Skip if too old
        report_time = datetime.fromisoformat(report["timestamp"])
        if report_time < cutoff_time:
            continue
        
        # Skip if flagged as misinformation (5+ flags)
        if report["flags"] >= 5:
            continue
        
        # Calculate time ago
        delta = datetime.now() - report_time
        if delta.seconds < 60:
            ago = "just now"
        elif delta.seconds < 3600:
            ago = f"{delta.seconds // 60}min ago"
        else:
            ago = f"{delta.seconds // 3600}h ago"
        
        report_copy = report.copy()
        report_copy["ago"] = ago
        relevant_reports.append(report_copy)
    
    return sorted(relevant_reports, key=lambda x: x["timestamp"], reverse=True)

def flag_report(report_id):
    """
    Flag a report as potentially false.
    Reports with 5+ flags will be hidden.
    
    Args:
        report_id: ID of report to flag
        
    Returns:
        bool: True if flagged successfully
    """
    data = _load_reports()
    
    for report in data["reports"]:
        if report["id"] == report_id:
            report["flags"] += 1
            _save_reports(data)
            return True
    
    return False

def verify_report(report_id):
    """
    Mark a report as verified (admin only - for future use).
    Verified reports cannot be flagged.
    """
    data = _load_reports()
    
    for report in data["reports"]:
        if report["id"] == report_id:
            report["verified"] = True
            _save_reports(data)
            return True
    
    return False

def cleanup_old_reports(days=1):
    """
    Archive reports older than specified days.
    Call this periodically to prevent file bloat.
    """
    data = _load_reports()
    cutoff = datetime.now() - timedelta(days=days)
    
    active_reports = []
    for report in data["reports"]:
        report_time = datetime.fromisoformat(report["timestamp"])
        if report_time >= cutoff:
            active_reports.append(report)
    
    data["reports"] = active_reports
    _save_reports(data)
    
    return len(data["reports"]) - len(active_reports)
