"""
AI Traffic News Anchor
Generates human-readable traffic bulletins using LLM
"""

import os
from pathlib import Path
from langchain_openai import ChatOpenAI

# Load API key from config file
def load_llm_config():
    """Load Featherless API key from llm_config.env"""
    config_path = Path(__file__).parent.parent / "llm_config.env"
    
    if not config_path.exists():
        raise FileNotFoundError(f"LLM config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == 'FEATHERLESS_API_KEY':
                        return value.strip()
    
    raise ValueError("FEATHERLESS_API_KEY not found in llm_config.env")

# Initialize LLM with strict timeout and lower token limit for speed
try:
    api_key = load_llm_config()
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.featherless.ai/v1",
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        temperature=0.7,
        max_tokens=100, # Reduced from 200 for speed
        request_timeout=3 # Strict 3s timeout
    )
except Exception as e:
    print(f"[WARNING] Failed to initialize LLM: {e}")
    llm = None


def generate_traffic_bulletin(prediction_data):
    """
    Generate a human-readable traffic bulletin from prediction data
    
    Args:
        prediction_data: Dictionary with prediction, context, live_data, etc.
    
    Returns:
        str: Traffic bulletin or fallback message
    """
    if llm is None:
        return generate_simple_bulletin(prediction_data)
    
    try:
        # Extract relevant data
        pred = prediction_data.get("prediction", {})
        ctx = prediction_data.get("context", {})
        live_data = prediction_data.get("live_data", {})
        city = prediction_data.get("city", "Mumbai")
        source = prediction_data.get("source", "Unknown")
        dest = prediction_data.get("destination", "Unknown")
        
        congestion_level = pred.get("congestion_level", "Unknown")
        confidence = pred.get("confidence_score", 0)
        weather_condition = ctx.get("weather", {}).get("Condition", "Clear")
        temperature = ctx.get("weather", {}).get("Temperature", 0)
        current_speed = live_data.get("current_speed", 0)
        
        # Get event info
        events_data = ctx.get("events", {})
        events = events_data.get("Events", [])
        event_descriptions = []
        if events:
            for event in events[:3]:  # Top 3 events
                event_descriptions.append(f"{event.get('Category')}: {event.get('Name')}")
        
        events_str = "; ".join(event_descriptions) if event_descriptions else "No major events"
        
        # Build prompt
        prompt = f"""You are a professional traffic news anchor for {city}. Based on the following data, provide a concise, helpful traffic bulletin (2-3 sentences max).

Route: {source} to {dest}
Current Congestion: {congestion_level}
Current Speed: {current_speed:.1f} km/h
Weather: {weather_condition}, {temperature}°C
Active Events: {events_str}

Provide a clear, actionable traffic update. Mention specific reasons for congestion and give advice to commuters."""

        messages = [
            ("system", "You are a professional traffic news anchor. Keep bulletins concise, informative, and helpful."),
            ("human", prompt)
        ]
        
        # Generate bulletin
        response = llm.invoke(messages)
        bulletin = response.content.strip()
        
        return bulletin
        
    except Exception as e:
        print(f"[ERROR] Failed to generate traffic bulletin (Timeout/Error): {e}")
        # Fallback to template based bulletin on error
        return generate_simple_bulletin(prediction_data)


def generate_simple_bulletin(prediction_data):
    """Fallback simple bulletin without LLM"""
    pred = prediction_data.get("prediction", {})
    ctx = prediction_data.get("context", {})
    
    congestion = pred.get("congestion_level", "Unknown")
    weather = ctx.get("weather", {}).get("Condition", "Clear")
    
    events_data = ctx.get("events", {})
    events = events_data.get("Events", [])
    
    if events:
        event_name = events[0].get("Name", "an event")
        return f"Traffic is {congestion.lower()} due to {weather.lower()} weather and {event_name}. Plan accordingly."
    else:
        return f"Traffic is {congestion.lower()} with {weather.lower()} weather conditions."
