import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Featherless Configuration
# Featherless Configuration
def load_llm_config_key():
    """Try to load from llm_config.env if not in os.environ"""
    try:
        from pathlib import Path
        # Assuming genai_handler.py is in backend/, and llm_config.env is in root or src parent?
        # root/backend/genai_handler.py -> root/llm_config.env
        # The traffic_anchor was in src/, looking at "parent.parent/llm_config.env"
        
        # Let's search a bit more robustly or just try the specific known path
        # Assuming repo root is parent of backend
        root = Path(__file__).parent.parent
        config_path = root / "llm_config.env"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                for line in f:
                    if 'FEATHERLESS_API_KEY' in line and '=' in line:
                        return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"[config] Error loading llm_config.env: {e}")
    return None

FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY") or load_llm_config_key()
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

if not FEATHERLESS_API_KEY:
    print("[WARNING] FEATHERLESS_API_KEY not found in environment or llm_config.env. Using dummy key.")
    FEATHERLESS_API_KEY = "dummy_key_for_no_crash"

client = openai.OpenAI(
    api_key=FEATHERLESS_API_KEY,
    base_url=FEATHERLESS_BASE_URL
)

SYSTEM_PROMPT = """
You are the GenAI layer of an Advanced Traffic Intelligence System.
Your goal is to convert structured traffic prediction data into intelligent, user-friendly explanations.

CRITICAL CONSTRAINTS:
1. DO NOT perform routing logic or override ML predictions.
2. ONLY use provided structured values. No hallucinations.
3. Tone: Professional, Clear, Concise, Intelligent.
4. Output Format: Conversational plain text. Max 3 sentences.
5. Tone: Helpful, Reassuring, like a smart co-pilot.

MODES:
- If congestion is low: "Traffic looks great! You should have a smooth ride."
- If congestion is high: "Heads up, there's a bit of a jam near [Location]. You might want to try the alternative route to save time."
- If checking future: "Leaving in 2 hours might save you about 15 minutes as traffic clears up."

Focus on being "understood" easily by a driver. Avoid complex jargon.
"""

def generate_traffic_insight(structured_data: dict, user_preference: str = "Fastest route") -> str:
    """
    Generates a natural language explanation for the traffic prediction.
    
    Args:
        structured_data: Dict containing predictions (times, congestion, uncertainty, etc.)
        user_preference: String indicating user priority (e.g., "Fastest", "Safe")
        
    Returns:
        String explanation.
    """
    
    # Construct User Prompt from Data
    user_prompt = f"""
    CONTEXT DATA:
    User Preference: {user_preference}
    
    Selected Route: {structured_data.get('selected_route_name', 'Current')}
    - ETA: {structured_data.get('selected_eta', 'N/A')} min
    - Congestion: {structured_data.get('selected_congestion', 'N/A')}
    - Uncertainty: {structured_data.get('congestion_uncertainty', 'Low')}
    
    Recommended Route: {structured_data.get('recommended_route_name', 'Alternative')}
    - ETA: {structured_data.get('recommended_eta', 'N/A')} min
    - Congestion: {structured_data.get('recommended_congestion', 'N/A')}
    - Savings: {structured_data.get('time_savings', '0')} min
    
    Future Forecast (Next 2 hours):
    - +1 hr ETA: {structured_data.get('future_eta_1h', 'N/A')}
    - +2 hr ETA: {structured_data.get('future_eta_2h', 'N/A')}
    
    Events/Factors: {structured_data.get('top_contributing_factors', 'None')}
    
    Task: Provide a concise recommendation and explanation based on this data.
    """
    
    try:
        if "dummy" in FEATHERLESS_API_KEY:
            print("[GENAI DEBUG] Using Dummy Key - Returning Fallback Response")
            raise Exception("Using Dummy Key")

        print(f"[GENAI DEBUG] Sending request to Featherless API... (Key: {FEATHERLESS_API_KEY[:4]}***)")
        
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=250,
            extra_body={
                "transforms": ["middle-out"]
            }
        )
        content = response.choices[0].message.content.strip()
        print(f"[GENAI DEBUG] Featherless API Success! Response length: {len(content)}")
        return content
        
    except Exception as e:
        print(f"[GENAI ERROR] {e}")
        return f"Based on current analysis, the recommended route offers a savings of {structured_data.get('time_savings', 0)} minutes despite moderate congestion. Traffic is expected to strictly follow the predicted trend. (Source: Fallback)"
